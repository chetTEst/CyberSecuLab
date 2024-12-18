import requests
import string
from .models import db, User, Session, Questions, Ports
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
                                            json={"url": f"https://lesson132.kasperstudent.ru/session{session_number}"})
        short_link = short_link_response.json().get("short_url")

        return short_link, session_number


def makeUser(session_number, first_last_name):
    with app.app_context():
        questionsNotVirus = db.session.query(Questions.id).filter(Questions.isVirus == False).all()
        questionsIsVirus = db.session.query(Questions.id).filter(Questions.isVirus == True).all()
        questionsNotDangerPort = db.session.query(Ports.id).filter(Ports.isDanger == False).all()
        questionsIsDangerPort = db.session.query(Ports.id).filter(Ports.isDanger == True).all()
        def generate_random_word_with_digits(length):
            with open('word_for_pass.txt') as f:
                word = random.choice(f.readlines()).strip()
                return ''.join([str(session_number)] + list(word) + [random.choice(string.digits) for _ in range(length-len(word))])

        session_obj = db.session.query(Session).filter_by(number=session_number).first()
        username = generate_random_word_with_digits(10)  # 10-character username
        random.shuffle(questionsNotVirus)
        random.shuffle(questionsIsVirus)
        random.shuffle(questionsNotDangerPort)
        random.shuffle(questionsIsDangerPort)
        questiosShuffle = questionsNotVirus[:4] + questionsIsVirus[:4]
        questiosShufflePorts = questionsNotDangerPort[:4] + questionsIsDangerPort[:4]
        random.shuffle(questiosShuffle)
        random.shuffle(questiosShufflePorts)
        for idx, question in enumerate(questiosShuffle):
            questiosShuffle[idx] = Questions.query.get(question[0])
        for idx, port in enumerate(questiosShufflePorts):
            questiosShufflePorts[idx] = Ports.query.get(port[0])

        user = User(username=username, session=session_obj, first_last_name=first_last_name,
                    q1=questiosShuffle[0], q2=questiosShuffle[1], q3=questiosShuffle[2], q4=questiosShuffle[3],
                    q9=questiosShufflePorts[0], q10=questiosShufflePorts[1], q11=questiosShufflePorts[2], q12=questiosShufflePorts[3],
                    q5=questiosShuffle[4], q6=questiosShuffle[5], q7=questiosShuffle[6], q8=questiosShuffle[7],
                    q13=questiosShufflePorts[4], q14=questiosShufflePorts[5], q15=questiosShufflePorts[6], q16=questiosShufflePorts[7])
        db.session.add(user)
        db.session.commit()
        # Create a new session in the database (assuming Session model is defined)
        # Pass the logins and passwords to the template
        return username

