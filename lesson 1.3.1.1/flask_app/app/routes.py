# routes.py
import pyotp
import qrcode
from base64 import b64encode
from functools import wraps
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, send_from_directory, Markup
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


@app.route('/start-training', methods=['POST'])
def start_training():
    session_link, logins_markup, passwords_markup = setUserSession(20)
    return render_template('training_result.html', session_link=session_link, logins=logins_markup, passwords=passwords_markup)


@app.route('/session<int:session_number>')
def index(session_number):
    return render_template('login.html')

@app.route('/session<int:session_number>/login', methods=['GET', 'POST'])
def login(session_number):
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        # Verify the password using its hash
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            if current_user.two_factor_enabled:
                return redirect(url_for('login_two_factor'))
            else:
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('dashboard'))

        else:
            flash('Не верные имя пользователя или пароль')

    return render_template('login.html')

@app.route('/session<int:session_number>/logout')
@login_required
def logout(session_number):
    current_user.authenticated = False
    db.session.add(current_user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))

@app.route('/session<int:session_number>/dashboard')
@login_required
def dashboard(session_number):
    # Get the role of the current user

    user_role = current_user.role

    # Get all files that the user has permission to access
    permissions = Permission.query.filter_by(role=user_role).all()

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
    print(accessible_files)

    return render_template('dashboard.html', files=accessible_files)



@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/two_factor_authentication')
@login_required
def two_factor_authentication():
    # Generate a new secret key for the user
    secret_key = pyotp.random_base32()

    # Save the secret key to the user's model
    current_user.two_factor_secret = secret_key
    db.session.commit()

    # Generate a QR code for the secret key
    totp = pyotp.totp.TOTP(secret_key)
    qr_code = qrcode.make(totp.provisioning_uri(name=current_user.username, issuer_name='сетевая безопасность'))
    qr_code = qr_code.resize((200, 200))
    # Convert the QR code image to bytes
    qr_code_bytes = BytesIO()
    qr_code.save(qr_code_bytes, format='PNG')
    qr_code_bytes.seek(0)
    qr_code_base64 = b64encode(qr_code_bytes.getvalue()).decode('utf-8')
    return render_template('two_factor_authentication.html', qr_code=qr_code_base64)

@app.route('/two-factor-verification', methods=['POST'])
@login_required
def two_factor_verification():
    user_code = request.form.get('code')

    # Verify the OTP provided by the user
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if totp.verify(user_code):
        current_user.two_factor_enabled = True
        db.session.commit()
        flash('Двухфакторная аутентификация подключена!')
        return redirect(url_for('dashboard'))
    else:
        flash('Не правильный код.')
        return redirect(url_for('two_factor_authentication'))

@app.route('/login-two-factor')
@anonymous_required
def login_two_factor():
    return render_template('loginTF.html')


@app.route('/login-two-factor-check', methods=['POST'])
@anonymous_required
def login_two_factor_check():
    user_code = request.form.get('code')
    # Verify the OTP provided by the user
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if totp.verify(user_code):
        current_user.authenticated = True
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('dashboard'))
    else:
        flash('Не правильный код.')
        return render_template('loginTF.html')