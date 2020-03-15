# The server written in flask
# I'm going to start and get something like this working:
#       https://blog.learningdollars.com/2019/11/29/how-to-serve-a-reactapp-with-a-flask-server/
# and the post get stuff

import os
import hashlib
from typing import NamedTuple

from flask import Flask, render_template, jsonify, abort, request, make_response, url_for, session, send_from_directory

# from flask_cors import CORS  # is this needed

app = Flask(__name__)
app.secret_key = "Not Random. Oh Noes!"  # This is for metadata encryption (using session)

UPLOAD_DIRECTORY = 'upload_files'


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)


class file_data_html(NamedTuple):
    name: str
    lat: float
    long: float
    format: str
    path: str
    dist: float
    id: int
    description: str
    date: str
    death_date: float
    req_password: bool
    password_hash: str
    num_likes: int
    creator: str


def get_signed_in_info():
    if 'cur_user' in session and session['cur_user'] is not None:
        cur_user = session['cur_user']
        signed_in = True
    else:
        cur_user = ''
        signed_in = False
    return signed_in, cur_user


def get_downloadable_files():

    return [file_data_html("test1", 40.015869, -105.279517, "dick", "test.jpg", 100, 12, "abc", "today", "tomorrow", True, hashlib.sha256("password".encode('utf-8')).hexdigest(), 0, "user1"),
            file_data_html("test2", 40.016869, -105.279617, "dick", "test.jpg", 101, 34, "def", "tomorrow", "Mar 3", True, hashlib.sha256("password1".encode('utf-8')).hexdigest(), 1, "user2")]


def handle_login_post():
    if 'sign_in' in request.form:  # we assume that username and password is there
        username = request.form['username']
        password_plain_text = request.form['password']
        print(username, password_plain_text)

        # try login
        is_valid_user = True

        if is_valid_user:
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


@app.route('/upload', methods=['GET'])
def upload_page_get():
    signed_in, cur_user = get_signed_in_info()

    return render_template("upload.html", signed_in=signed_in, cur_user=cur_user)


@app.route('/upload', methods=['POST'])
def upload_page_post():
    handle_login_post()

    signed_in, cur_user = get_signed_in_info()

    if signed_in:
        print(request.form)
        print(request.files)

        if 'input_file' not in request.files or request.files['input_file'].filename == '':
            return render_template("upload.html", signed_in=signed_in, cur_user=cur_user)  # look into flash

        input_file = request.files['input_file']
        if not os.path.exists(os.path.join(UPLOAD_DIRECTORY, cur_user)):
            os.makedirs(os.path.join(UPLOAD_DIRECTORY, cur_user))
        filename = os.path.join(cur_user, input_file.filename)
        input_file.save(os.path.join(UPLOAD_DIRECTORY, filename))

    return render_template("upload.html", signed_in=signed_in, cur_user=cur_user)


@app.route('/download', methods=['GET'])
def download_page_get():
    signed_in, cur_user = get_signed_in_info()

    test_data = get_downloadable_files()

    return render_template("download.html", fils=test_data, signed_in=signed_in, cur_user=cur_user, failed_password=False)


@app.route('/download', methods=['POST'])
def download_page_post():
    handle_login_post()

    signed_in, cur_user = get_signed_in_info()

    test_data = get_downloadable_files()

    path = ""
    password_hash = None
    req_password = False
    for data in test_data:
        if str(data.id) in request.form:
            path = data.path
            password_hash = data.password_hash
            req_password = data.req_password
            break

    if req_password:
        input_password = 'password'# input_password = request.form['file_password']
        input_password_hash = hashlib.sha256(input_password.encode('utf-8')).hexdigest()
        if input_password_hash != password_hash:
            return render_template("download.html", fils=test_data, signed_in=signed_in, cur_user=cur_user, failed_password=True)

    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


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
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    app.run(threaded=True, host='0.0.0.0', port=5000, debug=True)
