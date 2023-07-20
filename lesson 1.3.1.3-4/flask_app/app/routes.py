# routes.py
# -*- cuding: utf-8 -*-
import pyotp
import qrcode
import string
import json
from base64 import b64encode
from functools import wraps
from io import BytesIO
from flask import render_template, request, redirect, url_for, flash, send_from_directory, Markup, jsonify, session, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from . import app
from .models import db, User, Session, CipherType, Questions
from .SetUsers import setUserSession
from os import listdir
from config import path
from os.path import join as pjoin
from random import choice, randint

# Route for the homepage with the "Start training" button
@app.route('/')
def home():
    return render_template('home.html')


