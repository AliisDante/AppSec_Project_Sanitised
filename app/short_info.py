import random

from app import db

TEMPLATES = ["{first_name} has achieved greatness!",
             "{first_name} has been cycling more and more every week"]


def generate_random_short_info(user):
    template = random.choice(TEMPLATES)
    return template.format(first_name=user.first_name)


def update_user_short_info(user):
    new_short_info = generate_random_short_info(user)
    user.short_info = new_short_info
    db.session.commit()
