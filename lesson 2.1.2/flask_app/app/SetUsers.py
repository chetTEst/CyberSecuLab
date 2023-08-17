import random
import string
from werkzeug.security import generate_password_hash
from .models import db, User, Session, IPs
from flask import Markup
from . import app

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
        ipIsDDoS = db.session.query(IPs.id).filter(IPs.isDanger == True).all()
        ipNotDDoS = db.session.query(IPs.id).filter(IPs.isDanger == False).all()
        def generate_random_word_with_digits(length):
            with open('word_for_pass.txt') as f:
                word = random.choice(f.readlines()).strip()
                return ''.join([str(session_number)] + list(word) + [random.choice(string.digits) for _ in range(length-len(word))])

        session_obj = db.session.query(Session).filter_by(number=session_number).first()
        for i in range(n):
            username = generate_random_word_with_digits(10)  # 10-character username
            password = generate_random_word_with_digits(10)  # 10-character password
            password_hash = generate_password_hash(password)
            random.shuffle(ipIsDDoS)
            random.shuffle(ipNotDDoS)
            questiosShuffle = ipNotDDoS[:5] + ipIsDDoS[:5]
            random.shuffle(questiosShuffle)
            for idx, question in enumerate(questiosShuffle):
                questiosShuffle[idx] = IPs.query.get(question[0])

            user = User(username=username, password=password_hash, session=session_obj,
                        q1=questiosShuffle[0], q2=questiosShuffle[1], q3=questiosShuffle[2], q4=questiosShuffle[3],
                        q5=questiosShuffle[4], q6=questiosShuffle[5], q7=questiosShuffle[6], q8=questiosShuffle[7],
                        q9=questiosShuffle[8], q10=questiosShuffle[9])
            db.session.add(user)
            logins.append(username)
            passwords.append(password)
        db.session.commit()
        # Create a new session in the database (assuming Session model is defined)
        # Pass the logins and passwords to the template
        logins_markup = logins
        passwords_markup = passwords
        return (session_number, logins_markup, passwords_markup)

