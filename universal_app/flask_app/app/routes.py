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
import time
import pyseto
import json
from functools import wraps
from random import shuffle
from markupsafe import escape, Markup
from flask import render_template, request, redirect, url_for, flash, jsonify, session, abort, current_app, \
    make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room
from urllib.parse import quote, unquote
from datetime import datetime
from collections import defaultdict
from pyseto import Key
from . import app
from .models import db, User, Session, Question, Option, Assignment, EssayAnswer
from .SetUsers import setUserSession, makeUser
from config import path, TOKEN_API_KEY, PROD_STATE, SK_PASERK, PK_PASERK, SALT, TOLLERANCE

from icecream import ic

_sk = Key.from_paserk(SK_PASERK)
_pk = Key.from_paserk(PK_PASERK)

ic.enable() if not PROD_STATE else ic.disable()
socketio = SocketIO(app)


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


login_manager = LoginManager()
login_manager.init_app(app)


def check_name_format(text):
    pattern = r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$'
    if not re.match(pattern, text):
        return False
    return True


def check_login(session_number):
    try:
        if current_user.authenticated:
            return redirect(url_for('dashboard', session_number=session_number)), True
        else:
            logout_user()
            return redirect(url_for('login', session_number=session_number)), False

    except:
        return redirect(url_for('login', session_number=session_number)), False


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
        session_number = extract_session_number(requested_url)
        if session_number:
            return check_login(session_number)[0]
        else:
            return render_template("errors.html")
    else:
        # Возвращаем HTML-страницу для ошибок не связанных с сессией
        return render_template("errors.html")


@socketio.on('connect')
def handle_connect():
    ic()


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
        assignments = (Assignment.query
                       .filter_by(user_id=user.id)  # фильтруем по логину
                       .join(Question)  # если требуется доступ к вопросам
                       .all())
        questions = []
        for a in assignments:
            question_data = {
                'id': a.question_id,
                'qtype': a.question.qtype,
                'correct': a.correct,
                'user_correct': a.client_correct
            }

            # Добавляем текст эссе, если это эссе
            if a.question.qtype == 'essay':
                essay_answer = EssayAnswer.query.filter_by(
                    user_id=user.id,
                    question_id=a.question_id,
                    session_id=session_obj.id
                ).first()
                question_data['essay_text'] = essay_answer.text if essay_answer else ''

            questions.append(question_data)
        data = {
            'username': username,
            'first_last_name': first_last_name,
            'questions': questions
        }
        join_room(session_id)
        emit('user_joined', data, room=session_id)
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
        user.active = False
        ic(f'delete {user}, {user.username}')
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Route for the homepage with the "Start training" button
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/start-training-async', methods=['POST'])
def start_training_async():
    short_link, session_number = setUserSession()
    session['session_link'] = session_number
    session['short_link'] = short_link
    response = {
        'redirect_url': url_for('start_training')
    }
    return jsonify(response)


@app.route('/create-new-user', methods=['POST'])
def create_new_user():
    first_last_name = request.form.get('first_last_name')
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
        response = redirect(url_for('dashboard', sid=session_number))
        response.set_cookie('session_id', str(session_number))
        response.set_cookie('username', username)
        response.set_cookie('first_last_name', quote(first_last_name))
        return response


@app.route('/start-training', methods=['GET', 'POST'])
def start_training():
    session_link = session.get('session_link')
    short_link = session.get('short_link')
    if not session_link:
        # Перенаправляем на главную страницу
        return redirect(url_for('home'))

    # Получаем объект текущей сессии
    session_obj = Session.query.filter_by(number=session_link).first()
    if not session_obj:
        # Если сессия не найдена, перенаправляем на главную
        return redirect(url_for('home'))

    # Получаем всех пользователей, связанных с этой сессией
    users = User.query.filter_by(session_id=session_obj.id, active=True).all()

    # Формируем список словарей с полями first_last_name и username
    logins = []
    for user in users:
        assignments = (Assignment.query
                       .filter_by(user_id=user.id)
                       .join(Question)
                       .all())

        questions = []
        for a in assignments:
            question_data = {
                'id': a.question_id,
                'qtype': a.question.qtype,
                'correct': a.correct,
                'answered': a.answered
            }

            # Добавляем текст эссе, если это эссе
            if a.question.qtype == 'essay':
                essay_answer = EssayAnswer.query.filter_by(
                    user_id=user.id,
                    question_id=a.question_id,
                    session_id=session_obj.id
                ).first()
                question_data['essay_text'] = essay_answer.text if essay_answer else ''

            questions.append(question_data)

        logins.append({
            'first_last_name': user.first_last_name,
            'username': user.username,
            'questions': questions
        })

    return render_template('training_result.html', session_link=session_link, short_link=short_link, logins=logins)


@app.route('/session<int:session_number>')
def index(session_number):

    try:
        if current_user.authenticated:

            return redirect(url_for('dashboard', session_number=session_number))

    except:
        return redirect(url_for('login', session_number=session_number))


@app.route('/session<int:session_number>/login', methods=['GET'])
def login(session_number):
    check_login_data = check_login(session_number)
    if check_login_data[1]:
        return check_login_data[0]

    return render_template('login.html', session_link=session_number)


