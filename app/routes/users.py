from sqlalchemy import select
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_required
from app import app, db
from app.routes.helpers import privilege_level
from app.database import users
from app.database.models import User


DEFAULT_PAGINATION_MAX_ROWS = app.config["DEFAULT_PAGINATION_MAX_ROWS"]


@app.route("/users", defaults={"page_number": 1})
@app.route("/users/page/<int:page_number>")
@login_required
@privilege_level(["admin"])
def get_users(page_number):
    if page_number < 1:
        flash("Invalid page number", "error")
        return redirect(url_for("get_users"))
    if page_number <= 1:
        previous_page_number = None
    else:
        previous_page_number = page_number - 1
    next_page_number = page_number + 1

    offset = (page_number - 1) * DEFAULT_PAGINATION_MAX_ROWS
    users = db.session.execute(select(User).limit(DEFAULT_PAGINATION_MAX_ROWS).offset(offset)).scalars().all()
    return render_template("users/users.html", users=users, previous_page_number=previous_page_number, next_page_number=next_page_number)


@app.route("/users/<int:user_id>")
@login_required
@privilege_level(["admin"])
def update_user(user_id):
    user = users.get_user_by_id(user_id)
    if not user:
        flash("User does not exist", "error")
        return redirect(url_for("get_users"))
    return render_template("users/update_user.html", user=user)


@app.route("/users/<int:user_id>", methods=["POST"])
@login_required
@privilege_level(["admin"])
def confirm_update_user(user_id):
    user = users.get_user_by_id(user_id)
    new_username = request.form.get("new_username")
    new_fname = request.form.get("new_fname")
    new_lname = request.form.get("new_lname")
    new_role = request.form.get("user_role")
    if "" in [new_username, new_fname, new_lname]:
        flash("Required fields must be provided", "error")
        return redirect(url_for("update_user", user_id=user_id))
    existing_username = users.get_user_by_username(new_username)
    if existing_username and existing_username != user:
        flash("Username is in use already", "error")
        return redirect(url_for("update_user", user_id=user_id))
    user.username = new_username
    user.fname = new_fname
    user.lname = new_lname
    user.authorisations = new_role
    db.session.commit()
    flash("Update successful!", "success")
    return redirect(url_for("update_user", user_id=user_id))


@app.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@privilege_level(["admin"])
def delete_user(user_id):
    user = users.get_user_by_id(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("get_users"))
