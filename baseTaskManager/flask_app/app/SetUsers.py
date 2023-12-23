# -*- cuding: utf-8 -*-
import random
from .models import db, User, Ports
from . import app
from sqlalchemy import and_
import uuid
from icecream import ic
ic.disable()


def setUserSession():
    user_id = str(uuid.uuid4())
    with open('flags') as file:
        flags = file.readlines()
    with app.app_context():
        # Generate a unique session link
        questionsNotDangerPort = ic(db.session.query(Ports.id).filter(
            and_(Ports.isDanger == False,
                 Ports.isAnswer == False)).all())
        questionsIsDangerPort = ic(db.session.query(Ports.id).filter(
            and_(Ports.isDanger == True,
                 Ports.isAnswer == False)).all())
        random.shuffle(questionsNotDangerPort)
        random.shuffle(questionsIsDangerPort)
        questionsIsAnswer = db.session.query(Ports.id).filter(Ports.isAnswer == True).all()
        questiosShufflePorts = ic(questionsNotDangerPort[:3] + questionsIsDangerPort[:3] + questionsIsAnswer)
        random.shuffle(ic(questiosShufflePorts))
        for idx, port in enumerate(questiosShufflePorts):
            questiosShufflePorts[idx] = Ports.query.get(port[0])
        user = User(user_id=user_id, flag=random.choice(flags),
                    q1=questiosShufflePorts[0], q2=questiosShufflePorts[1], q3=questiosShufflePorts[2],
                    q4=questiosShufflePorts[3],
                    q5=questiosShufflePorts[4], q6=questiosShufflePorts[5], q7=questiosShufflePorts[6],
                    q8=questiosShufflePorts[7])
        db.session.add(user)
        db.session.commit()
        # Create a new session in the database (assuming Session model is defined)
        # Pass the logins and passwords to the template
        return user_id
