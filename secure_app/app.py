from flask import Flask
import redis
from flask import request, make_response, render_template, send_file, redirect, Response
import sys
import uuid
import requests
from .login import Login
from .register import Register
from .notes import Notes
from datetime import datetime, timedelta
import jwt
import crypt
from flask_pymongo import PyMongo
import random
import string
from functools import wraps

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://user:password@mongodb/db"

mongo = PyMongo(app)
r = redis.Redis(host='db', port=6379, db=0)

register_utils = Register(mongo)
login_utils = Login(r,mongo)
notes_utils = Notes(mongo)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if checkAuth(request.cookies.get('sessionId')) is False:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def checkAuth(sessionId):
    print(sessionId)
    if sessionId is not None and r.hget('sessions', sessionId):
        return True
    return False


@app.route('/')
def index():
    if checkAuth(request.cookies.get('sessionId')):
        exp = datetime.now() + timedelta(minutes = 2)
        current_user = r.hget('sessions', request.cookies.get('sessionId')).decode("utf-8")
        notes_list = notes_utils.get_notes(current_user)
        response = make_response( render_template("menu.html", notes = notes_list), 200)
        return response
    response = make_response(render_template("index.html"), 200)
    return response

@app.route('/login', methods=['POST'])
def login_to_app():
    username = request.form.get('login')
    password = request.form.get('password')
    # if user is not None:
    #     hashed_password = crypt.crypt(password, user.get("salt"))
    #     print(hashed_password, flush=True)
    #     if user.get("hash") == hashed_password:
    #         new_uuid = login_utils.generate_uuid()
    #         r.hset('sessions', new_uuid, username)
    #         response = redirect("/")
    #         response.set_cookie('sessionId', new_uuid, httponly=True)
    #         return response
    if login_utils.login(username, password):        
        new_uuid = login_utils.generate_uuid()
        r.hset('sessions', new_uuid, username)
        response = redirect("/")
        response.set_cookie('sessionId', new_uuid, httponly=True)
        return response
    response = make_response(render_template("index.html", error = "Niepoprawny login lub hasło."), 401)
    return response


@app.route('/logout')
@login_required
def logout():
    r.hdel('sessions', request.cookies.get('sessionId'))
    return redirect("/")


@app.route('/register', methods=['GET'])
def register_screen():   
    response = make_response(render_template("register.html"))
    return response

@app.route('/register', methods=['POST'])
def register():
    registration_status = register_utils.register(request.form)
    if registration_status.get("code") != 201:
        response = make_response(render_template("register.html", error=registration_status.get("status")), registration_status.get("code"))
        return response
    return redirect("/")


@app.route('/changepassword', methods=['GET'])
@login_required
def show_change_password_screen():
    response = make_response(render_template("change_password.html"))
    return response

@app.route('/changepassword', methods=['POST'])
@login_required
def change_password():
    current_user = r.hget('sessions', request.cookies.get('sessionId')).decode("utf-8")
    change_password_status = register_utils.change_password(current_user, request.form)
    if change_password_status.get("code") != 201:
        response = make_response(render_template("change_password.html", error=change_password_status.get("status")), change_password_status.get("code"))
        return response
    return redirect("/")

@app.route('/addnote', methods=['GET'])
@login_required
def show_note_screen():
    users_list = notes_utils.get_users_list()
    print(users_list, flush=True)
    response = make_response(render_template("add_note.html", users=users_list))
    return response

@app.route('/notes', methods=['POST'])
@login_required
def add_note():
    current_user = r.hget('sessions', request.cookies.get('sessionId')).decode("utf-8")
    print(current_user, flush=True)
    adding_status = notes_utils.add_note(request.form, current_user)
    if adding_status.get("code") != 201:
        response = make_response(render_template("add_note.html", error=adding_status.get("status")), adding_status.get("code"))
        return response
    return redirect("/")


@app.route('/notes/<id>', methods=['GET'])
@login_required
def get_note(id):
    mongo.db.note.remove()
    return redirect("/")