import random
import base64
from .models import db, IPs
from . import app


random.seed()

def setIPnumber():
    return ".".join([str(random.randint(20, 170)) for _ in range(4)])

def setIPs():

    with app.app_context():
        if IPs.query.count() == 0:
            for i in range(20):
                number = setIPnumber()
                value = random.randint(50, 80)
                question = IPs(number=number, value=value)
                db.session.add(question)
            db.session.commit()
            for i in range(20):
                number = setIPnumber()
                value = random.randint(60, 90)
                question = IPs(number=number, value=value, isDanger=True)
                db.session.add(question)
            db.session.commit()


setIPs()
