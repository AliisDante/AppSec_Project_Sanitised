import pyotp

import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow

import flask
from flask import render_template, session, url_for, request, redirect, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from werkzeug.exceptions import Forbidden

from app import app, db, get_current_timestamp
from app import captcha
from app import short_info
from app import auditing
from app.database import users

from app.database.models import *

# oauth implementation
flow = google_auth_oauthlib.flow.Flow.from_client_config(
    client_config={"web":{"client_id":"CENSORED","project_id":"CENSORED","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"CENSORED","redirect_uris":["CENSORED"]}},
    scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile','openid'])

flow.redirect_uri = "http://127.0.0.1:5000/oauth2callback"

authorization_url, state = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true')

import pyotp
import qrcode
import qrcode.image.svg

@app.route("/oauth2callback")
def oauth2callback():
    authorization_response = flask.request.url

    flow.fetch_token(code=request.args.get("code"))

    credentials = flow.credentials

    # then store creds in session
    # edit: not required

    # fetch creds for account
    session = flow.authorized_session()
    profile_info = session.get(
    'https://www.googleapis.com/userinfo/v2/me').json()


    # redirect to login - endpoint is /register/verify
    # args are email, username, password

    # send email, if all required details are passed and email/username unique
    email_check = db.session.execute(db.select(User).filter_by(email=profile_info["email"])).scalar()
    username_check = db.session.execute(db.select(User).filter_by(username=profile_info["email"])).scalar()
    if email_check == None and username_check == None:
        user = User()
        user.username = profile_info["email"]
        user.email = profile_info["email"]
        user.password_hash = generate_password_hash(pyotp.random_base32())
        user.totp_secret = pyotp.random_base32()
        user.verified_status = "fully"
        db.session.add(user)
        db.session.commit()

        url = pyotp.totp.TOTP(current_user.totp_secret).provisioning_uri(name=current_user.email, issuer_name='Carbon Cruncher')
        return render_template("registration/register_totp_setup.html", qr_img=url)
    else:
        user = users.get_user_by_email(profile_info["email"])
        login_user(user, False)
        return redirect(url_for("index"))

    # else, directly login
    



def prune_user_login_attempts(user):
    attempt_expiry_duration = app.config["USER_TIMEOUT_DURATION_IN_SECONDS"]
    for i in user.login_attempts:
        if i.timestamp + attempt_expiry_duration < get_current_timestamp():
            db.session.delete(i)

    db.session.commit()


def is_user_timed_out(user):
    timeout_duration = app.config["USER_TIMEOUT_DURATION_IN_SECONDS"]
    maximum_login_attempts = app.config["USER_MAXIMUM_ATTEMPTS"]
    if len(user.login_attempts) >= maximum_login_attempts and latest_login_attempt(user).timestamp + timeout_duration > get_current_timestamp():
        return True
    else:
        return False


def latest_login_attempt(user):
    class NoLoginAttempt:
        def __init__(self):
            self.timestamp = 0

    latest_timestamped_login_attempt = NoLoginAttempt()
    for i in user.login_attempts:
        if i.timestamp > latest_timestamped_login_attempt.timestamp:
            latest_timestamped_login_attempt = i

    return latest_timestamped_login_attempt


def post_login_tasks():
    short_info.update_user_short_info(current_user)
    auditing.create_event("login", "Successful login")


def post_logout_tasks():
    pass


@app.route("/login")
def get_login():
    return render_template("login/login.html", auth_url=authorization_url)


@app.route("/login", methods=['POST'])
def login():
    if not app.debug and not captcha.verify_captcha():
        flash("Invalid Captcha")
        return redirect(url_for("index"))

    username_email = request.form.get("username_email")
    password = request.form.get("password")
    remember_me = request.form.get("remember_me")

    user = users.get_user_by_email(username_email) or users.get_user_by_username(username_email)
    if user:
        prune_user_login_attempts(user)

    if user and is_user_timed_out(user):
        flash("User is locked out. Please wait...", "error")
        auditing.create_event(user, "login", f"Login attempt from {request.remote_addr}")
        users.add_login_attempt(user, get_current_timestamp(), True)
        return redirect(url_for("get_login"))
    elif user and check_password_hash(user.password_hash, password):
        session["login_user_id"] = user.id
        session["remember_me"] = remember_me
        auditing.create_event("login", f"Login attempt from {request.remote_addr}")
        users.add_login_attempt(user, get_current_timestamp(), True)
        return render_template("login/login_totp_code.html")
    else:
        flash("Incorrect username or password", "error")
        if user:
            auditing.create_event("login", f"Login attempt from {request.remote_addr}")
            users.add_login_attempt(user, get_current_timestamp(), True)
        return redirect(url_for("get_login"))


@app.route("/login/totp", methods=['POST'])
def post_login_totp():
    login_user_id = session.get("login_user_id")
    remember_me = session.get("remember_me")
    if not login_user_id:
        raise Forbidden()
    user = users.get_user_by_id(login_user_id)

    given_totp_code = request.form.get("totp_code")

    totp = pyotp.TOTP(user.totp_secret)
    if totp.verify(given_totp_code):
        login_user(user, remember_me)
        auditing.create_event("totp", "TOTP successful")
        post_login_tasks()
        return redirect(url_for("index"))
    elif app.debug:
        flash("TOTP override activated")
        login_user(user, remember_me)
        auditing.create_event("totp", "TOTP override activated")
        post_login_tasks()
        return redirect(url_for("index"))
    else:
        auditing.create_event("totp", "TOTP invalid")
        flash("Incorrect TOTP code", "error")
        return redirect(url_for("get_login"))


@app.route("/logout")
def logout():
    auditing.create_event("logout", "Successful logout")
    logout_user()
    post_logout_tasks()
    return redirect(url_for("index"))
