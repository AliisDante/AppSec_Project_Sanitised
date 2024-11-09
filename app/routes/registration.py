from flask import render_template, url_for, session, request, redirect, flash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import decode_token
from flask_login import login_user, login_required, current_user
from flask_mail import Message, Mail

import requests
import pyotp
import qrcode
import qrcode.image.svg

from app import app, db
from app.database.models import *

from werkzeug.security import generate_password_hash
mail = Mail(app)


@app.route("/register")
def get_register():
    return render_template("registration/register.html")

# defer doing security questions and recovery
""" @app.route("/register", methods=['POST'])
def post_register():
    # check if email is unique
    check = True
    if check:
        return render_template("registration/register_security_questions.html")
    else:
        return redirect(url_for('get_register')) """


@app.route("/register/verify", methods=['POST'])
def post_register_verify():
    # captcha verification
    data =  {
                "secret": app.config["CAPTCHA_SECRET"],
                "response": request.form.get('h-captcha-response')
            }

    r = requests.post("https://hcaptcha.com/siteverify", data=data)
    captcha_result = r.json()["success"] if r.status_code == 200 else False
    print(captcha_result)

    if not app.debug and captcha_result == False:
        flash("Captcha was not solved, try again", "error")
        return redirect(url_for('get_register'))


    # send email, if all required details are passed and email/username unique
    email_check = db.session.execute(db.select(User).filter_by(email=request.form.get('email'))).scalar()
    username_check = db.session.execute(db.select(User).filter_by(username=request.form.get('username'))).scalar()
    if email_check == None and username_check == None:
        if (request.form.get('email') != "" and request.form.get('username') != "" and request.form.get('password') != "") and (request.form.get('password') == request.form.get('confirm_password')):
            # add user to database
            user = User()
            user.username = request.form.get('username')
            user.email = request.form.get('email')
            user.password_hash = generate_password_hash(request.form.get('password'))
            user.totp_secret = pyotp.random_base32()
            user.verified_status = "partially"
            db.session.add(user)
            db.session.commit()

            # partial authenticate, require totp (so need verify email)
            login_user(user)

            # generate jwt link and send email
            access_token = create_access_token(identity=request.form.get('email'))
            print(access_token)

            subject = 'Carbon Cruncher Verify Email'
            message = f'''
                Click on this link to verify your email ownership.
                http://127.0.0.1/register/verified/{access_token}
            '''
            msg = Message(recipients=[request.form.get('email')], sender='carboncruncherdev@gmail.com', body=message, subject= subject)
            mail.send(msg)

            return render_template("registration/register_verify_email.html")
        else:
            # show error of invalid input
            flash("Ensure all fields are filled and passwords matches", "error")
            return redirect(url_for('get_register'))
    elif email_check == None:
        # username taken error
        flash("Username taken, try something else", "error")
        return redirect(url_for('get_register'))
    else:
        # email taken error
        flash("Email taken, try something else", "error")
        return redirect(url_for('get_register'))


@app.route("/register/verified/<secret>")
# @login_required
def get_register_verified(secret):
    # verify jwt, fully authenticated then show totp qr code
    print(secret)
    try:
        email_used = decode_token(secret)["sub"]
        print(email_used)

        # find username of email to fully authenticate
        if current_user.email == email_used:
            """ print(user) """
            current_user.verified_status = "fully"
            db.session.commit()
            """ db.session.commit()
            print(user.username)
 """
            # fetch totp token to render
            url = pyotp.totp.TOTP(current_user.totp_secret).provisioning_uri(name=current_user.email, issuer_name='Carbon Cruncher')
            print(url)

            # generate QR code for TOTP
            # qr = qrcode.QRCode(image_factory=qrcode.image.svg.SvgPathImage)
            # qr.add_data('Some data')
            # qr.make(fit=True)

            # img = qr.make_image(attrib={'class': 'some-css-class'})
            # img.to_string(encoding='unicode')
            # print(img.tostring())
            return render_template("registration/register_totp_setup.html", qr_img=url)
    except Exception as e:
        print(e)
        # error, wrong
        flash("Invalid token, register again", "error")
        return redirect(url_for('get_register'))
        # expried token (then send new one)
