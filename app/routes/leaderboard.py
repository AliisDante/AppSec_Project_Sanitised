from flask import render_template, request, url_for, redirect, flash
from app import app, db
from flask_login import current_user, login_required
from app.database.models import *
import math

@app.route('/leaderboard')
@login_required
def get_leaderboard():
    users = User.query.all()
    for i, user in enumerate(users):
        user.points = i + 1
    sorted_users = sorted(users, key=lambda user: user.points, reverse=True)

    # Pagination variables
    per_page = 10
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = sorted_users[start:end]

    total_pages = math.ceil(len(sorted_users) / per_page)

    card_image = '/static/img/card_image.jpg'
    return render_template('leaderboard/leaderboard.html', card_image=card_image, users=paginated_users, page=page, total_pages=total_pages)


