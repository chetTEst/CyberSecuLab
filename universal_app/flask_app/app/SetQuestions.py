from . import app
from .models import db, Question
from .utils import import_gift
from os import environ

GIFT_FILE = environ.get('GIFT_FILE', 'questions.gift')

with app.app_context():
    if Question.query.count() == 0 and GIFT_FILE:
        try:
            import_gift(GIFT_FILE)
        except FileNotFoundError:
            pass
