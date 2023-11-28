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
from flask import render_template, request, redirect, url_for,  jsonify
from flask_login import LoginManager, login_required, current_user
from . import app
from .models import db, User
from .SetUsers import setUserSession
from config import path
from icecream import ic
ic.enable()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    user_id = request.cookies.get('user_id')
    if not user_id:
        # Генерация нового ID и сохранение его в cookie
        user_id = setUserSession()
    if current_user.a1 == False:
        return render_template('502 Bad Gateway.html')
    else:
        return render_template('home.html')


@app.route('/firewall')
@login_required
def firewall(session_number):
    questions = [current_user.q1, current_user.q2, current_user.q3, current_user.q4,
                 current_user.q4, current_user.q6, current_user.q7, current_user.q8]

    # Преобразование вопросов в список словарей
    ports = [{'id': q.id, 'number': q.number, 'about': q.about, 'isDanger': q.isDanger} for q in questions]  # не включаем 'answer'
    # Передача списка в шаблон
    return render_template('firewall.html', logout_link=url_for('logout', session_number=session_number),
                           session_number=session_number,  ports=ports)


@app.route('/check_answer', methods=['POST'])
def check_answer():
    answer = request.json.get('answer')
    if answer == 'a1':
        setattr(current_user, 'a1', True)
        db.session.commit()
        return jsonify({'correct': True})



@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def handle_error(error):
    ic()
    return render_template("errors.html")
