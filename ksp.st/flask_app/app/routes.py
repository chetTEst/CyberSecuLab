# routes.py

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

from flask import request, redirect,  jsonify
from . import app
from .models import db, ShortLink
from config import TOKEN_API_KEY

from icecream import ic
ic.disable()


def base62(n):
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base52_string = ''
    while n > 0:
        n, remainder = divmod(n, 62)
        base52_string = chars[remainder] + base52_string
    return base52_string.zfill(4)

def generate_short_id():
    # Get the last short_id from the database
    last_short_id = ShortLink.query.order_by(ShortLink.id.desc()).first()
    if last_short_id:
        last_id = last_short_id.short_id_int
    else:
        last_id = 0

    # Generate the next short_id
    next_id = last_id + 1
    short_id = base62(next_id)

    # Return the new short_id
    return short_id, next_id


@app.route('/api/create/' + TOKEN_API_KEY, methods=['POST'])
def create_short_link():
    data = request.json
    original_url = data.get('url')
    short_id, short_id_int = generate_short_id()
    short_link = ShortLink(short_id=short_id, short_id_int=short_id_int, original_url=original_url)
    db.session.add(short_link)
    db.session.commit()
    return jsonify({"short_url": f"https://ksp.st/{short_id}"})

@app.route('/<short_id>')
def redirect_to_original(short_id):
    short_link = ShortLink.query.filter_by(short_id=short_id).first_or_404()
    return redirect(short_link.original_url)

@app.route('/')
def index():
    return "OK", 200
