# routes.py

'''
Welcome to the open-source file for the "Automatic Security Training and Testing System"
developed by Alexey Chetverov. This application aims to provide a robust tool for learning
and enhancing cybersecurity skills.

The system presented in this repository is designed to facilitate the process of education,
self-assessment, and comprehensive exploration of various aspects of cybersecurity. Users
will be able to utilize its functionalities to train their skills, test their knowledge, and
delve into different cybersecurity domains.

One of the unique features of this project is its licensing under Apache 2.0.
This means that users have the right to copy and distribute the software while preserving
the author's copyright. The open-source nature of the code allows the community to contribute
to the project's development, enhance its functionalities, and address potential issues.

We invite all interested individuals to join this exciting endeavor and contribute to the
growth of a tool that can make the world of cybersecurity even more reliable and secure.
Your ideas, feedback, and suggestions are warmly welcomed as they will help us improve
this experience further.

Thank you for your interest in this project, and we hope that this system will become
a valuable asset for anyone seeking to ensure data and information security in the modern
digital landscape.'''

import pyotp
import qrcode
import string
from base64 import b64encode
from functools import wraps
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from . import app
from .models import db, User, File, Permission, Session
from .SetUsers import setUserSession
from os import listdir
from config import path
from os.path import join as pjoin
from random import choice, randint
import re
from icecream import ic
ic.disable()


def generate_sequences(length):
    sequence1 = ''.join(choice(string.ascii_letters) for _ in range(length))
    sequence2 = sequence1[:-1] + choice(string.ascii_letters.replace(sequence1[-1], ''))
    sequence3 = sequence1[:-2] + choice(string.ascii_letters.replace(sequence1[-2], ''))
    return sequence1, sequence2, sequence3


def anonymous_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Проверка, вошел ли пользователь в систему
        if current_user.is_authenticated:
            # Если пользователь вошел, выполняем оригинальную функцию
            return f(*args, **kwargs)
        session_number = kwargs.get('session_number', None)
        if session_number is not None:
            return redirect(url_for('login', session_number=session_number))
        else:
            return render_template("errors.html")
        return f(*args, **kwargs)
    return decorated_function


def extract_session_number(url):
    # Шаблон регулярного выражения для поиска номера сессии
    pattern = r'/session(\d+)'

    # Поиск совпадений в URL
    match = re.search(pattern, url)

    # Если найдено совпадение, возвращаем номер сессии
    if match:
        return match.group(1)  # group(1) возвращает значение первой группы захвата
    else:
        return None


def error_do(requested_url):
    ic()
    # Проверяем, содержит ли URL паттерн /session<int:session_number>
    if '/session' in requested_url:
        # Извлекаем номер сессии из URL
        session_number = ic(extract_session_number(requested_url))
        if session_number:
            ic()
            try:
                if current_user.authenticated:
                    ic()
                    return redirect(url_for('dashboard', session_number=session_number))

            except:
                return ic(redirect(url_for('login', session_number=session_number)))
        else:
            ic()
            return render_template("errors.html")
    else:
        # Возвращаем HTML-страницу для ошибок не связанных с сессией
        return render_template("errors.html")


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
    student_count = int(request.form.get('student_count'))
    if student_count > 30:
        abort(400, "Максимальное ко-во учеников: 30.")
    session_link, logins_markup, passwords_markup = setUserSession(student_count)
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
    if not session_link or not logins_markup or not passwords_markup:
        # Перенаправляем на главную страницу
        return redirect(url_for('home'))
    return render_template('training_result.html', session_link=session_link, logins=logins_markup, passwords=passwords_markup)

@app.route('/session<int:session_number>')
def index(session_number):
    ic()
    try:
        if current_user.authenticated:
            ic()
            return redirect(url_for('dashboard', session_number=session_number))

    except:
        return ic(redirect(url_for('login', session_number=session_number)))
