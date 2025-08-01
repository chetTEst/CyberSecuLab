import pymysql
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index
from . import db

pymysql.install_as_MySQLdb()


class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=True)

    # def __init__(self, number, id uuid=None):
    #     self.number = number
    #     if number != 0 and uuid is None:  # Для всех сессий кроме 0 генерируем UUID
    #         self.uuid = str(uuid.uuid4())
    #     else:
    #         self.uuid = uuid

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    first_last_name = db.Column(db.String(128), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    session = db.relationship('Session')
    active = db.Column(db.Boolean, default=True)  # Add this
    authenticated = db.Column(db.Boolean, default=False)
    anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_active(self):
        return self.active

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_anonymous(self):
        return self.anonymous

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    qtype = db.Column(db.String(32), nullable=False)
    pool = db.Column(db.Integer, nullable=False, default=1)

class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    question = db.relationship('Question', foreign_keys=[question_id])
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    match_key = db.Column(db.Text, nullable=True)
    order_pos = db.Column(db.Integer, nullable=True)
    plain_values = db.Column(db.Text, nullable=False, default="")

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id])
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    question = db.relationship('Question', foreign_keys=[question_id])
    answered = db.Column(db.Boolean, default=False)
    correct = db.Column(db.Boolean, default=False)
    client_correct = db.Column(db.Boolean, default=False)
    user_response = db.Column(db.Text, nullable=True)


class EssayAnswer(db.Model):
    __tablename__ = 'essay_answers'

    id = db.Column(db.Integer, primary_key=True)
    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    session_id = db.Column(db.Integer, nullable=False)
    # Текст эссе
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)
    # Связи
    user = db.relationship('User', backref=db.backref('essay_answers', lazy='dynamic'))
    question = db.relationship('Question', backref=db.backref('essay_answers', lazy='dynamic'))

    def __repr__(self):
        return (f'<EssayAnswer id={self.id} user={self.user_id} '
                f'question={self.question_id} session={self.session_id}>')

# Индексы для таблицы User
Index('idx_user_username', User.username)
Index('idx_user_session_id', User.session_id)

# Индексы для таблицы Assignment
Index('idx_assignment_user_id', Assignment.user_id)
Index('idx_assignment_question_id', Assignment.question_id)

# Индексы для таблицы Question
Index('idx_question_pool', Question.pool)

# Индексы для таблицы EssayAnswer
Index('idx_essay_user_question', EssayAnswer.user_id, EssayAnswer.question_id)