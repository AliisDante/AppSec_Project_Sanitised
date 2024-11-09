from flask import render_template, request, url_for, redirect, flash
from app import app, db, captcha
from flask_login import current_user, login_required
from app.database.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from app.routes.helpers import secure_with_totp
from app.encryption.AES import encrypt
from app.scanner.filescanner import is_file_dangerous
from flask_jwt_extended import create_access_token, decode_token
from flask_mail import Message, Mail
import base64
import os
import re
import magic

mail = Mail(app)
email = ''

def image_to_base64(image_path):
    app_root = os.path.dirname(os.path.abspath(__file__))
    abs_image_path = os.path.join(app_root, image_path)
    with open(abs_image_path, 'rb') as image_file:
        image_data = image_file.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        return base64_data


@app.route('/setting/profile')
@login_required
def get_profile():
    profile_pic_binary = current_user.profile_pic
    if profile_pic_binary is None:
        profile_pic_base64 = image_to_base64('../static/img/user.png')

    else:
        profile_pic_base64 = base64.b64encode(profile_pic_binary).decode('utf-8')

    return render_template('accounts/profile.html', current_user=current_user,
                           profile_pic_base64=profile_pic_base64)


@app.route('/setting/account')
@login_required
def get_account():
    return render_template('accounts/account.html')


@app.route('/setting/update_password', methods=['GET'])
@login_required
@secure_with_totp(['GET', 'POST'], '/setting/update_password')
def get_update_password():
    return render_template('accounts/update_password.html')


@app.route('/setting/update_password', methods=['POST'])
@login_required
@secure_with_totp(['GET', 'POST'], '/setting/update_password')
def post_update_password():
    if not app.debug and not captcha.verify_captcha():
        flash('Invalid Captcha')
        return redirect(url_for("get_update_password"))

    new_password = request.form.get('new_password')
    cfm_password = request.form.get('cfm_password')
    old_password = request.form.get('old_password')

    if new_password != "" and cfm_password != "" and old_password != "":
        if not check_password_hash(current_user.password_hash, new_password):
            if new_password == cfm_password:
                # Check if the new password matches the regex pattern
                if re.search(app.config['PASSWORD_REGEX'], new_password):
                    current_user.password_hash = generate_password_hash(new_password)
                    db.session.commit()
                else:
                    flash(
                        'Password must be between 4 to 64 characters and contain at least one digit, one lowercase letter, and one uppercase letter.')
                    return redirect(url_for('get_update_password'))
            else:
                flash('Passwords must match')
                return redirect(url_for('get_update_password'))
        else:
            flash('New password cannot be the same as the old one')
            return redirect(url_for('get_update_password'))
    else:
        flash('Required fields cannot be empty')
        return redirect(url_for('get_update_password'))

    return redirect(url_for('get_account'))


@app.route('/setting/update_email/verify', methods=['GET'])
@login_required
@secure_with_totp(['GET', 'POST'], '/setting/update_email/verify')
def get_update_email():
    return render_template('accounts/update_email.html')


@app.route('/setting/update_email/verify', methods=['POST'])
@login_required
@secure_with_totp(['GET', 'POST'], '/setting/update_email/verify')
def post_update_email_verify():
    if not app.debug and not captcha.verify_captcha():
        flash('Invalid Captcha')
        return redirect(url_for("get_update_email"))

    new_email = request.form.get('new_email')
    if not re.match(app.config['EMAIL_REGEX'], new_email):
        flash('Invalid email format')
        return redirect(url_for('get_update_email'))

    email_check = db.session.execute(db.select(User).filter_by(email=request.form.get('email'))).scalar()
    if email_check == None:
        if request.form.get('new_email') != "" and request.form.get('password') != "":
            if check_password_hash(current_user.password_hash, request.form.get('password')):
                access_token = create_access_token(identity=request.form.get('new_email'))
                print(access_token)

                subject = 'Carbon Cruncher Verify Email'
                message = f'''
                                Click on this link to verify your email ownership.
                                http://127.0.0.1:5000/setting/update_email/verified/{access_token}
                            '''
                msg = Message(recipients=[request.form.get('new_email')], sender='carboncruncherdev@gmail.com',
                              body=message, subject=subject)
                mail.send(msg)
                global email
                email = request.form.get('new_email')
                return redirect(url_for('get_confirmation'))
            else:
                flash('Incorrect password')
                return redirect(url_for('get_update_email'))
        else:
            flash('Required fields cannot be empty')
            return redirect(url_for('get_update_email'))
    else:
        flash('Email taken, try something else', 'error')

@app.route('/setting/update_email/verified/<secret>')
@login_required
def get_update_email_verified(secret):
    print(secret)
    try:
        email_used = decode_token(secret)["sub"]
        global email

        if email == email_used:
            current_user.email = email
            db.session.commit()
            flash('Email changed successfully')
            return redirect(url_for('index'))


    except Exception as e:
        print(e)
        flash('Invalid token, try to change email again', 'error')
        return redirect(url_for('get_update_email'))

@app.route('/setting/update_email/confirmation')
@login_required
def get_confirmation():
    return render_template('/accounts/confirmation.html')
@app.route('/setting/update_profile', methods=['GET'])
@login_required
def get_update_profile():
    return render_template('accounts/update_profile.html')


