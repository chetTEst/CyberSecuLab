# -*- coding: utf-8 -*-
import requests
import random
import string
import uuid
from flask import current_app, abort
from .models import User, Session, Assignment
from config import TOKEN_API_KEY, SUBDOMAIN, DOMAIN, RANDOM_IN_VARIANTS
from . import db, redis_cache
from .RedisCacheLib import get_questions_by_pool, get_pool_size

random.seed()

def setUserSession():
    current_app.logger.debug(f"========= setUserSession =========")

    with current_app.app_context():
        session_number = db.session.query(db.func.max(Session.number)).scalar() or 0
        session_number += 1
        session_uuid = str(uuid.uuid4())
        session = Session(number=session_number, uuid=session_uuid)
        current_app.logger.debug(f"Создана сессия {session}")
        db.session.add(session)
        db.session.commit()

        # Создание новой короткой ссылки
        short_link_response = requests.post("https://g2u.run/api/create/" + TOKEN_API_KEY,
                                            json={"url": f"https://{SUBDOMAIN}.{DOMAIN}/session{session_uuid}"})
        short_link = short_link_response.json().get("short_url")

        return short_link, session_number, session_uuid


def _generate_username(session_number: int, length: int = 10) -> str:
    with open('word_for_pass.txt') as f:
        word = random.choice(f.readlines()).strip()
        return ''.join(
            [str(session_number)] + list(word) + [random.choice(string.digits) for _ in range(length - len(word))])


def makeUser(session_number: int, first_last_name: str):
    current_app.logger.debug(f"========= makeUser =========")
    random.seed()
    with current_app.app_context():
        if session_number == 0:
            session_obj = Session.query.filter_by(number=0).first()
        else:
            session_obj = Session.query.filter_by(number=session_number).first()
            current_app.logger.debug(f"Объект сессии {session_obj}")
        if not session_obj:
            current_app.logger.debug("Такой сессии НЕТ!")
            abort(400, "Такой сессии НЕТ!")
        pools = range(1, get_pool_size(redis_cache) + 1)
        username = _generate_username(session_obj.number, 10)
        user = User(username=username, first_last_name=first_last_name, session=session_obj)
        db.session.add(user)
        db.session.flush()
        variant = 0
        q_by_pool = get_questions_by_pool(redis_cache)
        current_app.logger.debug(f"Текущее состояние работы с вариантами RANDOM_IN_VARIANTS  = {RANDOM_IN_VARIANTS}")
        
        if not RANDOM_IN_VARIANTS: variant = random.randint(1, len(q_by_pool.get('1')) + 1)
        for pool in pools:
            q_ids = q_by_pool.get(str(pool))
            if not q_ids:
                continue
            if not RANDOM_IN_VARIANTS:
                q_id = q_ids[variant]
            else:
                q_id = random.choice(q_ids)
            assign = Assignment(user_id=user.id, question_id=q_id)
            db.session.add(assign)

        db.session.commit()
        return username

