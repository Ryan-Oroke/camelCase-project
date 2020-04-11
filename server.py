import os
import hashlib
from typing import NamedTuple

from flask import Flask, render_template, jsonify, abort, request, make_response, url_for, session, send_from_directory, send_file, flash

app = Flask(__name__)
app.secret_key = "Not Random. Oh Noes!"  # This is for metadata encryption (using session)

UPLOAD_DIRECTORY = 'upload_files'  # this is in static so we dont have to write any code to expose files for
                                   # preview. Note: this has a security down side as every file can be accessed.
# The static is implied. You must use url_for('static', filename='...') or an os.path.join('static', ...)
# or would it make sense to have a folder for preview images in static and the full files in UPLOAD_DIRECTORY.


@app.errorhandler(400)
def not_found(error):
    signed_in, cur_user = get_signed_in_info()
    return render_template("400.html", signed_in=signed_in, cur_user=cur_user)


@app.errorhandler(404)  # I don't know if you can do a POST request so I removed all forms from 404.html
def not_found(error):
    signed_in, cur_user = get_signed_in_info()
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
    # Note: session is different for each person who views the website.
    if 'cur_user' in session and session['cur_user'] is not None:
        cur_user = session['cur_user']
        signed_in = True
    else:
        cur_user = ''
        signed_in = False
    return signed_in, cur_user


def get_downloadable_files():
    # TODO: update this, this is all hard coded

    # I thing mongo will store "test_user/P1540913.JPG" for the path and then we need to add the UPLOAD_DIRECTORY part
    # or we could only store "P1540913.JPG" and add UPLOAD_DIRECTORY and user name

    return [file_data_html("test1", 40.015869, -105.279517, "jpg", os.path.join(UPLOAD_DIRECTORY, "test_user/P1540913.JPG").replace('\\', '/'), 100, 12, "abc", "today", "tomorrow", False, "", 0, "test_user"),
            file_data_html("test2", 40.016869, -105.279617, "jpg", os.path.join(UPLOAD_DIRECTORY, "test_user/P1540506.JPG").replace('\\', '/'), 101, 34, "def", "tomorrow", "Mar 3", True, hashlib.sha256("password".encode('utf-8')).hexdigest(), 1, "test_user")]
    # Note, we want to store the path starting in static/ but not including the static part


def handle_login_post():
    # here we check if we are signing in. In the form I set the submit button's name attribute to be `sign_in`
    if 'sign_in' in request.form:  # we assume that username and password have been set
        # In the form there is an input box with the name `username`. The value is then passes in with the POST request.
        username = request.form['username']
        password_plain_text = request.form['password']
        print("username:", username, "password:", password_plain_text)

        # TODO: try login with mongo
        # TODO: is_valid_user = mongoIO.?.try_get_user(..)
        is_valid_user = True

        if is_valid_user:
            # session is how we can store data for a user.
            # it works using cookies allowing the user to not have to re-sign in every time.
            session['cur_user'] = username
            # We use flash to tell the user things
            flash('You were successfully logged in')
        else:
            session['cur_user'] = None
            flash('Logged in failed.')
        return True
    elif 'sign_out' in request.form:
        session['cur_user'] = None
        flash('You were successfully logged out')
        return True
    else:
        return False


# We need to tell flask what to do.
@app.route('/', methods=['GET', 'POST'])
def root_route():
    # if you go to `http://localhost:5000/` this function will be called. Note we would be using the request method GET.
    print("root_route was called with", request.method)  # flask will have print this out
    # GET normally doesn't have any data associated with it.
    # We also need to handle POST.
    if request.method == 'POST':
        # if we are a POST request the data is stored in request.form (try to log in or out).
        print(request.form)
        # A post request is made for us when you have a form in HTML. It will use the name attribute as the key
        # and the value attribute as the value
        # the login form is the same for each page
        handle_login_post()

    # get data from the session
    signed_in, cur_user = get_signed_in_info()

    # we then render the index.html file with the sign in info.
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
    # We only want to allow for upload if the user is signed in
    # TODO: really we should also remove the upload model if we are not signed in
    if signed_in:
        print(request.form)
        # if the form includes a file upload, the data is stored in request.files
        print(request.files)

        if 'input_file' not in request.files or request.files['input_file'].filename == '':
            # flash is how we tell the user things
            flash("No file to upload found")
            return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user)

        # TODO: validate user password

        input_file = request.files['input_file']
        # we store files at `static/UPLOAD_DIRECTORY/<username>/<file>` that's what `file_path` will store
        if not os.path.exists(os.path.join('static', UPLOAD_DIRECTORY, cur_user)):
            os.makedirs(os.path.join('static', UPLOAD_DIRECTORY, cur_user))
        filename = os.path.join(cur_user, input_file.filename)
        file_path = os.path.join('static', UPLOAD_DIRECTORY, filename)

        # We save the file to the file system
        input_file.save(file_path)  # TODO: maybe check if file exists too as to not overwrite
        flash("File uploaded successfully")

        # TODO: add data to mongo (Note we will store filename)

    else:
        flash("You must be signed in to upload files.")
    return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user)


def handle_download_post(signed_in, cur_user, this_file_data, file_data):
    path = this_file_data.path
    password_hash = this_file_data.password_hash
    req_password = this_file_data.req_password

    if req_password:
        input_password = 'password'  # TODO: input_password = request.form['file_password']
        input_password_hash = hashlib.sha256(input_password.encode('utf-8')).hexdigest()
        if input_password_hash != password_hash:
            flash("Incorrect password to download file")
            return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user)

    # print(os.path.join('static', path))
    # send file is how we have the user download the file.
    return send_file(os.path.join('static', path), as_attachment=True)


@app.route('/download', methods=['GET'])
def download_page_get():
    # Note: for GET all we want to do is render the page
    signed_in, cur_user = get_signed_in_info()

    file_data = get_downloadable_files()

    return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user)


@app.route('/download', methods=['POST'])
def download_page_post():
    # The request.form is different depending of which form you submit. You can only submit one at a time.
    print(request.form)
    did_login = handle_login_post()

    # this is not POST specific, but data is still needed in the POST.
    signed_in, cur_user = get_signed_in_info()

    # will call mongo, TODO: pass in current location
    file_data = get_downloadable_files()

    if did_login:
        return render_template("download.html", fils=file_data, signed_in=signed_in, cur_user=cur_user)
    elif 'upload_post' in request.form:
        # This is the form in the upload model
        return handle_upload_post(signed_in, cur_user, file_data)
    else:
        # each download button is its own form with a unique ID
        for this_file_data in file_data:
            if str(this_file_data.id) in request.form:
                print('hit')
                return handle_download_post(signed_in, cur_user, this_file_data, file_data)

    abort(400)  # Bad Request


# IDK what to do with this page
@app.route('/navbar', methods=['GET', 'POST'])
def navbar_page():
    if request.method == 'POST':
        # if the html template does not support flash then nothing will happen
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
    # starts the app
    app.run(threaded=True, host='0.0.0.0', port=5000, debug=True)
