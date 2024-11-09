import os
import safety

print(os.popen("safety check").read())

import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from app.config import Config

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
login_manager = LoginManager(app)
csrf_protect = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, default_limits=app.config["DEFAULT_RATE_LIMITS"], storage_uri="memory://")
mail = Mail(app)


def get_current_timestamp():
    return int(time.time())


from app.database import models
from app.routes import index, calculator, login, recovery, registration, account, leaderboard, posts, challenge, auditing, users


login_manager.login_view = "get_login"


@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    return db.session.get(models.User, user_id)


@app.after_request
def add_secure_headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self' https://fonts.googleapis.com https://js.hcaptcha.com https://fonts.gstatic.com https://newassets.hcaptcha.com https://api.qrserver.com/v1/create-qr-code/ https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.3.2/chart.umd.js 'unsafe-inline' data: blob:;"
    return response

from flask_socketio import SocketIO
async_mode = None
socket_ = SocketIO(app, async_mode=async_mode)