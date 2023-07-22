# -*- cuding: utf-8 -*-
import random
import string
from werkzeug.security import generate_password_hash
from .models import db, User, Session, Questions
from flask import Markup
from . import app

def setUserSession(n, part):
    with app.app_context():
        logins = []
        passwords = []
        questions = []
        for qn in range(1, 5):
            questions.append(db.session.query(Questions.id).filter(Questions.type == qn+4*part).all())
        # Generate a unique session link
        session_number = db.session.query(db.func.max(Session.number)).scalar() or 0
        session_number += 1
        session = Session(number=session_number)
        db.session.add(session)
        db.session.commit()
        def generate_random_word_with_digits(length):
            with open('word_for_pass.txt') as f:
                word = random.choice(f.readlines()).strip()
                return ''.join([str(session_number)] + list(word) + [random.choice(string.digits) for _ in range(length-len(word))])
        for i in range(n):
            username = generate_random_word_with_digits(10)  # 10-character username
            password = generate_random_word_with_digits(10)  # 10-character password
            password_hash = generate_password_hash(password)
            q1 = Questions.query.get(random.choice(questions[0])[0])
            q2 = Questions.query.get(random.choice(questions[1])[0])
            q3 = Questions.query.get(random.choice(questions[2])[0])
            q4 = Questions.query.get(random.choice(questions[3])[0])
            session_obj = Session.query.get(session_number)
            user = User(username=username, password=password_hash, session=session_obj,
                        q1=q1, q2=q2, q3=q3, q4=q4)
            db.session.add(user)
            logins.append(username)
            passwords.append(password)
        # Create a new session in the database (assuming Session model is defined)
        # Pass the logins and passwords to the template
        db.session.commit()
        logins_markup = logins
        passwords_markup = passwords
        return (session_number, logins_markup, passwords_markup)
def setUsertStart():
    with app.app_context():
        session_number = db.session.query(db.func.max(Session.number)).scalar() or 0
        session_number += 1
        print(session_number)
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
