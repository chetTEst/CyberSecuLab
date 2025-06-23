# -*- cuding: utf-8 -*-
import requests
import random
import string
from flask import current_app
from werkzeug.security import generate_password_hash
from .models import db, User, Session, Question, Assignment
from config import TOKEN_API_KEY, PROD_STATE, SUBDOMAIN, DOMAIN
from . import app

random.seed()

from icecream import ic

ic.enable() if not PROD_STATE else ic.disable()
with app.app_context():
    q_by_pool = current_app.config["QUESTIONS_BY_POOL"]


def setUserSession():
    with app.app_context():
        session_number = db.session.query(db.func.max(Session.number)).scalar() or 0
        session_number += 1
        session = Session(number=session_number)
        db.session.add(session)
        db.session.commit()

        # Создание новой короткой ссылки
        short_link_response = requests.post("https://g2u.run/api/create/" + TOKEN_API_KEY,
                                            json={"url": f"https://{SUBDOMAIN}.{DOMAIN}/session{session_number}"})
        short_link = short_link_response.json().get("short_url")

        return short_link, session_number


def _generate_username(session_number: int, length: int = 10) -> str:
    with open('word_for_pass.txt') as f:
        word = random.choice(f.readlines()).strip()
        return ''.join(
            [str(session_number)] + list(word) + [random.choice(string.digits) for _ in range(length - len(word))])


def makeUser(session_number: int, first_last_name: str):
    ic()
    with app.app_context():
        session_obj = Session.query.filter_by(number=session_number).first()
        if not session_obj:
            raise ValueError('session not found')

        pools = range(1, ic(current_app.config['POOL_SIZE']) + 1)
        ic(pools)
        username = _generate_username(session_number, 10)
        user = User(username=username, first_last_name=first_last_name, session=session_obj)
        db.session.add(user)
        db.session.flush()

        for pool in pools:
            q_ids = q_by_pool.get(pool)
            if not q_ids:
                continue
            q_id = random.choice(q_ids)
            assign = Assignment(user_id=user.id, question_id=q_id)
            db.session.add(assign)

        db.session.commit()
        return username

