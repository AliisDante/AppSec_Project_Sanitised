from datetime import datetime

import magic
from sqlalchemy import select, update
from flask import render_template, redirect, url_for, request, make_response, flash
from flask_login import current_user, login_required

from app import app, db, get_current_timestamp
from app.captcha import verify_captcha
from app.encryption import AES
from app.database.models import Post, PostImage
from app.routes.helpers import secure_with_totp
from app.scanner.filescanner import is_file_dangerous


@app.template_global()
def get_post_datetime_formatted(timestamp):
    datetime_obj = datetime.fromtimestamp(timestamp)
    format_str = "%d %B at %I:%M %p"
    return datetime_obj.strftime(format_str)


@app.route("/posts", methods=["GET", "POST"])
@secure_with_totp(["GET", "POST"], "/posts", True)
def posts():
    all_posts = db.session.execute(select(Post).order_by(Post.timestamp.desc())).scalars().all()
    return render_template("posts/posts.html", posts=all_posts)


@app.route("/posts/submit", methods=["POST"])
@login_required
@secure_with_totp(["POST"], "/posts")
def confirm_post():
    if not verify_captcha():
        flash("Invalid Captcha", "error")
        return redirect(url_for("posts"))
    post_content = request.form.get("post_content")
    post_images = request.files.getlist("images")
    new_post = Post(content=post_content,
                    likes=0,
                    timestamp=get_current_timestamp(),
                    author_id=current_user.id)
    db.session.add(new_post)
    db.session.flush()
    for i in post_images:
        image_data = i.read()
        if image_data == b"":
            continue
        detected_mimetype = magic.from_buffer(image_data, mime=True)
        if detected_mimetype not in app.config["SAFE_MIMETYPES"]:
            flash("Unsafe file", "error")
            db.session.rollback()
            return redirect(url_for("posts"))
        elif is_file_dangerous(image_data, detected_mimetype):
            flash("Unsafe file", "error")
            db.session.rollback()
            return redirect(url_for("posts"))
        encrypted_image_data = AES.encrypt(image_data)
        new_post_image = PostImage(post_id=new_post.id, data=encrypted_image_data)
        db.session.add(new_post_image)
    db.session.commit()
    return redirect(url_for("posts"))


@app.route("/posts/image/<int:image_id>")
def post_image(image_id):
    statement = select(PostImage).where(PostImage.id == image_id)
    result = db.session.execute(statement).scalar_one_or_none()
    decrypted_image_data = AES.decrypt(result.data)
    given_mimetype = "image/jpeg"
    detected_mimetype = magic.from_buffer(decrypted_image_data, mime=True)
    if detected_mimetype in app.config["SAFE_MIMETYPES"]:
        given_mimetype = detected_mimetype
    response = make_response(decrypted_image_data)
    response.headers["Content-Type"] = given_mimetype
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/posts/<int:post_id>/like", methods=["POST"])
@login_required
def like_post(post_id):
    post = db.session.execute(select(Post).where(Post.id == post_id)).first()[0]
    post.likes += 1
    db.session.commit()
    return ""


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = db.session.execute(select(Post).where(Post.id == post_id)).first()[0]
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted", "success")
    return redirect(url_for("posts"))
