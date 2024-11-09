from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import select

from app import app, db
from app.routes.helpers import privilege_level
from app.database.models import Log


DEFAULT_PAGINATION_MAX_ROWS = app.config["DEFAULT_PAGINATION_MAX_ROWS"]


@app.route("/logs", defaults={"page_number": 1, "type": "all"})
@app.route("/logs/<type>", defaults={"page_number": 1})
@app.route("/logs/<type>/page/<int:page_number>")
@login_required
@privilege_level(["admin"])
def get_logs(type, page_number):
    if page_number < 1:
        flash("Invalid page number", "error")
        return redirect(url_for("get_users"))
    if page_number <= 1:
        previous_page_number = None
    else:
        previous_page_number = page_number - 1
    next_page_number = page_number + 1

    offset = (page_number - 1) * DEFAULT_PAGINATION_MAX_ROWS
    query = select(Log).limit(DEFAULT_PAGINATION_MAX_ROWS).offset(offset).order_by(Log.timestamp.desc())
    if type != "all":
        query = query.where(Log.type == type)
    logs = db.session.execute(query).scalars().all()
    return render_template("auditing/logs.html", logs=logs, previous_page_number=previous_page_number, next_page_number=next_page_number, current_log_type=type)
