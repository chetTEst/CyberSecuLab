# __init__.py

'''
Welcome to the open-source file for the "Automatic Security Training and Testing System"
developed by Alexey Chetverov. This application aims to provide a robust tool for learning
and enhancing cybersecurity skills.

The system presented in this repository is designed to facilitate the process of education,
self-assessment, and comprehensive exploration of various aspects of cybersecurity. Users
will be able to utilize its functionalities to train their skills, test their knowledge, and
delve into different cybersecurity domains.

One of the unique features of this project is its licensing under Apache 2.0.
This means that users have the right to copy and distribute the software while preserving
the author's copyright. The open-source nature of the code allows the community to contribute
to the project's development, enhance its functionalities, and address potential issues.

We invite all interested individuals to join this exciting endeavor and contribute to the
growth of a tool that can make the world of cybersecurity even more reliable and secure.
Your ideas, feedback, and suggestions are warmly welcomed as they will help us improve
this experience further.

Thank you for your interest in this project, and we hope that this system will become
a valuable asset for anyone seeking to ensure data and information security in the modern
digital landscape.'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import path, db_host, db_port, db_user, db_pass, db_name, TOKEN_API_KEY
from os.path import join as pjoin
from os import environ
from icecream import ic
ic.disable()

app = Flask(__name__)
db = SQLAlchemy()

def create_app():
    if environ.get('FLASK_DEBUG') == 'production':
        # Запущено через wsgi
        app.config['SQLALCHEMY_DATABASE_URI'] = ic(f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}')
    else:
        # Запущено через run.py
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + pjoin(path, 'tmp', 'lesson.db')
    app.config['SECRET_KEY'] = 'NH}R3Se}X8|"%<8w'
    return app

app = create_app()


# Register routes
from . import CreateDb
from . import routes



# Run the application
if __name__ == '__main__':
    app.run()

