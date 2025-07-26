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
from flask import (
    render_template, request, redirect, url_for, jsonify, session, abort, 
    current_app, make_response, Blueprint
)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import emit
from urllib.parse import quote
from collections import defaultdict
from pyseto import Key
from . import redis_cache
from .RedisCacheLib import get_correct_answers



from .models import db, User, Session, Question, Option, Assignment, EssayAnswer
from .SetUsers import setUserSession, makeUser
from config import path, SK_PASERK, PK_PASERK, TOLLERANCE, SUBDOMAIN, DOMAIN

_sk = Key.from_paserk(SK_PASERK)
_pk = Key.from_paserk(PK_PASERK)

bp = Blueprint('main', __name__)


def anonymous_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Проверка, вошел ли пользователь в систему
        if current_user.is_authenticated:
            # Если пользователь вошел, выполняем оригинальную функцию
            return f(*args, **kwargs)
        session_number = kwargs.get('session_number', None)
        if session_number is not None:
            return redirect(url_for('main.login', session_number=session_number))
        else:
            return render_template("errors.html")

    return decorated_function


login_manager = LoginManager()
login_manager.init_app(current_app)



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
            return redirect(url_for('main.dashboard', session_identifier=session_identifier)), True
        else:
            logout_user()
            return redirect(url_for('main.login', session_identifier=session_number)), False

    except:
        return redirect(url_for('main.login', session_identifier=session_number)), False

def error_do(requested_url):
    current_app.logger.debug(f"====== error_do =======")
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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Route for the homepage with the "Start training" button
@bp.route('/')
def home():
    current_app.logger.debug(f"====== home =======")
    return render_template('home.html')


@bp.route('/start-training-async', methods=['POST'])
def start_training_async():
    current_app.logger.debug(f"=== AJAX REQUEST RECEIVED ====== start-training-async =======")
    user_type = request.form.get('user_type', 'teacher')  # по умолчанию 'teacher'
    current_app.logger.debug(f"Получен тип пользователя {user_type}")

    if user_type == 'teacher':
        def create_session_async():
            try:
                short_link, session_number, session_uuid = setUserSession()
                session['session_link'] = session_number
                session['session_uuid'] = session_uuid
                session['short_link'] = short_link
                return short_link, session_number, session_uuid
            except Exception as e:
                current_app.logger.error(f"Ошибка создания сессии: {e}")
                return None, None, None
                
        short_link, session_number, session_uuid = create_session_async()  
        current_app.logger.debug(f"Создана Сессия {session_number} {short_link} {session_uuid}")

        if session_number is None:
            return jsonify({'error': 'Ошибка создания сессии'}), 500
            
        response = {
            'redirect_url': url_for('main.start_training')
        }
        current_app.logger.debug(f"Отправка данных после открытия сессии {session_number} {short_link} {session_uuid}")
        return jsonify(response)
        
    response = {
        'redirect_url': f"https://{SUBDOMAIN}.{DOMAIN}/session{0}"
    }
    return jsonify(response)
        


@bp.route('/create-new-user', methods=['POST'])
def create_new_user():
    current_app.logger.debug(f"====== create-new-user =======")
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
        'redirect_url': url_for('main.register', session_identifier=session_identifier)
    }
    return jsonify(response)


@bp.route('/session<path:session_identifier>/register', methods=['GET', 'POST'])
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
        response = redirect(url_for('main.dashboard', session_identifier=session_identifier))
        response.set_cookie('session_id', session_identifier)
        response.set_cookie('username', username)
        response.set_cookie('first_last_name', quote(first_last_name))
        return response


@bp.route('/start-training', methods=['GET', 'POST'])
def start_training():
    current_app.logger.debug(f"========= start_training =========")
    session_link = session.get('session_link')
    session_uuid = session.get('session_uuid')
    short_link = session.get('short_link')
    if not session_link or not session_uuid:
        # Перенаправляем на главную страницу
        return redirect(url_for('main.home'))

    # Получаем объект текущей сессии
    session_obj = Session.query.filter_by(number=session_link).first()
    if not session_obj:
        # Если сессия не найдена, перенаправляем на главную
        return redirect(url_for('main.home'))

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


@bp.route('/session<path:session_identifier>')
def index(session_identifier):
    if session_identifier == '0':
        session_number = 0
        try:
            if current_user.authenticated:

                return redirect(url_for('main.dashboard', session_identifier=session_identifier))

        except:
            return redirect(url_for('main.login', session_identifier=session_identifier))
    else:
        # Ищем сессию по UUID
        session_obj = Session.query.filter_by(uuid=session_identifier).first()
        if not session_obj:
            return render_template("errors.html")
        
        try:
            if current_user.authenticated:
                return redirect(url_for('main.dashboard', session_identifier=session_identifier))
        except:
            return redirect(url_for('main.login', session_identifier=session_identifier))


@bp.route('/session<path:session_identifier>/login', methods=['GET'])
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


@bp.route('/session<path:session_identifier>/dashboard')
@login_required
def dashboard(session_identifier):
    current_app.logger.debug("====== dashboard =======")
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
        return redirect(url_for('main.login', session_identifier=session_identifier))
    
    if current_user.active and session_obj.id != current_user.session_id:
        # Получаем правильный идентификатор для редиректа
        user_session = Session.query.get(current_user.session_id)
        redirect_id = user_session.uuid if user_session.uuid else user_session.number
        return redirect(url_for('main.dashboard', session_identifier=redirect_id))
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
            logout_link=url_for('main.logout', session_identifier=session_identifier)
        )
    )
    return resp



@bp.route('/session<path:session_identifier>/submit', methods=['POST'])
@login_required
def submit_session(session_identifier):
    current_app.logger.debug(f"====== submit_session =======")
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
    current_app.logger.debug(f"Данные получены от пользователя {username}")
    data_to_socket = defaultdict(dict)

    ALLOWED_TAGS = ["b", "i", "u", "em", "strong", "br", "ul", "ol", "li", "span", "p", "a", "img"]
    # кэш правильных ответов вида { question_id: ['ответ1','ответ2',...] }
    correct_map = get_correct_answers(redis_cache)

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

    emit('answers_post',
                  {'username': username,
                   'questions': dict(data_to_socket),
                   'session_uuid': room_id},
                    namespace='/',
                    room=room_id)
    current_app.logger.debug(f"Выполнен emit в {room_id} от пользователя {username}")
    return jsonify({"status": "ok", "message": "Результаты сохранены"}), 200


@bp.route('/session<path:session_identifier>/logout')
@login_required
def logout(session_identifier):
    current_user.authenticated = False
    db.session.add(current_user)
    db.session.commit()
    response = make_response(redirect(url_for('main.login', session_identifier=session_identifier)))
    response.set_cookie('clear_quiz_data', 'true', max_age=5)  # Кука на 5 секунд
    logout_user()
    return response


@bp.route('/.well-known/appspecific/com.chrome.devtools.json')
def devtools_config():
    # возвращаем 404 без рендеринга шаблона
    return '', 404



