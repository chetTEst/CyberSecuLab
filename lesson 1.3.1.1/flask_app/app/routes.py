# routes.py
import pyotp
import qrcode
import json
from base64 import b64encode
from functools import wraps
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, send_from_directory, Markup, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from . import app
from .models import db, User, File, Permission, Session
from .SetUsers import setUserSession
from os import listdir
from config import path
from os.path import join as pjoin


def anonymous_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for the homepage with the "Start training" button
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/start-training-async', methods=['POST'])
def start_training_async():
    session_link, logins_markup, passwords_markup = setUserSession(12)
    session['session_link'] = session_link
    session['logins'] = logins_markup
    session['passwords'] = passwords_markup
    response = {
        'redirect_url': url_for('start_training')
    }
    return jsonify(response)

@app.route('/start-training', methods=['GET', 'POST'])
def start_training():
    session_link = session.get('session_link')
    logins_markup = session.get('logins')
    passwords_markup = session.get('passwords')
    return render_template('training_result.html', session_link=session_link, logins=logins_markup, passwords=passwords_markup)

@app.route('/session<int:session_number>')
def index(session_number):
    return render_template('login.html', session_link=session_number)

@app.route('/session<int:session_number>/login', methods=['GET', 'POST'])
def login(session_number):
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        # Verify the password using its hash
        if user and check_password_hash(user.password, password) and user.session == session_number:
            login_user(user, remember=remember)
            if user.two_factor_enabled:
                return redirect(url_for('login_two_factor', session_number=session_number))
            else:
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('dashboard', session_number=session_number))
        else:
            flash('Не верные имя пользователя или пароль сессии')

    return render_template('login.html', session_link=session_number)

@app.route('/session<int:session_number>/logout')
@login_required
def logout(session_number):
    current_user.authenticated = False
    db.session.add(current_user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login', session_number=session_number))

@app.route('/session<int:session_number>/dashboard')
@login_required
def dashboard(session_number):
    # Get the role of the current user

    user_role = current_user.role
    user_two_factor = current_user.two_factor_enabled

    # Get all files that the user has permission to access
    permissions = Permission.query.filter(Permission.role <= user_role).all()

    # Get the ids of the files that the user has permission to access
    file_ids = [permission.file_id for permission in permissions]
    # Get the files that the user has permission to access
    files = File.query.filter(File.id.in_(file_ids)).all()
    # Get the path of the files directory
    files_dir = pjoin(path, 'app', 'files')

    # Get all the file names in the files directory
    all_files = listdir(files_dir)

    # Filter the files based on the user's permissions
    accessible_files = [{"path":file} for file in all_files if file in [f.path for f in files]]

    return render_template('dashboard.html', files=accessible_files,
                           logout_link=url_for('logout', session_number=session_number),
                           two_factor_authentication_link=url_for('two_factor_authentication', session_number=session_number),
                           user_two_factor=user_two_factor)


@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/session<int:session_number>/two_factor_authentication')
@login_required
def two_factor_authentication(session_number):
    # Generate a new secret key for the user
    if not current_user.two_factor_secret:
        secret_key = pyotp.random_base32()
    else:
        secret_key = current_user.two_factor_secret

    # Save the secret key to the user's model
    current_user.two_factor_secret = secret_key
    db.session.commit()

    # Generate a QR code for the secret key
    totp = pyotp.totp.TOTP(secret_key)
    qr_code = qrcode.make(totp.provisioning_uri(name=current_user.username, issuer_name='Урок сетевая безопасность'))
    qr_code = qr_code.resize((200, 200))
    # Convert the QR code image to bytes
    qr_code_bytes = BytesIO()
    qr_code.save(qr_code_bytes, format='PNG')
    qr_code_bytes.seek(0)
    qr_code_base64 = b64encode(qr_code_bytes.getvalue()).decode('utf-8')
    return render_template('two_factor_authentication.html', qr_code=qr_code_base64,
                           two_factor_verification_link=url_for('two_factor_verification', session_number=session_number),
                           dashboard_link=url_for('dashboard', session_number=session_number))

@app.route('/session<int:session_number>/two-factor-verification', methods=['POST'])
@login_required
def two_factor_verification(session_number):
    user_code = request.form.get('code')

    # Verify the OTP provided by the user
    totp = pyotp.TOTP(current_user.two_factor_secret)
    print(totp)
    if totp.verify(user_code):
        current_user.two_factor_enabled = True
        db.session.commit()
        flash('Двухфакторная аутентификация подключена!')
        return redirect(url_for('dashboard', session_number=session_number))
    else:
        flash('Не правильный код.')
        return redirect(url_for('two_factor_authentication', session_number=session_number))

@app.route('/session<int:session_number>/login-two-factor')
@anonymous_required
def login_two_factor(session_number):
    return render_template('loginTF.html', action_link=url_for('login_two_factor_check', session_number=session_number))


@app.route('/session<int:session_number>/login-two-factor-check', methods=['POST'])
@anonymous_required
def login_two_factor_check(session_number):
    user_code = request.form.get('code')
    # Verify the OTP provided by the user
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if totp.verify(user_code):
        current_user.authenticated = True
        current_user.two_factor_enter = True
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('dashboard', session_number=session_number))
    else:
        flash('Не правильный код.')
        return render_template('loginTF.html', acton_link=url_for('login_two_factor_check', session_number=session_number))


@app.route('/update_badges', methods=['GET'])
def update_badges():
    data = {}
    session = request.args.get('session_id')
    users = User.query.filter_by(session=session).all()  # Замените это на ваш запрос к БД
    for user in users:
        data[user.username] = {
            'authenticated': user.authenticated,
            'two_factor_enabled': user.two_factor_enabled,
            'authenticated_two_factor_enabled': user.two_factor_enter
        }
    return jsonify(data)

