import requests

from app import app
from flask import request


def verify_captcha():
    captcha_response = request.form.get('h-captcha-response')
    data = {"secret": app.config["CAPTCHA_SECRET"],
            "response": captcha_response}
    r = requests.post("https://hcaptcha.com/siteverify", data=data)
    if app.debug:
        return True
    elif r.status_code == 200:
        return r.json()["success"]
    else:
        return False
