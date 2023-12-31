import random
import string
from werkzeug.security import generate_password_hash
from .models import db, User, Session, Tasks
from flask import Markup
from . import app
from os.path import join
from config import path

def setUserSession(n):
    with app.app_context():
        logins = []
        passwords = []
        # Generate a unique session link
        session_number = db.session.query(db.func.max(Session.number)).scalar() or 0
        session_number += 1
        session = Session(number=session_number)
        db.session.add(session)
        db.session.commit()
        questions = [db.session.query(Tasks.id).filter(Tasks.number == i).all() for i in range(1, 8)]
        def generate_random_word_with_digits(length):
            with open('word_for_pass.txt') as f:
                word = random.choice(f.readlines()).strip()
                return ''.join([str(session_number)] + list(word) + [random.choice(string.digits) for _ in range(length-len(word))])

        session_obj = db.session.query(Session).filter_by(number=session_number).first()
        for i in range(n):
            username = generate_random_word_with_digits(10)  # 10-character username
            password = generate_random_word_with_digits(10)  # 10-character password
            password_hash = generate_password_hash(password)
            user = User(username=username, password=password_hash, session=session_obj,
                        q1=Tasks.query.get(random.choice(questions[0])[0]),
                        q2=Tasks.query.get(random.choice(questions[1])[0]),
                        q3=Tasks.query.get(random.choice(questions[2])[0]),
                        q4=Tasks.query.get(random.choice(questions[3])[0]),
                        q5=Tasks.query.get(random.choice(questions[4])[0]),
                        q6=Tasks.query.get(random.choice(questions[5])[0]),
                        q7=Tasks.query.get(random.choice(questions[6])[0]),
                        )
            db.session.add(user)
            logins.append(username)
            passwords.append(password)
        db.session.commit()
        # Create a new session in the database (assuming Session model is defined)
        # Pass the logins and passwords to the template
        logins_markup = logins
        passwords_markup = passwords
        return (session_number, logins_markup, passwords_markup)

