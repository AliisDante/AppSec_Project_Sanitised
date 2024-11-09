from functools import wraps

from flask import render_template, request, redirect, url_for, flash, session
from flask_login import current_user
import pyotp

from app import app
from app import auditing


TOTP_VERIFIED_COUNT = app.config["TOTP_VERIFIED_COUNT"]


def secure_with_totp(secured_methods=["GET", "POST"],
                     custom_redirect_url=None,
                     allow_when_unauthenticated_with_get=False):
    def wrap_view_function(view_function):
        @wraps(view_function)
        def wrapped_view_function(*args, **kwargs):
            redirect_url = custom_redirect_url or \
                    url_for(view_function.__name__)
            if request.method in secured_methods:
                if request.method == "GET" and \
                        allow_when_unauthenticated_with_get and \
                        not current_user.is_authenticated:
                    return view_function(*args, **kwargs)
                elif request.form.get("totp_code"):
                    given_totp_code = request.form.get("totp_code")
                    totp = pyotp.TOTP(current_user.totp_secret)
                    if totp.verify(given_totp_code):
                        auditing.create_event("totp", "TOTP successful")
                        session["totp_verified_count"] = TOTP_VERIFIED_COUNT
                        return redirect(redirect_url)
                    elif app.debug:
                        flash("TOTP override activated")
                        auditing.create_event("totp", "TOTP override activated")
                        session["totp_verified_count"] = TOTP_VERIFIED_COUNT
                        return redirect(redirect_url)
                    else:
                        auditing.create_event("totp", "TOTP invalid")
                        flash("Incorrect TOTP code", "error")
                        return redirect(redirect_url)
                elif session.get("totp_verified_count"):
                    totp_verified_count = session["totp_verified_count"]
                    session["totp_verified_count"] = totp_verified_count - 1
                    if totp_verified_count < 0:
                        del session["totp_verified_count"]
                    return view_function(*args, **kwargs)
                return render_template("totp/totp.html",
                                       url=url_for(view_function.__name__))
            else:
                return view_function(*args, **kwargs)
        return wrapped_view_function
    return wrap_view_function


def privilege_level(required_privilege_levels):
    def wrapper(view_function):
        @wraps(view_function)
        def wrapped_view_function(*args, **kwargs):
            if current_user.authorisations not in required_privilege_levels:
                flash("Access not granted", "error")
                return redirect(url_for("index"))
            else:
                return view_function(*args, **kwargs)
        return wrapped_view_function
    return wrapper


def log_access_attempts(view_function):
    @wraps(view_function)
    def wrapped_view_function(*args, **kwargs):
        auditing.create_event("access", auditing.entity_format("Logged route {path} accessed by {entity}", path=request.path))
        return view_function(*args, **kwargs)
    return wrapped_view_function
