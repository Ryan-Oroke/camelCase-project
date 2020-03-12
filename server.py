# The server written in flask
# I'm going to start and get something like this working:
#       https://blog.learningdollars.com/2019/11/29/how-to-serve-a-reactapp-with-a-flask-server/
# and the post get stuff

import os
from typing import NamedTuple

from flask import Flask, render_template, jsonify, abort, request, make_response, url_for, session

# from flask_cors import CORS  # is this needed

app = Flask(__name__)
app.secret_key = "Not Random. Oh Noes!"  # This is for metadata encryption

# CORS(app)


class file_data_html(NamedTuple):
    name: str
    lat: float
    long: float
    format: str
    path: str
    dist: float
    id: int


def get_signed_in_info():
    if 'cur_user' in session and session['cur_user'] is not None:
        cur_user = session['cur_user']
        signed_in = True
    else:
        cur_user = ''
        signed_in = False
    return signed_in, cur_user


def handle_login_post():
    if 'sign_in' in request.form:  # we assume that username and password is there
        username = request.form['username']
        password_plain_text = request.form['password']
        print(username, password_plain_text)

        # try login
        is_valid_user = True

        if True:
            session['cur_user'] = username
        else:
            session['cur_user'] = None

    elif 'sign_out' in request.form:
        session['cur_user'] = None


@app.route('/', methods=['GET', 'POST'])
def root_route():
    if request.method == 'POST':
        handle_login_post()

    signed_in, cur_user = get_signed_in_info()

    return render_template("index.html", signed_in=signed_in, cur_user=cur_user)


@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        handle_login_post()

    signed_in, cur_user = get_signed_in_info()

    return render_template("upload.html", signed_in=signed_in, cur_user=cur_user)


@app.route('/download', methods=['GET', 'POST'])
def download_page():
    if request.method == 'POST':
        handle_login_post()

    signed_in, cur_user = get_signed_in_info()

    test_data = [file_data_html("test1", 40.015869, -105.279517, "dick", "123", 100, 12), file_data_html("test2", 40.016869, -105.279617, "dick", "123", 101, 34)]

    return render_template("download.html", fils=test_data, signed_in=signed_in, cur_user=cur_user)


@app.route('/navbar', methods=['GET', 'POST'])
def navbar_page():
    if request.method == 'POST':
        handle_login_post()

    signed_in, cur_user = get_signed_in_info()

    return render_template("navbar.html", signed_in=signed_in, cur_user=cur_user)


@app.route('/about', methods=['GET', 'POST'])
def about_page():
    if request.method == 'POST':
        handle_login_post()

    signed_in, cur_user = get_signed_in_info()

    return render_template("about.html", signed_in=signed_in, cur_user=cur_user)


if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', port=5000, debug=True)
