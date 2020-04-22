import os
import hashlib
from typing import NamedTuple
import time
import datetime

import mongoIO

from flask import Flask, render_template, jsonify, abort, request, make_response, url_for, session, send_from_directory, flash, send_file, redirect

app = Flask(__name__)
app.secret_key = "Not Random. Oh Noes!"  # This is for metadata encryption (using session)

UPLOAD_DIRECTORY = 'upload_files'  # this is in static so we dont have to write any code to expose files for
                                   # preview. Note: this has a security down side as every file can be accessed.
# The static is implied. You must use url_for('static', filename='...') or an os.path.join('static', ...)
# or would it make sense to have a folder for preview images in static and the full files in UPLOAD_DIRECTORY.

# db_info = mongoIO.DB_info("localhost", 27017, "FreeDrop", "file_data", "user_data")  # should we make a new connection for each user
# db_info.connect()


client = pymongo.MongoClient("mongodb+srv://admin:ryanisadmin@freedropcluster-quzgv.mongodb.net/test?retryWrites=true&w=majority")
db = client.test



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
    id: str
    description: str
    date: str
    death_date: str
    req_password: bool
    password_hash: str
    num_likes: int
    creator: str
    downloads: float


def get_signed_in_info():
    # Note: session is different for each person who views the website.
    if 'cur_user' in session and session['cur_user'] is not None:
        cur_user = session['cur_user']
        signed_in = True
    else:
        cur_user = ''
        signed_in = False
    return signed_in, cur_user


def get_downloadable_files(lat, long):
    # I thing mongo will store "test_user/P1540913.JPG" for the path and then we need to add the UPLOAD_DIRECTORY part

    """
    # The files can be found at https://drive.google.com/file/d/1obNPWyEka1e1D4-jvuvVS3x3gegCDf_x/view?usp=sharing
    # just put the unzipped file into the static file
    return [file_data_html("test1", 40.015869, -105.279517, "jpg",
                           os.path.join(UPLOAD_DIRECTORY, "test_user/P1540913.JPG").replace('\\', '/'), 100, 12, "abc",
                           "today", "tomorrow", False, "", 0, "test_user", 420),
            file_data_html("test2", 40.016869, -105.278617, "jpg",
                           os.path.join(UPLOAD_DIRECTORY, "test_user/P1540506.JPG").replace('\\', '/'), 101, 34, "def",
                           "tomorrow", "Mar 3", False, hashlib.sha256("password".encode('utf-8')).hexdigest(), 1,
                           "test_user", 69),
            file_data_html("test3", 40.017869, -105.275517, "jpg",
                           os.path.join(UPLOAD_DIRECTORY, "test_user/P1540915.JPG").replace('\\', '/'), 100, 56, "111",
                           "today", "tomorrow", False, hashlib.sha256("password".encode('utf-8')).hexdigest(), 0,
                           "test_user", 1),
            file_data_html("test4", 40.014869, -105.276617, "pdf",
                           os.path.join(UPLOAD_DIRECTORY, "test_user/test_pdf.pdf").replace('\\', '/'), 101, 78, "222",
                           "tomorrow", "Mar 3", False, hashlib.sha256("password".encode('utf-8')).hexdigest(), 1,
                           "test_user", 2),
            file_data_html("test5", 40.013869, -105.277617, "jpg",
                           os.path.join(UPLOAD_DIRECTORY, "test_user/LkgdAgN.jpg").replace('\\', '/'), 101, 90, "333",
                           "tomorrow", "Mar 3", True, hashlib.sha256("password".encode('utf-8')).hexdigest(), 1,
                           "test_user", 3)]
    # Note, we want to store the path starting in `static/` but it is not including the path
    """

    mongo_data = db_info.get_all_files_in_range(float(lat), float(long), 0.1, 20)  # TODO: change range

    data = [file_data_html(mfd['file_name'], mfd['gps_lat'], mfd['gps_long'],
                           os.path.splitext(mfd['file_path'])[1].lstrip('.'),
                           os.path.join(UPLOAD_DIRECTORY, mfd['file_path']).replace('\\', '/'), mfd['vis_dist'],
                           str(mfd['_id']), mfd['file_description'],
                           time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mfd['file_create_time'])),
                           time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((mfd['file_create_time'] + mfd['vis_time']))),
                           mfd['file_req_password'],
                           mfd['file_password_hash'], mfd['num_likes'], mfd['creator_name'], mfd['num_downloads'])
            for mfd in mongo_data]
    # print(data)
    return data


