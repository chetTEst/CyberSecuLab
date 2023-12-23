# -*- cuding: utf-8 -*-
import random
import base64
from .models import db, Questions
from . import app

random.seed()

def setQuestions():
    def salt_lang(message):
        glasn = 'аеиоуыэюяАЕИОУЫЭЮЯ'
        soglasn = 'бвгджзйклмнпрстфхцчшщ'
        newMesage = ""
        for ch in message:
            if ch in glasn:
                newMesage += ch + "с" + ch
            elif ch == " ":
                newMesage += " "
            else:
                newMesage += ch
        return newMesage

    with app.app_context():
        with open('text_for_tasks_poslovica', encoding='utf-8') as f:
            # Расшифровать Соленый язык
            for line in f.readlines():
                line = line.strip()
                question = Questions(text=salt_lang(line), answer=line)
                db.session.add(question)
            db.session.commit()

with app.app_context():
    if Questions.query.count() == 0:
        setQuestions()



