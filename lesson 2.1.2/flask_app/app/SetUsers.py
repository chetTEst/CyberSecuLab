import string
import requests
from .models import db, User, Session, IPs
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
                                            json={"url": f"https://lesson212.kasperstudent.ru/session{session_number}"})
        short_link = short_link_response.json().get("short_url")

        return short_link, session_number



def makeUser(session_number, first_last_name):
    with app.app_context():
        ipIsDDoS = db.session.query(IPs.id).filter(IPs.isDanger == True).all()
        ipNotDDoS = db.session.query(IPs.id).filter(IPs.isDanger == False).all()
        def generate_random_word_with_digits(length):
            with open('word_for_pass.txt') as f:
                word = random.choice(f.readlines()).strip()
                return ''.join([str(session_number)] + list(word) + [random.choice(string.digits) for _ in range(length-len(word))])

        session_obj = db.session.query(Session).filter_by(number=session_number).first()
        username = generate_random_word_with_digits(10)  # 10-character username

        random.shuffle(ipIsDDoS)
        random.shuffle(ipNotDDoS)
        questiosShuffle = ipNotDDoS[:5] + ipIsDDoS[:5]
        random.shuffle(questiosShuffle)
        for idx, question in enumerate(questiosShuffle):
            questiosShuffle[idx] = IPs.query.get(question[0])

        user = User(username=username, first_last_name=first_last_name, session=session_obj,
                    q1=questiosShuffle[0], q2=questiosShuffle[1], q3=questiosShuffle[2], q4=questiosShuffle[3],
                    q5=questiosShuffle[4], q6=questiosShuffle[5], q7=questiosShuffle[6], q8=questiosShuffle[7],
                    q9=questiosShuffle[8], q10=questiosShuffle[9])
        db.session.add(user)
        db.session.commit()

        return username

