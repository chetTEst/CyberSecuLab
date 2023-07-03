import random
import string
from werkzeug.security import generate_password_hash
from .models import db, User, Session
from flask import Markup
from . import app

def setUserSession(n):
    with app.app_context():
        logins = []
        passwords = []

        # Generate a unique session link
        session_number = db.session.query(db.func.max(Session.number)).scalar() or 0
        session_number += 1
        def generate_random_word_with_digits(length):
            with open('word_for_pass.txt') as f:
                word = random.choice(f.readlines()).strip()
                return ''.join([str(session_number)] + list(word) + [random.choice(string.digits) for _ in range(length-len(word))])
        halfN = n // 2
        for i in range(n):
            if i < halfN:
                role = 0
            else:
                role = 1
            username = generate_random_word_with_digits(10)  # 10-character username
            password = generate_random_word_with_digits(10)  # 10-character password
            password_hash = generate_password_hash(password)
            user = User(username=username, password=password_hash, role=role, session=session_number)
            db.session.add(user)
            logins.append(username)
            passwords.append(password)
        # Create a new session in the database (assuming Session model is defined)
        session = Session(number=session_number)
        db.session.add(session)
        db.session.commit()
        # Pass the logins and passwords to the template
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
