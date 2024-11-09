from flask import render_template, url_for, session, request, redirect, flash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import decode_token
from app import app, db, captcha
from app.database import users
from flask_mail import Message, Mail
from werkzeug.security import generate_password_hash, check_password_hash
import re
from app.encryption.AES import decrypt
mail = Mail(app)


@app.route("/recovery")
def get_email_recovery():
    return render_template("recovery/recovery.html")


@app.route("/recovery", methods=['POST'])
def post_email_recovery():
    if not app.debug and not captcha.verify_captcha():
        flash('Invalid Captcha')
        return redirect(url_for("get_email_recovery"))
    email = request.form.get('email')
    user = users.get_user_by_email(email)
    if email != '':
        if user:
            access_token = create_access_token(identity=email)
            print(access_token)
            subject = 'Carbon Cruncher Forget Password'
            message = f'''
                Click on this link to reset your password.
                http://127.0.0.1:5000/recovery/verified/{access_token}
            '''
            msg = Message(recipients=[email], sender='carboncruncherdev@gmail.com', body=message, subject= subject)
            mail.send(msg)
            return render_template("recovery/recovery_confirm.html")
        else:
            flash('No account found with matching email')
            return redirect(url_for('get_email_recovery'))
    else:
        flash('Email cannot be empty')
        return redirect(url_for('get_email_recovery'))


@app.route("/recovery/verified/<secret>")
def get_recovery_questions(secret):
    # email verified, ask security questions
    try:
        email_used = decode_token(secret)['sub']
        print(email_used)
        return render_template("recovery/recovery_questions.html", secret=secret)
    except Exception as e:
        print(e)
        flash("Invalid token", "error")
        return redirect(url_for('get_email_recovery'))
        # expried token (then send new one)


@app.route("/recovery/verified/<secret>", methods=['POST'])
def post_recovery_questions(secret):
    # check if questions are correct, authenticated then let them reset password
    if not app.debug and not captcha.verify_captcha():
        flash('Invalid Captcha')
        return redirect(url_for("get_recovery_questions", secret=secret))
    email_used = decode_token(secret)['sub']
    print(email_used)
    user = users.get_user_by_email(email_used)
    print(user)
    answer1 = request.form.get('answer1').upper().replace(" ","")
    answer2 = request.form.get('answer2').upper().replace(" ","")
    answer3 = request.form.get('answer3').upper().replace(" ","")
    print(answer1)
    print(user.answer1)
    print(answer2)
    print(user.answer2)
    print(answer3)
    print(user.answer3)
    if answer1 != '' and answer2 != '' and answer3 != '':
        if decrypt(user.answer1).decode('utf-8') == answer1 and decrypt(user.answer2).decode('utf-8') == answer2 and decrypt(user.answer3).decode('utf-8') == answer3:
            return redirect(url_for('get_recovery_reset', secret=secret))
        else:
            flash('Incorrect answers, please try again.')
            return redirect(url_for('get_recovery_questions', secret=secret))
    else:
        flash('Required fields cannot be empty. ')
        return redirect(url_for('get_recovery_questions', secret=secret))


@app.route("/recovery/reset/<secret>", methods=['POST'])
def post_recovery_reset(secret):
    email_used = decode_token(secret)['sub']
    user = users.get_user_by_email(email_used)
    new_password = request.form.get('new_password')
    cfm_password = request.form.get('cfm_password')
    if new_password != "" and cfm_password != "":
        if not check_password_hash(user.password_hash, new_password):
            if new_password == cfm_password:
                # Check if the new password matches the regex pattern
                    if re.search(app.config['PASSWORD_REGEX'], new_password):
                        user.password_hash = generate_password_hash(new_password)
                        db.session.commit()

                    else:
                        flash('Password must be between 4 to 64 characters and contain at least one digit, one lowercase letter, and one uppercase letter.')
                        return redirect(url_for('get_recovery_reset', secret=secret))
            else:
                flash('Passwords must match')
                return redirect(url_for('get_recovery_reset', secret=secret))
        else:
            flash('New password cannot be the same as the old one')
            return redirect(url_for('get_recovery_reset', secret=secret))
    else:
        flash('Required fields cannot be empty')
        return redirect(url_for('get_recovery_reset', secret=secret))

    flash('Successfully updated password.')
    return redirect(url_for('get_account'))

@app.route("/recovery/reset/<secret>", methods=['GET'])
def get_recovery_reset(secret):
    # Render the template for resetting the password (assuming you have a template for it)
    return render_template("recovery/recovery_reset.html", secret=secret)

@app.route("/recovery/id")
def get_id():
    return render_template('recovery/recovery_id.html')

@app.route("/recovery/id", methods=['POST'])
def post_id():
    if not app.debug and not captcha.verify_captcha():
        flash('Invalid Captcha')
        return redirect(url_for("get_id"))
    email = request.form.get('email')
    user = users.get_user_by_email(email)
    if email != '':
        if user:
            username = user.username
            subject = 'Carbon Cruncher Forget ID'
            message = f'''
                Your username with Carbon Cruncher is:
                {username}
            '''
            msg = Message(recipients=[email], sender='carboncruncherdev@gmail.com', body=message, subject= subject)
            mail.send(msg)
            return render_template("recovery/recovery_id_confirm.html")
        else:
            flash('No account found with matching email')
            return redirect(url_for('get_id'))
    else:
        flash('Email cannot be empty')
        return redirect(url_for('get_id'))
