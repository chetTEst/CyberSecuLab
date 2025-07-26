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
import bleach
from functools import wraps
from random import shuffle
from flask import render_template, request, redirect, url_for, jsonify, session, abort, current_app, \
    make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room
from urllib.parse import quote, unquote
from collections import defaultdict
from pyseto import Key
from . import app, socketio
from .models import db, User, Session, Question, Option, Assignment, EssayAnswer
from .SetUsers import setUserSession, makeUser
from config import path, PROD_STATE, SK_PASERK, PK_PASERK, TOLLERANCE, SUBDOMAIN, DOMAIN

from icecream import ic

_sk = Key.from_paserk(SK_PASERK)
_pk = Key.from_paserk(PK_PASERK)
active_sessions = {}

ic.enable() if not PROD_STATE else ic.disable()



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
            session_obj = Session.query.get(current_user.session.id)
            session_identifier = session_obj.uuid if session_obj.uuid else session_obj.number
            return redirect(url_for('dashboard', session_identifier=session_identifier)), True
        else:
            logout_user()
            return redirect(url_for('login', session_identifier=session_number)), False

    except:
        return redirect(url_for('login', session_identifier=session_number)), False


def extract_session_number(url):
    # Шаблон регулярного выражения для поиска идентификатора сессии
    pattern = r'/session([^/]+)'

    # Поиск совпадений в URL
    match = re.search(pattern, url)

    # Если найдено совпадение, возвращаем идентификатор сессии
    if match:
        return match.group(1)  # group(1) возвращает значение первой группы захвата
    else:
        return None


def error_do(requested_url):
    ic()
    # Проверяем, содержит ли URL паттерн /session<int:session_number>
    if '/session' in requested_url:
        # Извлекаем номер сессии из URL
        # Извлекаем идентификатор сессии из URL
        match = re.search(r'/session([^/]+)', requested_url)
        if match:
            session_identifier = match.group(1)
            return check_login(session_identifier)[0]
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
    try:
        ic()
        session_identifier = ic(data.get('session_id'))
        username = ic(data.get('username'))
        first_last_name = ic(unquote(data.get('first_last_name', 'teacher maybe')))
                
        # Определяем, является ли идентификатор UUID или числом
        if session_identifier == '0':
            session_obj = Session.query.filter_by(number=0).first()
            room_id = '0'  # Для сессии 0 используем '0' как идентификатор комнаты
        else:
            # Ищем сессию по UUID
            session_obj = Session.query.filter_by(uuid=session_identifier).first()
            if not session_obj:
                return
            room_id = session_identifier  # Используем UUID как идентификатор комнаты

        user = ic(User.query.filter_by(username=username).first())
        
        
        if user and user.session == session_obj:
            ic()
            # Добавляем пользователя в словарь активных сессий
            if session_identifier not in active_sessions:
                active_sessions[session_identifier] = {}
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
                    question_data['essay_question'] = a.question.text if a.question else ''
                questions.append(question_data)
            data = {
                'username': username,
                'first_last_name': first_last_name,
                'questions': questions
            }
            join_room(room_id)
            emit('user_joined', data, room=room_id)
        else:
            ic()
            join_room(room_id)
            emit('user_joined', {'username': 'teacher'}, room=room_id)  
    except Exception as e:
        app.logger.error(f"Error in join_session handler: {e}")


@socketio.on('remove_user')
def handle_remove_user(data):
    try:
        session_identifier = ic(data.get('session_id'))
        username = ic(data.get('username'))

        # Определяем, является ли идентификатор UUID или числом
        if session_identifier == '0':
            session_obj = Session.query.filter_by(number=0).first()
        else:
            # Ищем сессию по UUID
            session_obj = Session.query.filter_by(uuid=session_identifier).first()
            if not session_obj:
                return

        # Удаление пользователя из базы данных
        user = User.query.filter_by(username=username, session_id=session_obj.id).first()
        if user:
            user.active = False
            ic(f'delete {user}, {user.username}')
            db.session.commit()
    except Exception as e:
        app.logger.error(f"Error in remove_user handler: {e}")


