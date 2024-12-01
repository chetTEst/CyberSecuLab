# -*- cuding: utf-8 -*-
import requests
import random
import string
from werkzeug.security import generate_password_hash
from .models import db, User, Session, Questions
from config import TOKEN_API_KEY, PROD_STATE
from . import app

from icecream import ic

ic.enable() if not PROD_STATE else ic.disable()

def setUserSession(part):
    with app.app_context():
        session_number = db.session.query(db.func.max(Session.number)).scalar() or 0
        session_number += 1
        session = Session(number=session_number, part=part)
        db.session.add(session)
        db.session.commit()

        # Создание новой короткой ссылки
        short_link_response = requests.post("https://ksp.st/api/create/" + TOKEN_API_KEY,
                                            json={"url": f"https://lesson13134.kasperstudent.ru/session{session_number}"})
        short_link = short_link_response.json().get("short_url")

        return short_link, session_number





def makeUser(session_number, first_last_name):
    with app.app_context():
        questions = []
        def generate_random_word_with_digits(length):
            with open('word_for_pass.txt') as f:
                word = random.choice(f.readlines()).strip()
                return ''.join([str(session_number)] + list(word) + [random.choice(string.digits) for _ in range(length-len(word))])

        session_obj = db.session.query(Session).filter_by(number=session_number).first()
        part = session_obj.part
        for qn in range(1, 5):
            questions.append(db.session.query(Questions.id).filter(Questions.type == qn+4*part).all())
        username = generate_random_word_with_digits(10)  # 10-character username
        q1 = Questions.query.get(random.choice(questions[0])[0])
        q2 = Questions.query.get(random.choice(questions[1])[0])
        q3 = Questions.query.get(random.choice(questions[2])[0])
        q4 = Questions.query.get(random.choice(questions[3])[0])
        user = User(username=username, first_last_name=first_last_name, session=session_obj,
                    q1=q1, q2=q2, q3=q3, q4=q4)
        db.session.add(user)
        db.session.commit()
        return username
def setUsertStart():
    with app.app_context():
        session_number = db.session.query(db.func.max(Session.number)).scalar() or 0
        session_number += 1
        # Generate a random string of the given length
        def generate_random_string(length):
            return ''.join(random.choice(string.ascii_letters) for _ in range(length))

        # Open a file to write the usernames and passwords
        with open('user_credentials.txt', 'w') as f:
            # Generate 20 users with 'user' role
            username = 'user'  # 10-character username
            password = 'user'  # 10-character password
            password_hash = generate_password_hash(password)
            user = User(username=username, password=password_hash, role=0, session=session_number)
            db.session.add(user)
            for _ in range(20):
                username = generate_random_string(10) # 10-character username
                password = generate_random_string(10) # 10-character password
                password_hash = generate_password_hash(password)
                user = User(username=username, password=password_hash, role=0, session=session_number)
                db.session.add(user)
                # Write the username and password to the file
                f.write(f'{username}:{password}:user\n')

            # Generate 20 users with 'admin' role
            for _ in range(20):
                username = generate_random_string(10) # 10-character username
                password = generate_random_string(10) # 10-character password
                password_hash = generate_password_hash(password)
                user = User(username=username, password=password_hash, role=1, session=session_number)
                db.session.add(user)
                # Write the username and password to the file
                f.write(f'{username}:{password}:admin\n')

        # Commit the changes to the database
        db.session.commit()
