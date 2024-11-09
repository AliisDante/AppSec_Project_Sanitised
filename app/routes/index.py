from flask import render_template

from app import app
from app.routes.helpers import log_access_attempts


@app.route("/")
@log_access_attempts
def index():
    return render_template("home.html")