@app.route('/session<int:session_number>/login', methods=['GET', 'POST'])
def login(session_number):
    ic()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        # Verify the password using its hash
        if user and check_password_hash(user.password, password) and user.session == session_number:
            login_user(user, remember=remember)
            if not user.first_enter:
                user.first_enter = True
            if user.two_factor_enabled:
                return redirect(url_for('login_two_factor', session_number=session_number))
            else:
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('dashboard', session_number=session_number))
        else:
            flash('Не верные имя пользователя или пароль сессии')
    ic()
    return render_template('login.html', session_link=session_number)

@app.route('/session<int:session_number>/logout')
@login_required
@anonymous_required
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
                           user_two_factor=user_two_factor,
                           session_number=session_number)


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
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(totp.provisioning_uri(name=current_user.username, issuer_name='Урок сетевая безопасность'))
    qr.make(fit=True)
    qr_code = qr.make_image(fill_color="black", back_color="white")
    ic(qr_code)
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
    if totp.verify(user_code):
        current_user.two_factor_enabled = True
        db.session.commit()
        flash('Двухфакторная аутентификация подключена!')
        return redirect(url_for('dashboard', session_number=session_number))
    else:
        flash('Не правильный код.')
        return redirect(url_for('two_factor_authentication', session_number=session_number))

@app.route('/session<int:session_number>/login-two-factor')
def login_two_factor(session_number):
    return render_template('loginTF.html', action_link=url_for('login_two_factor_check', session_number=session_number))


@app.route('/session<int:session_number>/login-two-factor-check', methods=['POST'])
def login_two_factor_check(session_number):
    requested_url = ic(request.url)
    try:
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
    except:
        return error_do(requested_url)


@app.route('/update_badges', methods=['GET'])
def update_badges():
    data = {}
    session = request.args.get('session_id')
    users = User.query.filter_by(session=session).all()  # Замените это на ваш запрос к БД
    for user in users:
        data[user.username] = {
            'authenticated': user.first_enter,
            'two_factor_enabled': user.two_factor_enabled,
            'authenticated_two_factor_enabled': user.two_factor_enter,
            'check_message_is_true': user.check_message
        }
    return jsonify(data)

@app.route('/session<int:session_number>/resultmessage', methods=['POST'])
@login_required
def resultmessage(session_number):
    message = request.form.get('message')
    wrong_answer = request.form.get('va')
    message_original = message
    answer1, answer2, answer3 = generate_sequences(15)
    modification_type = randint(1, 3)  # Случайным образом выбираем тип изменения
    def integrity(message):
        modification_type = randint(1, 2)
        if modification_type == 1:
            position = randint(0, len(message) - 1)  # Случайным образом выбираем позицию для удаления символа
            modified_message = message[:position] + message[position + 1:]
            return modified_message
        else:
            position = randint(0, len(message) - 1)  # Случайным образом выбираем позицию для замены символа
            random_char = chr(randint(32, 126))  # Случайным образом выбираем символ ASCII
            modified_message = message[:position] + random_char + message[position + 1:]
        return modified_message
    def availability(message):
        position = randint(0, len(message) - 3) # Случайным образом выбираем окончание сообщения
        modified_message = f'{message[:position]}... Сообщение больше не доступно'
        return modified_message
    def confidentiality(message):
        modified_message = f'Служба контроля за сообщениями проверила ваше сообщение: "{message}"'
        return modified_message

    if modification_type == 1:
        answer = answer1
        message = integrity(message)
    elif modification_type == 2:
        answer = answer2
        message = availability(message)
    elif modification_type == 3:
        answer = answer3
        message = confidentiality(message)
    if wrong_answer:
        flash('Ой, ответ не верный. Давай по-новой!')
    return render_template("returnmessage.html",
                           answer=answer,
                           answer1=answer1,
                           answer2=answer2,
                           answer3=answer3,
                           message=message,
                           dashboard_link=url_for('dashboard', session_number=session_number),
                           session_number=session_number,
                           message_original=message_original)


@app.route('/record-answer', methods=['POST'])
@login_required
def record_answer():
    current_user.check_message = True
    db.session.commit()
    return jsonify({'success': True})


@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def handle_error(error):
    requested_url = ic(request.url)
    return error_do(requested_url)
