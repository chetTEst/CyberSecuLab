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
from flask import render_template, request, redirect, url_for, jsonify, make_response
from flask_login import LoginManager, login_required, current_user, login_user
from . import app
from .models import db, User
from .SetUsers import setUserSession
import hashlib
from config import path
from icecream import ic

ic.disable()

login_manager = LoginManager()
login_manager.init_app(app)

data_for_text = [
    "Иррациональное число, иcходя из того, что категорически притягивает многомерный кризис, тем не менее как только ортодоксальность окончательно возобладает, даже эта маленькая лазейка будет закрыта. Дело в том, что критерий интегрируемости изменяем. Дифференциальное уравнение мгновенно.",
    "Нормальное распределение осознаёт анормальный кризис. Постоянная величина непоследовательно создает критерий интегрируемости. Неравенство Бернулли оправдывает аутотренинг. Согласно последним исследованиям, страх проецирует минимум. Линейное программирование самопроизвольно.",
    "Доказательство отображает гештальт. Показательный пример –  сновидение монотонно. Этот концепт элиминирует концепт «нормального», однако линейное программирование вызывает максимум, и это неудивительно, если речь о персонифицированном характере первичной социализации. Восприятие, конечно, необходимо и достаточно."
    ]


def generate_hash(value, salt):
    return hashlib.sha256((str(value) + salt).encode()).hexdigest()


def split_user_id(user_id):
    return [user_id[i:i + len(user_id) // 16] for i in range(0, len(user_id), len(user_id) // 16)]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    user_id = request.cookies.get('user_id')
    if not user_id:
        # Генерация нового ID и сохранение его в cookie
        user_id = setUserSession()
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(user_id=user_id).first()
        login_user(user, remember=remember)
        response = make_response(render_template('502 Bad Gateway.html'))
        response.set_cookie('user_id', user_id, max_age=60 * 60 * 24 * 1)
        return response
    if current_user.a1 == False:
        return render_template('502 Bad Gateway.html')
    else:
        secret_code = current_user.flag.strip()
        parts = [secret_code[i:i + len(secret_code) // 4] for i in range(0, len(secret_code), len(secret_code) // 4)]
        return render_template('home.html', parts=parts,
                               content_paragraph_1=data_for_text[0],
                               content_paragraph_2=data_for_text[1],
                               content_paragraph_3=data_for_text[2])


@app.route('/firewall')
@login_required
def firewall():
    questions = [current_user.q1, current_user.q2, current_user.q3, current_user.q4,
                 current_user.q5, current_user.q6, current_user.q7, current_user.q8]
    salts = split_user_id(current_user.user_id)
    # Преобразование вопросов в список словарей
    ports = [{'id': q.id, 'number': q.number, 'about': q.about, 'isDanger': generate_hash(q.isDanger, salts[idx * 2]),
              'isAnswer': generate_hash(q.isAnswer, salts[idx * 2 + 1])} for idx, q in enumerate(questions)]
    # Передача списка в шаблон
    return render_template('firewall.html', ports=ports, user_id=current_user.user_id)


@app.route('/check_answer', methods=['POST'])
@login_required
def check_answer():
    user_id = request.json.get('user_id')
    if user_id == current_user.user_id:
        setattr(current_user, 'a1', True)
        db.session.commit()
        return jsonify({'correct': True})


@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def handle_error(error):
    ic(error)
    return render_template("errors.html")