@app.route('/setting/update_profile', methods=['POST'])
@login_required
def post_update_profile():
    if not app.debug and not captcha.verify_captcha():
        flash('Invalid Captcha')
        return redirect(url_for("get_update_profile"))
    pfp = request.files.get('profile_photo')
    if request.form.get('new_username') != "" and request.form.get('new_fname') != "" and request.form.get(
            'new_lname') != "":
        current_user.username = request.form.get('new_username')
        current_user.first_name = request.form.get('new_fname')
        current_user.last_name = request.form.get('new_lname')

        # Check if the profile photo was provided or has an empty filename
        if pfp is None or pfp.filename == '':
            # Set the default photo here
            default_photo_path = '../static/img/user.png'
            app_root = os.path.dirname(os.path.abspath(__file__))
            abs_image_path = os.path.join(app_root, default_photo_path)
            with open(abs_image_path, 'rb') as f:
                default_photo_bytes = f.read()
            current_user.profile_pic = default_photo_bytes
        else:
            pfp_bytes = pfp.read()
            detected_mimetype = magic.Magic(mime=True).from_buffer(pfp_bytes)
            if detected_mimetype not in app.config['SAFE_MIMETYPES']:
                flash('Unsupported file.')
                return redirect(url_for('get_update_profile'))
            if not is_file_dangerous(pfp, detected_mimetype):
                flash('Malicious file detected.')
                return redirect(url_for('get_update_profile'))
            current_user.profile_pic = pfp_bytes

        db.session.commit()
    else:
        flash('Required fields cannot be empty')
        return redirect(url_for('get_profile'))

    return redirect(url_for("get_profile"))


@app.route('/getting_started/get_name', methods=['GET'])
@login_required
def get_name():
    return render_template('/accounts/getting_started.html')


@app.route('/getting_started/post_name', methods=['POST'])
@login_required
def post_name():
    if not app.debug and not captcha.verify_captcha():
        flash('Invalid Captcha')
        return redirect(url_for("get_name"))
    if request.form.get('first_name') == "" or request.form.get('last_name') == '':
        flash('Name fields must not be empty.')
        return redirect(url_for("get_name"))
    else:
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        db.session.commit()
        return redirect(url_for("get_profile_photo"))


@app.route('/getting_started/get_profile_photo', methods=['GET'])
@login_required
def get_profile_photo():
    profile_pic_bin = current_user.profile_pic
    if profile_pic_bin is None:
        profile_pic_base64 = image_to_base64('../static/img/user.png')
    else:
        profile_pic_base64 = base64.b64encode(profile_pic_bin).decode('utf-8')
    return render_template('/accounts/profile_photo.html', profile_pic_base64=profile_pic_base64)


@app.route('/getting_started/get_profile_photo', methods=['POST'])
@login_required
def post_profile_photo():
    profile_photo = request.files['profile_photo']

    if profile_photo is None or profile_photo.filename == '':
        default_photo_path = '../static/img/user.png'
        app_root = os.path.dirname(os.path.abspath(__file__))
        abs_image_path = os.path.join(app_root, default_photo_path)
        with open(abs_image_path, 'rb') as f:
            default_photo_bytes = f.read()
        current_user.profile_pic = default_photo_bytes
        db.session.commit()

    else:
        pfp_bytes = profile_photo.read()
        detected_mimetype = magic.Magic(mime=True).from_buffer(pfp_bytes)
        if detected_mimetype not in app.config['SAFE_MIMETYPES']:
            flash('Unsupported file.')
            return redirect(url_for('get_profile_photo'))
        if not is_file_dangerous(profile_photo, detected_mimetype):
            flash('Malicious file detected.')
            return redirect(url_for('get_profile_photo'))
        current_user.profile_pic = pfp_bytes
        db.session.commit()

    return redirect(url_for('get_profile'))


@app.route('/remove_profile_photo', methods=['POST'])
@login_required
def remove_profile_photo():
    current_user.profile_pic = None
    db.session.commit()
    return redirect(url_for('get_update_profile'))


@app.route('/setting/answer_securityqns', methods=['GET'])
@login_required
@secure_with_totp(['GET', 'POST'], '/setting/answer_securityqns')
def get_security_questions():
    return render_template('/accounts/securityqns.html')


@app.route('/setting/answer_securityqns', methods=['POST'])
@login_required
@secure_with_totp(['GET', 'POST'], '/setting/answer_securityqns')
def post_security_questions():
    if not app.debug and not captcha.verify_captcha():
        flash('Invalid Captcha')
        return redirect(url_for("get_security_questions"))

    # if not captcha.verify_captcha():
    #     flash('Invalid Captcha')
    #     return redirect(url_for("get_security_questions"))
    #
    answer1 = request.form.get('answer1')
    answer2 = request.form.get('answer2')
    answer3 = request.form.get('answer3')
    if answer1 != None and answer2 != None and answer3 != None:
        current_user.answer1 = encrypt(answer1.upper().encode('utf-8'))
        current_user.answer2 = encrypt(answer2.upper().encode('utf-8'))
        current_user.answer3 = encrypt(answer3.upper().encode('utf-8'))
        db.session.commit()
        flash('Security questions successfully answered.')
        return redirect(url_for('get_profile'))
    else:
        flash('Required fields cannot be empty.')
        return redirect(url_for('get_security_questions'))