@socketio.on('disconnect')
def handle_disconnect():
    try:
        # Удаляем пользователя из словаря активных сессий
        for session_id, users in list(active_sessions.items()):
            for username, sid in list(users.items()):
                if sid == request.sid:
                    del active_sessions[session_id][username]
                    app.logger.info(f"User {username} removed from session {session_id}")
                    # Если в сессии больше нет пользователей, удаляем сессию
                    if not active_sessions[session_id]:
                        del active_sessions[session_id]
                    break
    except Exception as e:
        app.logger.error(f"Error in disconnect handler: {e}")


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
    user_type = request.form.get('user_type', 'teacher')  # по умолчанию 'teacher'

    if user_type == 'teacher':
        short_link, session_number, session_uuid = setUserSession()
        session['session_link'] = session_number
        session['session_uuid'] = session_uuid
        session['short_link'] = short_link
        response = {
                'redirect_url': url_for('start_training')
            }
        return jsonify(response)
    response = {
        'redirect_url': f"https://{SUBDOMAIN}.{DOMAIN}/session{0}"
    }
    return jsonify(response)
        


@app.route('/create-new-user', methods=['POST'])
def create_new_user():
    ic()
    first_last_name = request.form.get('first_last_name')
    if not check_name_format(first_last_name):
        abort(400, "Не верный формат имени: Фамилия Имя")
    
    session_identifier = request.form.get('session_number')
    # Проверяем, является ли идентификатор числом (для сессии 0) или UUID
    if session_identifier == '0':
        session_number = 0
    else:
        # Ищем сессию по UUID
        session_obj = Session.query.filter_by(uuid=session_identifier).first()
        if not session_obj:
            abort(400, "Неверный идентификатор сессии")
        session_number = session_obj.number
    
    
    username = makeUser(session_number, first_last_name)
    session['username'] = username
    session['first_last_name'] = first_last_name

    response = {
        'redirect_url': url_for('register', session_identifier=session_identifier)
    }
    return jsonify(response)


@app.route('/session<path:session_identifier>/register', methods=['GET', 'POST'])
def register(session_identifier):
    username = session.get('username')
    first_last_name = session.get('first_last_name')
    
    # Проверяем, является ли идентификатор числом (для сессии 0) или UUID
    if session_identifier == '0':
        session_number = 0
        session_obj = Session.query.filter_by(number=session_number).first()
    else:
        # Ищем сессию по UUID
        session_obj = Session.query.filter_by(uuid=session_identifier).first()
        if not session_obj:
            return render_template("errors.html")

    user = User.query.filter_by(username=username).first()
    if user and user.session == session_obj:
        login_user(user, remember=True)
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        response = redirect(url_for('dashboard', session_identifier=session_identifier))
        response.set_cookie('session_id', session_identifier)
        response.set_cookie('username', username)
        response.set_cookie('first_last_name', quote(first_last_name))
        return response


@app.route('/start-training', methods=['GET', 'POST'])
def start_training():
    session_link = session.get('session_link')
    session_uuid = session.get('session_uuid')
    short_link = session.get('short_link')
    if not session_link or not session_uuid:
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
        total = sum(1 for a in assignments if a.question.qtype!='essay' and a.question.qtype!='description')
        correct = sum(1 for a in assignments if a.correct and a.question.qtype!='essay' and a.question.qtype!='description')

        # безопасно вычисляем процент
        percent = round((correct / total * 100), 2) if total else 0
        questions = []
        for a in assignments:
            question_data = {
                'id': a.question_id,
                'qtype': a.question.qtype,
                'correct': a.correct,
                'answered': a.answered,
                'question': a.question.text
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
            'questions': questions,
            'percent': f"{percent:.2f}",
        })

    return render_template('training_result.html',
                           session_link=session_link,
                           session_uuid=session_uuid,
                           short_link=short_link,
                           logins=logins)


@app.route('/session<path:session_identifier>')
def index(session_identifier):
    if session_identifier == '0':
        session_number = 0
        try:
            if current_user.authenticated:

                return redirect(url_for('dashboard', session_identifier=session_identifier))

        except:
            return redirect(url_for('login', session_identifier=session_identifier))
    else:
        # Ищем сессию по UUID
        session_obj = Session.query.filter_by(uuid=session_identifier).first()
        if not session_obj:
            return render_template("errors.html")
        
        try:
            if current_user.authenticated:
                return redirect(url_for('dashboard', session_identifier=session_identifier))
        except:
            return redirect(url_for('login', session_identifier=session_identifier))


