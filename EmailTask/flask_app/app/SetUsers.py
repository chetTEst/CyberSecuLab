# -*- cuding: utf-8 -*-
import random
from .models import db, User, Emails
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
        questionsNotDangerEmail = ic(db.session.query(Emails.id).filter(
            and_(Emails.isDanger == False,
                 Emails.isSpam == False)).all())
        questionsIsDangerEmail = ic(db.session.query(Emails.id).filter(
            and_(Emails.isDanger == True,
                 Emails.isSpam == False)).all())
        questionsIsSpamEmail = ic(db.session.query(Emails.id).filter(
            and_(Emails.isDanger == False,
                 Emails.isSpam == True)).all())
        random.shuffle(questionsNotDangerEmail)
        random.shuffle(questionsIsDangerEmail)
        random.shuffle(questionsIsSpamEmail)
        questiosShufflePorts = ic(questionsNotDangerEmail[:3] + questionsIsDangerEmail[:3] + questionsIsSpamEmail[:3])
        random.shuffle(ic(questiosShufflePorts))
        for idx, port in enumerate(questiosShufflePorts):
            questiosShufflePorts[idx] = Emails.query.get(port[0])
        user = User(user_id=user_id, flag=random.choice(flags),
                    q1=questiosShufflePorts[0], q2=questiosShufflePorts[1], q3=questiosShufflePorts[2],
                    q4=questiosShufflePorts[3], q5=questiosShufflePorts[4], q6=questiosShufflePorts[5],
                    q7=questiosShufflePorts[6], q8=questiosShufflePorts[7], q9=questiosShufflePorts[8])
        db.session.add(user)
        db.session.commit()
        # Create a new session in the database (assuming Session model is defined)
        # Pass the logins and passwords to the template
        return user_id
