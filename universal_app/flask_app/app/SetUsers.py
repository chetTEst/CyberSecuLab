import random
import string
from .models import db, User, Session, Question, Assignment
from . import app

random.seed()

def set_user_session(part: int):
    with app.app_context():
        number = db.session.query(db.func.max(Session.number)).scalar() or 0
        number += 1
        session = Session(number=number, part=part)
        db.session.add(session)
        db.session.commit()
        return number

def _generate_username(length: int) -> str:
    letters = string.ascii_lowercase
    digits = string.digits
    word = ''.join(random.choice(letters) for _ in range(length - 3))
    return word + ''.join(random.choice(digits) for _ in range(3))

def make_user(session_number: int, first_last_name: str):
    with app.app_context():
        session_obj = Session.query.filter_by(number=session_number).first()
        if not session_obj:
            raise ValueError('session not found')

        pools = sorted({q.pool for q in Question.query.all()})
        username = _generate_username(10)
        user = User(username=username, first_last_name=first_last_name, session=session_obj)
        db.session.add(user)
        db.session.flush()

        for pool in pools:
            q_ids = [q.id for q in Question.query.filter_by(pool=pool).all()]
            if not q_ids:
                continue
            q_id = random.choice(q_ids)
            assign = Assignment(user_id=user.id, question_id=q_id)
            db.session.add(assign)

        db.session.commit()
        return username

