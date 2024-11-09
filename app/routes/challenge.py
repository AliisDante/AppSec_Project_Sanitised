from flask import render_template
from app import app, db
from app.database import models
from flask_login import login_required

@app.route('/challenges')
@login_required
def get_challenges():
    card_image = 'static/img/card_image.jpg'
    return render_template("/challenges/challenge.html", card_image=card_image)