@app.route('/session<path:session_identifier>/login', methods=['GET'])
def login(session_identifier):
    # Проверяем, является ли идентификатор числом (для сессии 0) или UUID
    if session_identifier == '0':
        session_number = 0
        check_login_data = check_login(session_number)
        if check_login_data[1]:
            return check_login_data[0]
        return render_template('login.html', session_link=session_identifier)
    else:
        # Ищем сессию по UUID
        session_obj = Session.query.filter_by(uuid=session_identifier).first()
        if not session_obj:
            return render_template("errors.html")
        
        check_login_data = check_login(session_obj.number)
        if check_login_data[1]:
            return check_login_data[0]
        return render_template('login.html', session_link=session_identifier)


@app.route('/session<path:session_identifier>/dashboard')
@login_required
def dashboard(session_identifier):

    # Проверяем, является ли идентификатор числом (для сессии 0) или UUID
    if session_identifier == '0':
        session_number = 0
        session_obj = Session.query.filter_by(number=session_number).first()
    else:
        # Ищем сессию по UUID
        session_obj = Session.query.filter_by(uuid=session_identifier).first()
        if not session_obj:
            return render_template("errors.html")

    if not (current_user.active):
        current_user.authenticated = False
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('login', session_identifier=session_identifier))
    
    if current_user.active and session_obj.id != current_user.session_id:
        # Получаем правильный идентификатор для редиректа
        user_session = Session.query.get(current_user.session_id)
        redirect_id = user_session.uuid if user_session.uuid else user_session.number
        return redirect(url_for('dashboard', session_identifier=redirect_id))
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
            "session": session_obj.uuid, "exp": time.time() + 3600, "q": payload_q},
        serializer=json,
        exp=3600
    ).decode("utf-8")

    resp = make_response(
        render_template(
            'dashboard.html',
            session_identifier=session_identifier,
            paseto_token=token,
            paseto_pk=PK_PASERK.split(".", 2)[2],
            logout_link=url_for('logout', session_identifier=session_identifier)
        )
    )
    return resp



@app.route('/session<path:session_identifier>/submit', methods=['POST'])
@login_required
def submit_session(session_identifier):

    # Проверяем, является ли идентификатор числом (для сессии 0) или UUID
    if session_identifier == '0':
        session_id = 0
        session_obj = Session.query.filter_by(number=session_id).first()
        room_id = '0'
    else:
        # Ищем сессию по UUID
        session_obj = Session.query.filter_by(uuid=session_identifier).first()
        if not session_obj:
            return jsonify({"status": "error", "message": "Неверный идентификатор сессии"}), 400
        room_id = session_identifier
    session_id = session_obj.id

    payload = request.get_json(force=True)
    results = payload.get('results', [])
    essays  = payload.get('essays', {})
    username = payload.get('username', "")
    ic(username)
    data_to_socket = defaultdict(dict)

    ALLOWED_TAGS = ["b", "i", "u", "em", "strong", "br", "ul", "ol", "li", "span", "p", "a", "img"]
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
        text = bleach.clean(text, tags=ALLOWED_TAGS, strip=True)
        essay_correct = bool(text)
        data_to_socket[qid]["text"] = text
        data_to_socket[qid]["correct"] = essay_correct
        data_to_socket[qid]["q_type"] = "essay"
        data_to_socket[qid]["answered"] = True  # добавляем это поле
        data_to_socket[qid]["client_correct"] = essay_correct
        q_text = Question.query.filter_by(id=qid).first().text
        data_to_socket[qid]["q_text"] = q_text
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
                text=text
            )
            db.session.add(ea)
        else:
            ea.text = text.strip()

    db.session.commit()

    socketio.emit('answers_post',
                  {'username': username,
                   'questions': dict(data_to_socket),
                   'session_uuid': room_id},
                    namespace='/',
                    room=room_id)
    return jsonify({"status": "ok", "message": "Результаты сохранены"}), 200


@app.route('/session<path:session_identifier>/logout')
@login_required
def logout(session_identifier):
    current_user.authenticated = False
    db.session.add(current_user)
    db.session.commit()
    response = make_response(redirect(url_for('login', session_identifier=session_identifier)))
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

@app.errorhandler(429)
def ratelimit_handler(e):
    return f"Лимит запросов превышен, попробуйте через {e.description}", 429