@app.route('/session<int:sid>/dashboard')
@login_required
def dashboard(sid):
    if not (current_user.active):
        current_user.authenticated = False
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('login', session_number=sid))
    assignments = Assignment.query \
        .filter_by(user_id=current_user.id) \
        .all()
    qs = [{'id': a.question_id, "correct": a.correct, "answered": a.answered} for a in assignments]
    # 2) Собираем payload для PASETO
    payload_q = []
    for q in qs:
        qst = Question.query.filter_by(id=q["id"]).first()
        entry = {
            "id": q["id"],
            "text": qst.text,
            "type": qst.qtype,
            "correct": q["correct"],
            "answered": q["answered"],
        }

        if qst.qtype in ("multichoice", "truefalse"):
            entry["hashes"] = [{"text": opt.text.strip()} for opt in
                               Option.query.filter_by(question_id=qst.id, is_correct=True)]
            entry["options"] = [{"text": opt.text.strip()} for opt in
                                Option.query.filter_by(question_id=qst.id, is_correct=False)]
            shuffle(entry["options"])
        elif qst.qtype == "numerical":
            entry["hashes"], entry["tol"] = Option.query.filter_by(question_id=qst.id).first().text.strip(), TOLLERANCE
        elif qst.qtype == "shortanswer":
            entry["hashes"] = Option.query.filter_by(question_id=qst.id).first().text.strip()
        elif qst.qtype == "matching":
            entry["hashes"] = [f"{opt.match_key.strip()}" for opt in
                               Option.query.filter_by(question_id=qst.id, is_correct=True)]
            entry["options"] = [f"{opt.text.strip()}|{opt.match_key.strip()}" for opt in
                                Option.query.filter_by(question_id=qst.id, is_correct=False)]
        elif qst.qtype == "missingword":
            entry["hashes"] = [{"text": opt.text.strip()} for opt in
                               Option.query.filter_by(question_id=qst.id, is_correct=True)]
            entry["options"] = [{"text": opt.text.strip()} for opt in
                                Option.query.filter_by(question_id=qst.id, is_correct=False)]
            shuffle(entry["options"])

        # qtype "essay", "description": просто пропускаем

        payload_q.append(entry)

    token = pyseto.encode(
        _sk,
        {
            "session": sid, "exp": time.time() + 3600, "q": payload_q},
        serializer=json,
        exp=3600
    ).decode("utf-8")

    resp = make_response(
        render_template(
            'dashboard.html',
            session_number=sid,
            paseto_token=token,
            paseto_pk=PK_PASERK.split(".", 2)[2],
            logout_link=url_for('logout', session_number=sid)
        )
    )
    return resp



@app.route('/session<int:session_id>/submit', methods=['POST'])
@login_required
def submit_session(session_id):
    payload = request.get_json(force=True)
    results = payload.get('results', [])
    essays  = payload.get('essays', {})
    username = payload.get('username', "")
    ic(username)
    data_to_socket = defaultdict(dict)


    # кэш правильных ответов вида { question_id: ['ответ1','ответ2',...] }
    correct_map = current_app.config.get('CORRECT_ANSWERS', {})

    for item in results:
        qid           = int(item['question_id'])
        client_corr   = bool(item.get('correct', False))
        raw_answer    = item.get('answer', [])
        q_type        = item.get('question_type', "")


        # нормализуем user_answer в список строк
        if isinstance(raw_answer, str):
            ua_list = [raw_answer.strip().lower()] if raw_answer.strip() else []
        else:
            ua_list = [str(x).strip().lower() for x in raw_answer]

        # серверная проверка: сравниваем множества в нижнем регистре
        corr_list   = correct_map.get(qid, [])
        ua_list     = [u.lower() for u in ua_list]
        corr_set    = {c.lower() for c in corr_list}
        ua_set      = set(ua_list)
        server_corr = False
        if corr_list and ua_list:
            if q_type == 'multichoice':
                server_corr = ua_set == corr_set
            else:
                server_corr = ua_list == corr_list

        # upsert в Assignment
        asg = Assignment.query.filter_by(
            user_id=current_user.id,
            question_id=qid
        ).first()

        asg.user_response  = json.dumps(ua_list, ensure_ascii=False)
        asg.client_correct = client_corr
        asg.correct = server_corr
        asg.answered       = True
        data_to_socket[qid]["correct"] = server_corr
        data_to_socket[qid]["answered"] = True
        data_to_socket[qid]["q_type"] = q_type
        data_to_socket[qid]["client_correct"] = client_corr
    # обработка эссе
    for qid_str, text in essays.items():
        qid = int(qid_str)
        essay_correct = bool(text.strip())
        data_to_socket[qid]["text"] = text
        data_to_socket[qid]["correct"] = essay_correct
        data_to_socket[qid]["q_type"] = "essay"
        data_to_socket[qid]["answered"] = True  # добавляем это поле
        data_to_socket[qid]["client_correct"] = essay_correct
        ea = EssayAnswer.query.filter_by(
            user_id=current_user.id,
            question_id=qid,
            session_id=session_id
        ).first()
        if not ea:
            ea = EssayAnswer(
                user_id=current_user.id,
                question_id=qid,
                session_id=session_id,
                text=text.strip()
            )
            db.session.add(ea)
        else:
            ea.text = text.strip()

    db.session.commit()

    socketio.emit('answers_post',
                  {'username': username,
                   'questions': dict(data_to_socket),
                   'session_id': session_id},
                    namespace='/',
                    room=str(session_id))
    return jsonify({"status": "ok", "message": "Результаты сохранены"}), 200


@app.route('/session<int:session_number>/logout')
@login_required
def logout(session_number):
    current_user.authenticated = False
    db.session.add(current_user)
    db.session.commit()
    response = make_response(redirect(url_for('login', session_number=session_number)))
    response.set_cookie('clear_quiz_data', 'true', max_age=5)  # Кука на 5 секунд
    logout_user()
    return response


@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def devtools_config():
    # возвращаем 404 без рендеринга шаблона
    return '', 404


@app.errorhandler(400)
def bad_request(error):
    return str(error.description), 400


@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def handle_error(error):
    ic()
    requested_url = request.url
    return error_do(requested_url)