def get_search_files(lat, long, key):

    mongo_data = db_info.get_all_searchable_files(float(lat), float(long), 0.1, 20, key)  # TODO: change range

    data = [file_data_html(mfd['file_name'], mfd['gps_lat'], mfd['gps_long'],
                           os.path.splitext(mfd['file_path'])[1].lstrip('.'),
                           os.path.join(UPLOAD_DIRECTORY, mfd['file_path']).replace('\\', '/'), mfd['vis_dist'],
                           str(mfd['_id']), mfd['file_description'],
                           time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mfd['file_create_time'])),
                           time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((mfd['file_create_time'] + mfd['vis_time']))),
                           mfd['file_req_password'],
                           mfd['file_password_hash'], mfd['num_likes'], mfd['creator_name'], mfd['num_downloads'])
            for mfd in mongo_data ]
    # print(data)

    if data == []:
        flash("No files were found using the given keywords. Please change the search criteria and try again.");
    return data


def handle_login_post():
    # here we check if we are signing in. In the form I set the submit button's name attribute to be `sign_in`
    if 'sign_in' in request.form:  # we assume that username and password have been set
        # In the form there is an input box with the name `username`. The value is then passed in with the POST request.
        username_or_email = request.form['username']  # Note this could also be an email
        password_plain_text = request.form['password']
        print("username:", username_or_email, "password:", password_plain_text)

        res = db_info.try_get_user(username_or_email, password_plain_text)
        if res is not None:
            username = res['user_name']  # if you sign in with email
            is_valid_user = True
            # should we store more info about user in session?
        else:
            is_valid_user = False

        if is_valid_user:
            # session is how we can store data for a user.
            # it works using cookies allowing the user to not have to re-sign in every time.
            session['cur_user'] = username
            # We use flash to tell the user things
            # flash('You were successfully logged in')
        else:
            session['cur_user'] = None
            flash('Log in failed, username or password is incorrect.')
        return True
    elif 'sign_out' in request.form:
        session['cur_user'] = None
        # flash('You were successfully logged out')
        return True
    else:
        return False


# this is an example, it is not intended to be used for the website
# We need to tell flask what to do when the route `/test_example` receives a request
@app.route('/test_example', methods=['GET', 'POST'])
def test_example_route():
    # if you go to `http://localhost:5000/test_example` this function will be called.
    # Note, when you view you would be using the request method GET.
    print("test_example_route was called with", request.method)  # flask will have print this out
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

    # we then render the `index.html` file with the sign in info.
    return render_template("index.html", signed_in=signed_in, cur_user=cur_user)


def handle_upload_post(signed_in, cur_user, file_data, search_str):
    # We only want to allow for upload if the user is signed in
    # DONE: really we should also remove the upload model if we are not signed in
    if signed_in:
        print(request.form)
        # if the form includes a file upload, the data is stored in `request.files`
        print(request.files)

        if 'input_file' not in request.files or request.files['input_file'].filename == '':
            # flash is how we tell the user things
            flash("No file found for uploading. Please select a file.")
            return render_template("map.html", fils=file_data, signed_in=signed_in, cur_user=cur_user, searchstr=search_str)

        res = db_info.try_get_user(cur_user, request.form['user_password'])
        if res is not None:
            input_file = request.files['input_file']
            # we store files at `static/UPLOAD_DIRECTORY/<username>/<file>` that's what `file_path` will store
            if not os.path.exists(os.path.join('static', UPLOAD_DIRECTORY, cur_user)):
                os.makedirs(os.path.join('static', UPLOAD_DIRECTORY, cur_user))
            filename = os.path.join(cur_user, input_file.filename)
            file_path = os.path.join('static', UPLOAD_DIRECTORY, filename)

            # We save the file to the file system
            if not os.path.exists(os.path.join('static', UPLOAD_DIRECTORY, filename)):
                input_file.save(file_path)  # DONE: maybe check if file exists too as to not overwrite

                req_pass = False
                pass_hash = ''
                if request.form['file_password'] != '':
                    req_pass = True
                    pass_hash = hashlib.sha256(request.form['file_password'].encode('utf-8')).hexdigest()

                print("Test" + request.form['gps_lat'])

                ret = db_info.ins_file(mongoIO.file_data_entry(session['cur_user'], request.form['inputFileName'],
                                                            request.form['inputFileDescription'], time.time(), filename,
                                                            req_pass, pass_hash, float(request.form['gps_lat']),
                                                            float(request.form['gps_long']),
                                                            float(request.form['visibleDistance']),
                                                            10000000.0, 0, 0))

                flash("File uploaded successfully") # check rets of `.save` and `.ins_file`

            else:
                flash("File has already been uploaded!");
        else:
            flash("The password you entered is incorrect.")
    else:
        flash("You must be signed in to upload files.")
    return render_template("map.html", fils=file_data, signed_in=signed_in, cur_user=cur_user, searchstr=search_str)


