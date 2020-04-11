import os
import hashlib
from typing import NamedTuple

from flask import Flask, render_template, jsonify, abort, request, make_response, url_for, session, send_from_directory, send_file

app = Flask(__name__)
app.secret_key = "Not Random. Oh Noes!"  # This is for metadata encryption (using session)

UPLOAD_DIRECTORY = 'upload_files'  # this is in static so we dont have to write any code to expose files for
                                   # preview. Note: this has a security down side as every file can be accessed.
# The static is implied. You must use url_for('static', filename='...') or an os.path.join('static', ...)
# or would it make sense to have a folder for preview images in static and the full files in UPLOAD_DIRECTORY.


@app.errorhandler(400)
def not_found(error):
    signed_in, cur_user = get_signed_in_info()
    # return make_response(jsonify( { 'error': 'Bad request' } ), 400)  # TODO: make 400.html
    return render_template("400.html", signed_in=signed_in, cur_user=cur_user)


@app.errorhandler(404)
def not_found(error):
    signed_in, cur_user = get_signed_in_info()
    # return make_response(jsonify( { 'error': 'Not found' } ), 404)  # TODO: make 404.html
    return render_template("404.html", signed_in=signed_in, cur_user=cur_user)


class file_data_html(NamedTuple):
    name: str
    lat: float
    long: float
    format: str
    path: str  # a path starting in static/UPLOAD_DIRECTORY
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
    # I thing mongo will store "test_user/P1540913.JPG" for the path and then we need to add the UPLOAD_DIRECTORY part
    # or we could only store "P1540913.JPG" and add UPLOAD_DIRECTORY and user name

    return [file_data_html("test1", 40.015869, -105.279517, "jpg", os.path.join(UPLOAD_DIRECTORY, "test_user/P1540913.JPG").replace('\\', '/'), 100, 12, "abc", "today", "tomorrow", False, "", 0, "test_user"),
            file_data_html("test2", 40.016869, -105.279617, "jpg", os.path.join(UPLOAD_DIRECTORY, "test_user/P1540506.JPG").replace('\\', '/'), 101, 34, "def", "tomorrow", "Mar 3", True, hashlib.sha256("password".encode('utf-8')).hexdigest(), 1, "test_user")]
    # Note, we want to store the path starting in static/ but not including the static part


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
        return True
    elif 'sign_out' in request.form:
        session['cur_user'] = None
        return True
    else:
        return False


@app.route('/', methods=['GET', 'POST'])
def root_route():
    if request.method == 'POST':
        handle_login_post()

    signed_in, cur_user = get_signed_in_info()

    return render_template("index.html", signed_in=signed_in, cur_user=cur_user)


"""
@app.route('/upload', methods=['GET'])
def upload_page_get():
    signed_in, cur_user = get_signed_in_info()

    return render_template("upload.html", signed_in=signed_in, cur_user=cur_user)


@app.route('/upload', methods=['POST'])  # TODO: move to
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
"""


def handle_upload_post(signed_in, cur_user, file_data):
    if signed_in:  # have a better else
        print(request.form)
        print(request.files)

        if 'input_file' not in request.files or request.files['input_file'].filename == '':
            return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user, failed_password=False)  # look into flash

        # TODO: validate user password
        input_file = request.files['input_file']
        if not os.path.exists(os.path.join(UPLOAD_DIRECTORY, cur_user)):
            os.makedirs(os.path.join(UPLOAD_DIRECTORY, cur_user))
        filename = os.path.join(cur_user, input_file.filename)
        file_path = os.path.join('static', UPLOAD_DIRECTORY, filename)
        input_file.save(file_path)  # maybe check if file exists too
        # TODO: add data to mongo (Note we will store filename)

    return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user, failed_password=False)


def handle_download_post(signed_in, cur_user, this_file_data, file_data):
    path = this_file_data.path
    password_hash = this_file_data.password_hash
    req_password = this_file_data.req_password

    if req_password:
        input_password = 'password'  # input_password = request.form['file_password']
        input_password_hash = hashlib.sha256(input_password.encode('utf-8')).hexdigest()
        if input_password_hash != password_hash:
            return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user,
                                   failed_password=True)
    # print(os.path.join('static', path))
    return send_file(os.path.join('static', path), as_attachment=True)


@app.route('/download', methods=['GET'])
def download_page_get():
    signed_in, cur_user = get_signed_in_info()

    file_data = get_downloadable_files()

    return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user,
                           failed_password=False)


@app.route('/download', methods=['POST'])
def download_page_post():
    print(request.form)
    did_login = handle_login_post()

    signed_in, cur_user = get_signed_in_info()

    file_data = get_downloadable_files()

    if did_login:
        return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user,
                               failed_password=False)
    elif 'upload_post' in request.form:
        return handle_upload_post(signed_in, cur_user, file_data)
    else:
        for this_file_data in file_data:
            if str(this_file_data.id) in request.form:
                print('hit')
                return handle_download_post(signed_in, cur_user, this_file_data, file_data)

    abort(400)
    # return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user,
    #                       failed_password=False)


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


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        if handle_login_post():
            pass
        elif 'sign_up' in request.form:
            print(request.form)
            pass  # I think all we need to do is pass the data to mongo
            # should we sign the user in for them or not

    signed_in, cur_user = get_signed_in_info()

    return render_template("register.html", signed_in=signed_in, cur_user=cur_user)


if __name__ == "__main__":
    up_path = os.path.join('static', UPLOAD_DIRECTORY)
    if not os.path.exists(up_path):
        os.makedirs(up_path)
    app.run(threaded=True, host='0.0.0.0', port=5000, debug=True)
