from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.dialects.mysql import LONGBLOB

from app import db


class TimestampHelper:
    def get_datetime_obj(self):
        return datetime.fromtimestamp(self.timestamp)

    def get_user_datetime(self):
        return self.get_datetime_obj().strftime("%d/%m/%y %H:%M:%S")


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    email = db.Column(db.String(256))
    username = db.Column(db.String(256))
    password_hash = db.Column(db.String(256))
    points = db.Column(db.String(256))
    short_info = db.Column(db.String(256))
    totp_secret = db.Column(db.String(256))
    verified_status = db.Column(db.String(256))
    posts = db.relationship("Post", backref="author", cascade="all, delete-orphan")
    login_attempts = db.relationship("LoginAttempt", backref="user")
    group = db.Column(db.Integer, db.ForeignKey("group.id"))
    authorisations = db.Column(db.String(64))
    profile_pic = db.Column(LONGBLOB)
    answer1 = db.Column(LONGBLOB)
    answer2 = db.Column(LONGBLOB)
    answer3 = db.Column(LONGBLOB)


class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(256))
    likes = db.Column(db.Integer)
    timestamp = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    images = db.relationship("PostImage", backref="post", cascade="all, delete-orphan")


class PostImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    data = db.Column(LONGBLOB)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256))


class Log(db.Model, TimestampHelper):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(256))
    title = db.Column(db.String(256))
    description = db.Column(db.TEXT)
    system_data = db.Column(db.TEXT)
    timestamp = db.Column(db.Integer)
