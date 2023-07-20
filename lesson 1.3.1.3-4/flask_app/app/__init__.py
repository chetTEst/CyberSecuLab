# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import path
from os.path import join as pjoin

app = Flask(__name__)
db = SQLAlchemy()

def create_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + pjoin(path, 'tmp', 'lesson.db') #'mysql+pymysql://lesson1311:lesson1311@localhost:33061/lesson1311'
    app.config['SECRET_KEY'] = 'NH}R3Se}X8|"%<8w!!'
    app.config['UPLOAD_FOLDER'] = pjoin(path, 'app', 'files')
    return app

app = create_app()


# Register routes
from . import CreateDb
from . import SetQuestions
from . import routes


# Run the application
if __name__ == '__main__':
    app.run()