def handle_download_post(signed_in, cur_user, this_file_data, file_data, search_str):
    path = this_file_data.path
    password_hash = this_file_data.password_hash
    req_password = this_file_data.req_password

    if req_password:
        input_password = request.form['file_password']
        input_password_hash = hashlib.sha256(input_password.encode('utf-8')).hexdigest()
        if input_password_hash != password_hash:
            flash("Incorrect password to download file")
            return render_template("map.html", fils=file_data, signed_in=signed_in, cur_user=cur_user, searchstr=search_str)
    # print(os.path.join('static', path))
    # send file is how we have the user download the file.
    return send_file(os.path.join('static', path), as_attachment=True)


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
            res = db_info.try_create_user(request.form['username'], request.form['password'], 'first name', 'last name', request.form['email'])
            if res is None:
                flash("Failed to create user, username or email might be taken.")
            else:
                flash("User created successfully.")
                # should we sign the user in for them or not

    signed_in, cur_user = get_signed_in_info()

    return render_template("register.html", signed_in=signed_in, cur_user=cur_user)


@app.route('/', methods=['GET'])
def map_page_get():
    # We don't really care about GET here
    signed_in, cur_user = get_signed_in_info()
    
    # test.html will get location data and then send a POST to `/`
    # thus we will call `map_page_post`
    return render_template("auto_submit.html", signed_in=signed_in, cur_user=cur_user)


def get_lat_long():
    if 'auto_sub_hidden' in request.form or 'auto_sub_button' in request.form:
        lat = request.form['gps_lat']
        long = request.form['gps_long']
        session['cur_lat'] = lat
        session['cur_long'] = long
        res = True
        return lat, long, res
    elif 'cur_lat' in session:
        lat = session['cur_lat']
        long = session['cur_long']
        res = False
        return lat, long, res
    else:
        lat = 0
        long = 0
        res = False
        return lat, long, res


@app.route('/', methods=['POST'])
def map_page_post():
    # The request.form is different depending of which form you submit. You can only submit one at a time.
    print(request.form)
    did_login = handle_login_post()

    lat, long, did_lat_long_post = get_lat_long()

    # this is not POST specific, but data is still needed in the POST.
    signed_in, cur_user = get_signed_in_info()

    search_str = request.args.get('searchstr')
    print(search_str)

    # will call mongo to get files
    if search_str is None:
        search_str = ''
        file_data = get_downloadable_files(lat, long)
    else:
        file_data = get_search_files(lat, long, search_str)


    flash("Page Refreshed Successfully")
    
    if did_login or did_lat_long_post:
        # all rendering of `map.html` is done in this post
        return render_template("map.html", fils=file_data, signed_in=signed_in, cur_user=cur_user, searchstr=search_str)
    elif 'upload_post' in request.form:
        # This is the form in the upload model
        return handle_upload_post(signed_in, cur_user, file_data, search_str)
    elif 'search_post' in request.form:
        #This is the search button on the main page
        #file_data = get_search_files(lat, long, request.form['searchTextBox'])
        #return render_template("map.html", fils=file_data, signed_in=signed_in, cur_user=cur_user)
        return redirect(url_for('map_page_post', searchstr=request.form['searchTextBox']))
    else:
        # each download button is its own form with a unique ID
        for this_file_data in file_data:
            if str(this_file_data.id) in request.form:
                print('hit')
                return handle_download_post(signed_in, cur_user, this_file_data, file_data, search_str)

    abort(400)  # Bad Request


@app.route('/user', methods=['GET'])
def user_page_get():
    signed_in, cur_user = get_signed_in_info()

    if not signed_in:
        return redirect(url_for('register_page'))

    return render_template("user.html", signed_in=signed_in, cur_user=cur_user)


@app.route('/user', methods=['POST'])
def user_page_post():
    handle_login_post()

    signed_in, cur_user = get_signed_in_info()

    if not signed_in:
        return redirect(url_for('register_page'))

    return render_template("user.html", signed_in=signed_in, cur_user=cur_user)


if __name__ == "__main__":
    up_path = os.path.join('static', UPLOAD_DIRECTORY)
    if not os.path.exists(up_path):
        os.makedirs(up_path)
    # starts the app at `http://localhost:5000/`
    app.run(threaded=True, host='0.0.0.0', port=5000, debug=True)
