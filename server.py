# The server written in flask
# I'm going to start and get something like this working:
#       https://blog.learningdollars.com/2019/11/29/how-to-serve-a-reactapp-with-a-flask-server/
# and the post get stuff

import os
from typing import NamedTuple

from flask import Flask, render_template, jsonify, abort, request, make_response, url_for

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


@app.route('/')
def root_route():
    return render_template("index.html")


@app.route('/upload')
def upload_page():
    return render_template("upload.html")


@app.route('/download')
def download_page():
    test_data = [file_data_html("test1", 40.015869, -105.279517, "dick", "123", 100, 12), file_data_html("test2", 40.016869, -105.279617, "dick", "123", 101, 34)]



    return render_template("download.html", fils=test_data)


@app.route('/navbar')
def navbar_page():
    return render_template("navbar.html")


@app.route('/about')
def about_page():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', port=5000, debug=True)
