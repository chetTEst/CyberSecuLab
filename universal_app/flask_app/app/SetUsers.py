import uuid
import random
from .models import db, User, Question, Assignment
from . import app

random.seed()

def create_session_user(username):
    with app.app_context():
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        return user.id

def assign_random_questions(user_id, count=5):
    with app.app_context():
        q_ids = [q.id for q in Question.query.all()]
        random.shuffle(q_ids)
        for q_id in q_ids[:count]:
            assign = Assignment(user_id=user_id, question_id=q_id)
            db.session.add(assign)
        db.session.commit()

