# routes.py
# -*- cuding: utf-8 -*-

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

from functools import wraps
from flask import render_template, request, redirect, url_for, flash, jsonify, session, abort, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from . import app
from .models import db, User, Session
from .SetUsers import setUserSession
from config import path
import re
from icecream import ic
ic.disable()


def check_login(session_number):
    ic()
    try:
        if current_user.authenticated:
            ic()
            return ic(redirect(url_for('dashboard', session_number=session_number))), True

    except:
        return ic(redirect(url_for('login', session_number=session_number))), False


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
            return check_login(session_number)[0]
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
    check_login_data = ic(check_login(session_number))
    if check_login_data[1]:
        return check_login_data[0]

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        # Verify the password using its hash
        session_obj = db.session.query(Session).filter_by(number=session_number).first()
        if user and check_password_hash(user.password, password) and user.session == session_obj:
            login_user(user, remember=remember)
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('dashboard', session_number=session_number))
        else:
            flash('Не верные имя пользователя или пароль сессии')

    return render_template('login.html', session_link=session_number)

@app.route('/session<int:session_number>/dashboard')
@login_required
def dashboard(session_number):
    ic()
    questions = [current_user.q1, current_user.q2, current_user.q3, current_user.q4,
                 current_user.q5, current_user.q6, current_user.q7, current_user.q8]

    # Преобразование вопросов в список словарей
    files = [{'id': q.id, 'filename': q.filename, 'hash': q.hash, 'isVirus': q.isVirus} for q in questions]  # не включаем 'answer'
    # Передача списка в шаблон
    return render_template('dashboard.html', logout_link=url_for('logout', session_number=session_number),
                           session_number=session_number,  files=files,
                           firewall_link=url_for('firewall', session_number=session_number))

@app.route('/session<int:session_number>/firewall')
@login_required
def firewall(session_number):
    questions = [current_user.q9, current_user.q10, current_user.q11, current_user.q12,
                 current_user.q13, current_user.q14, current_user.q15, current_user.q16]

    # Преобразование вопросов в список словарей
    ports = [{'id': q.id, 'number': q.number, 'about': q.about, 'isDanger': q.isDanger} for q in questions]  # не включаем 'answer'
    # Передача списка в шаблон
    return render_template('firewall.html', logout_link=url_for('logout', session_number=session_number),
                           session_number=session_number,  ports=ports)

@app.route('/get_user_answers', methods=['GET'])
@login_required
def get_user_answers():
    data = {
        'a1': current_user.a1,
    }
    return jsonify(data)


@app.route('/update_badges', methods=['GET'])
def update_badges():
    data = {}
    session_id = request.args.get('session_id')
    session_obj = db.session.query(Session).filter_by(number=session_id).first()
    users = User.query.filter_by(session=session_obj).all()
    for user in users:
        data[user.username] = {
            'a1': user.a1,
            'a2': user.a2,
        }
    return jsonify(data)


@app.route('/check_answer', methods=['POST'])
def check_answer():
    answer = request.json.get('answer')
    if answer == 'a1':
        setattr(current_user, 'a1', True)
        db.session.commit()
        return jsonify({'correct': True})
    if answer == 'a2':
        setattr(current_user, 'a2', True)
        db.session.commit()
        return jsonify({'correct': True})
    return jsonify({'correct': False})



@app.route('/session<int:session_number>/logout')
@login_required
@anonymous_required
def logout(session_number):
    current_user.authenticated = False
    db.session.add(current_user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login', session_number=session_number))

@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def handle_error(error):
    ic()
    requested_url = ic(request.url)
    return error_do(requested_url)
