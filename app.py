import hashlib
import os
from os import listdir

import flask
from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'files/'
version = listdir("files/")[0][4:-4] if listdir("files/")[0][10:] == ".apk" and listdir("files/")[0][:3] == "app" \
    else listdir("files/")[0]


@app.route('/')
@app.route('/home')
def home():
    return flask.render_template('main/home.html')


@app.route('/about')
def about():
    return flask.render_template('main/about.html')


@app.route('/projects')
def projects():
    return flask.render_template('main/projects.html')


@app.route('/links')
def links():
    return flask.render_template('main/links.html')


@app.route('/press1mtimes')
def press1mtimes():
    return flask.render_template('press1mtimes/home.html', version=version)


@app.route('/download', methods=['GET'])
def download():
    file = listdir("files/")
    return flask.send_from_directory(directory='files', filename=str(file[0]), as_attachment=True)


@app.route('/update')
def update():
    return flask.render_template('press1mtimes/update.html')


@app.route('/load', methods=['POST'])
def load():
    if request.method != 'POST':
        return
    key = os.environ.get('KEY')
    u_key = request.form['key']

    if hashlib.sha224(bytes(u_key, encoding='utf-8')).hexdigest() != key:
        return "Wrong password."

    f = request.files['file']
    global version
    filename = secure_filename(f.filename)
    if filename[10:] == ".apk" and filename[:3] == "app":
        if request.form['v_code'] != "":
            version = request.form['v_code']
        else:
            version = filename[4:-4]
    else:
        return "Wrong file name..."

    files = listdir("files/")
    for file in files:
        os.remove(f'files/{file}')
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return flask.render_template('press1mtimes/home.html', version=version)


# noinspection PyUnusedLocal
@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('main/404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
