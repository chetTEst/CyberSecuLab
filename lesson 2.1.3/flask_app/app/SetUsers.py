import string
import requests
from .models import db, User, Session, Tasks
from . import app
from config import TOKEN_API_KEY, PROD_STATE
import random
from icecream import ic

ic.enable() if not PROD_STATE else ic.disable()


def setUserSession():
    with app.app_context():
        session_number = db.session.query(db.func.max(Session.number)).scalar() or 0
        session_number += 1
        session = Session(number=session_number)
        db.session.add(session)
        db.session.commit()

        # Создание новой короткой ссылки
        short_link_response = requests.post("https://ksp.st/api/create/" + TOKEN_API_KEY,
                                            json={"url": f"https://lesson213.kasperstudent.ru/session{session_number}"})
        short_link = short_link_response.json().get("short_url")

        return short_link, session_number

def makeUser(session_number, first_last_name):
    with app.app_context():
        questions = [db.session.query(Tasks.id).filter(Tasks.number == i).all() for i in range(1, 8)]
        def generate_random_word_with_digits(length):
            with open('word_for_pass.txt') as f:
                word = random.choice(f.readlines()).strip()
                return ''.join([str(session_number)] + list(word) + [random.choice(string.digits) for _ in range(length-len(word))])

        session_obj = db.session.query(Session).filter_by(number=session_number).first()
        username = generate_random_word_with_digits(10)  # 10-character username
        user = User(username=username, first_last_name=first_last_name, session=session_obj,
                    q1=Tasks.query.get(random.choice(questions[0])[0]),
                    q2=Tasks.query.get(random.choice(questions[1])[0]),
                    q3=Tasks.query.get(random.choice(questions[2])[0]),
                    q4=Tasks.query.get(random.choice(questions[3])[0]),
                    q5=Tasks.query.get(random.choice(questions[4])[0]),
                    q6=Tasks.query.get(random.choice(questions[5])[0]),
                    q7=Tasks.query.get(random.choice(questions[6])[0])
                    )
        db.session.add(user)
        db.session.commit()
        # Create a new session in the database (assuming Session model is defined)
        # Pass the logins and passwords to the template
        return username

