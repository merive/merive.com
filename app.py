import hashlib
import os
from io import BytesIO

import flask
from flask import Flask, request, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route('/')
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


@app.errorhandler(HTTPException)
def error_handler(e):
    return flask.render_template('main/error.html', error_code=e.code, error_text=f'Oops, {e.code}...'), e.code


# Press1MTimes code
@app.route('/press1mtimes')
def press1mtimes():
    data = DataBase.query.filter_by(project="Press1MTimes").first()
    return flask.render_template('press1mtimes/home.html', version=data.version_code)


@app.route('/press1mtimes/download')
def download_p1mt():
    data = DataBase.query.filter_by(project="Press1MTimes").first()
    return send_file(BytesIO(data.data), attachment_filename=data.file_name, as_attachment=True)


# MTools code
@app.route('/mtools')
def mtools():
    data = DataBase.query.filter_by(project="MTools").first()
    return flask.render_template('mtools/home.html', version=data.version_code)


@app.route('/mtools/download/<platform>')
def download_mtools(platform: str):
    data = DataBase.query.filter_by(project="MTools", platform=platform).first()
    return send_file(BytesIO(data.data), attachment_filename=data.file_name, as_attachment=True)


# DataBase code
class DataBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(15), unique=False, nullable=False)
    version_code = db.Column(db.String(6), unique=False, nullable=False)
    project = db.Column(db.String(30), unique=False, nullable=False)
    platform = db.Column(db.String(10), unique=False, nullable=True)
    data = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return '<DataBase %r>' % self.id


@app.route('/update')
def update():
    return flask.render_template('main/update.html')


@app.route('/upload', methods=['POST'])
def upload():
    check_hash(request.form['key'])

    try:
        delete_from_db(request.form['project'], request.form['platform'])
    except AttributeError:
        print("DataBase is empty")

    add_in_db(request.files['file'].filename, request.form['v_code'], request.files['file'].read(),
              request.form['project'], request.form['platform'])
    return flask.render_template('main/update.html', result="File has been uploaded successfully.")


def check_hash(u_key):
    if hashlib.sha224(bytes(u_key, encoding='utf-8')).hexdigest() != os.environ.get('KEY'):
        return flask.render_template('main/error.html', error_code="403", error_text="Access is denied, 403..."), 403


def delete_from_db(project, platform):
    DataBase.query.filter_by(id=DataBase.query.filter_by(project=project, platform=platform).first().id).delete()


def add_in_db(filename, version_code, data, project, platform):
    new = DataBase(file_name=filename, version_code=version_code, data=data, project=project, platform=platform)
    db.session.add(new)
    db.session.commit()


if __name__ == "__main__":
    app.run(debug=False)
