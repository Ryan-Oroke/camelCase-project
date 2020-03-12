# The server written in flask
# I'm going to start and get something like this working:
#       https://blog.learningdollars.com/2019/11/29/how-to-serve-a-reactapp-with-a-flask-server/
# and the post get stuff

import os

from flask import Flask, render_template, jsonify, abort, request, make_response, url_for

# from flask_cors import CORS  # is this needed

app = Flask(__name__)
app.secret_key = "Not Random. Oh Noes!"  # This is for metadata encryption

# CORS(app)

@app.route('/')
def root_route():
    return render_template("master.html")


@app.route('/login')
def login_page():
    return render_template("login.html")


@app.route('/upload')
def upload_page():
    return render_template("upload.html")


@app.route('/download')
def download_page():
    return render_template("download.html")


@app.route('/navbar')
def navbar_page():
    return render_template("navbar.html")


@app.route('/about')
def about_page():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', port=5000, debug=True)
