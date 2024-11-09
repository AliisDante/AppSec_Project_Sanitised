from app import db
from app.database.models import User, LoginAttempt


def get_user_by_email(email):
    query = db.select(User).filter_by(email=email)
    result = db.session.execute(query).scalar_one_or_none()
    return result


def get_user_by_username(username):
    query = db.select(User).filter_by(username=username)
    result = db.session.execute(query).scalar_one_or_none()
    return result


def get_user_by_id(id):
    user = db.session.get(User, id)
    return user


def add_login_attempt(user, timestamp, commit=True):
    new_login_attempt = LoginAttempt(timestamp=timestamp, user_id=user.id)
    if commit:
        db.session.add(new_login_attempt)
        db.session.commit()

    return new_login_attempt
