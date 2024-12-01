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
import re

from functools import wraps
from flask import render_template, request, redirect, url_for, flash, jsonify, session, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room
from urllib.parse import quote, unquote
from . import app
from .models import db, User, Session, IPs
from .SetUsers import setUserSession, makeUser
from config import path, TOKEN_API_KEY, PROD_STATE

from icecream import ic

ic.enable() if not PROD_STATE else ic.disable()

socketio = SocketIO(app)


def check_name_format(text):
    ic()
    pattern = r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$'
    if not re.match(pattern, text):
        return False
    return True


def check_login(session_number):
    try:
        if current_user.authenticated:
            return redirect(url_for('dashboard', session_number=session_number)), True

    except:
        return redirect(url_for('login', session_number=session_number)), False


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


@socketio.on('connect')
def handle_connect():
    ic()
    ic("Client connected")


@socketio.on('join_session')
def handle_join(data):
    ic()
    session_id = ic(data.get('session_id'))
    username = ic(data.get('username'))
    first_last_name = ic(unquote(data.get('first_last_name', 'teacher maybe')))
    session_obj = Session.query.filter_by(number=session_id).first()

    user = ic(User.query.filter_by(username=username).first())
    if user and user.session == session_obj:
        ic()
        join_room(session_id)
        emit('user_joined', {'username': username, 'first_last_name': first_last_name}, room=session_id)
    else:
        ic()
        join_room(session_id)
        emit('user_joined', {'username': 'teacher'}, room=session_id)  #


@socketio.on('remove_user')
def handle_remove_user(data):
    session_id = ic(data.get('session_id'))
    username = ic(data.get('username'))

    # Удаление пользователя из базы данных
    user = User.query.filter_by(username=username, session_id=session_id).first()
    if user:
        ic(f'delete {user}, {user.username}')
        db.session.delete(user)
        db.session.commit()


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
    ic()
    short_link, session_number = setUserSession()
    session['session_link'] = session_number
    session['short_link'] = short_link
    response = {
        'redirect_url': url_for('start_training')
    }
    return jsonify(response)

@app.route('/create-new-user', methods=['POST'])
def create_new_user():
    ic()
    first_last_name = ic(request.form.get('first_last_name'))
    if not check_name_format(first_last_name):
        abort(400, "Не верный формат имени: Фамилия Имя")
    session_number = int(request.form.get('session_number'))
    username = makeUser(session_number, first_last_name)
    session['username'] = username
    session['first_last_name'] = first_last_name

    response = {
        'redirect_url': url_for('register', session_number=session_number)
    }
    return jsonify(response)



@app.route('/start-training', methods=['GET', 'POST'])
def start_training():
    session_link = session.get('session_link')
    short_link = session.get('short_link')
    ic()
    if not session_link:
        # Перенаправляем на главную страницу
        return redirect(url_for('home'))

    # Получаем объект текущей сессии
    session_obj = Session.query.filter_by(number=session_link).first()
    if not session_obj:
        # Если сессия не найдена, перенаправляем на главную
        return redirect(url_for('home'))

    # Получаем всех пользователей, связанных с этой сессией
    users = User.query.filter_by(session_id=session_obj.id).all()

    # Формируем список словарей с полями first_last_name и username
    logins = [{"first_last_name": user.first_last_name, "username": user.username} for user in users]

    return render_template('training_result.html', session_link=session_link, short_link=short_link, logins=logins)


@app.route('/session<int:session_number>')
def index(session_number):
    return render_template('login.html', session_link=session_number)


@app.route('/session<int:session_number>/register', methods=['GET', 'POST'])
def register(session_number):
    username = session.get('username')
    first_last_name = session.get('first_last_name')
    session_obj = Session.query.filter_by(number=session_number).first()

    user = User.query.filter_by(username=username).first()
    if user and user.session == session_obj:
        login_user(user, remember=True)
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        response = redirect(url_for('dashboard', session_number=session_number))
        response.set_cookie('session_id', str(session_number))
        response.set_cookie('username', username)
        response.set_cookie('first_last_name', quote(first_last_name))
        return response
    # Set a cookie for browser-based session tracking


@app.route('/session<int:session_number>/login', methods=['GET'])
def login(session_number):
    check_login_data = ic(check_login(session_number))
    if check_login_data[1]:
        return check_login_data[0]

    return render_template('login.html', session_link=session_number)


@app.route('/session<int:session_number>/dashboard')
@login_required
def dashboard(session_number):
    questions = [current_user.q1, current_user.q2, current_user.q3, current_user.q4,
                 current_user.q5, current_user.q6, current_user.q7, current_user.q8,
                 current_user.q9, current_user.q10]

    # Преобразование вопросов в список словарей
    ips = [{'id': q.id, 'number': q.number, 'value': q.value, 'isDanger': q.isDanger} for q in
           questions]  # не включаем 'answer'
    # Передача списка в шаблон
    return render_template('dashboard.html', logout_link=url_for('logout', session_number=session_number),
                           session_number=session_number, ips=ips)


@app.route('/get_user_answers', methods=['GET'])
@anonymous_required
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
        }
    return jsonify(data)


@app.route('/check_answer', methods=['POST'])
@anonymous_required
def check_answer():
    answer = request.json.get('answer')
    if answer == 'a1':
        setattr(current_user, 'a1', True)
        db.session.commit()
        return jsonify({'correct': True})
    return jsonify({'correct': False})


@app.route('/session<int:session_number>/logout')
@login_required
def logout(session_number):
    current_user.authenticated = False
    db.session.add(current_user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login', session_number=session_number))

@app.errorhandler(400)
def bad_request(error):
    return str(error.description), 400


@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def handle_error(error):
    ic()
    requested_url = ic(request.url)
    return error_do(requested_url)
