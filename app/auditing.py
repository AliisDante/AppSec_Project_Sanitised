from flask import request
from flask_login import current_user

from app import get_current_timestamp, db
from app.database.models import Log


def entity_format(string, *args, **kwargs):
    if current_user.is_authenticated:
        entity = current_user.username
    else:
        entity = request.remote_addr

    return string.format(*args, entity=entity, **kwargs)


def create_event(type, title="", description=""):
    new_log = Log(type=type,
                  title=title,
                  description=description,
                  system_data=None,
                  timestamp=get_current_timestamp())
    db.session.add(new_log)
    db.session.commit()
