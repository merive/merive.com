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
@app.route('/home')
def home():
    return flask.render_template('main/home.html')


@app.route('/projects')
def projects():
    return flask.render_template('main/projects.html')


@app.route('/links')
def links():
    return flask.render_template('main/links.html')


@app.route('/about')
def about():
    return flask.render_template('main/about.html')


@app.errorhandler(HTTPException)
def error_handler(e):
    return flask.render_template('main/error.html', error_code=e.code), e.code


# Press1MTimes code
class P1MTBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(25), unique=False, nullable=False)
    version_code = db.Column(db.String(6), unique=False, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return '<P1MTBase %r>' % self.id

    @staticmethod
    def add_in_db(filename, version_code, data):
        new = P1MTBase(file_name=filename, version_code=version_code, data=data)
        db.session.add(new)
        db.session.commit()

    @staticmethod
    def remove_rows():
        P1MTBase.query.delete()


@app.route('/P1MT')
def press1mtimes():
    # data = P1MTBase.query.filter_by().first()
    return flask.render_template('P1MT/home.html')


@app.route('/press1mtimes/download')
def download_p1mt():
    data = P1MTBase.query.filter_by().first()
    return send_file(BytesIO(data.data), attachment_filename=data.file_name, as_attachment=True)


@app.route('/P1MT/update')
def update_p1mt():
    return flask.render_template('P1MT/update.html')


@app.route('/P1MT/upload', methods=['POST'])
def upload_p1mt():
    check_hash(request.form['key'])
    P1MTBase().remove_rows()
    P1MTBase().add_in_db(request.files['file'].filename, request.form['version_code'], request.files['file'].read())
    return flask.render_template('P1MT/update.html', result="File has been uploaded successfully.")


# MTools code
class MToolsBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(25), unique=False, nullable=False)
    version_code = db.Column(db.String(6), unique=False, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    file_type = db.Column(db.String(3), unique=False, nullable=False)

    def __repr__(self):
        return '<MToolsBase %r>' % self.id

    @staticmethod
    def add_in_db(filename, version_code, data):
        new = MToolsBase(file_name=filename, version_code=version_code, data=data,
                         file_type=filename[len(filename) - 3:].upper())
        db.session.add(new)
        db.session.commit()

    @staticmethod
    def remove_rows(filename):
        try:
            MToolsBase.query.filter_by(file_type=filename[len(filename) - 3:].upper()).first().delete()
        except AttributeError:
            pass


@app.route('/MTools')
def mtools():
    data = MToolsBase.query.filter_by().first()
    return flask.render_template('MTools/home.html', version=data.version_code)


@app.route('/mtools/download/<file_type>')
def download_mtools(file_type: str):
    data = MToolsBase.query.filter_by(file_type=file_type).first()
    return send_file(BytesIO(data.data), attachment_filename=data.file_name, as_attachment=True)


@app.route('/MTools/update')
def update_mtools():
    return flask.render_template('MTools/update.html')


@app.route('/MTools/upload', methods=['POST'])
def upload_mtools():
    check_hash(request.form['key'])
    MToolsBase().remove_rows(request.files['file'].filename)
    MToolsBase().add_in_db(request.files['file'].filename, request.form['version_code'], request.files['file'].read())
    return flask.render_template('MTools/update.html', result="File has been uploaded successfully.")


# Parzibot code
@app.route('/Parzibot')
def parzibot():
    return flask.render_template('Parzibot/home.html')


def check_hash(u_key):
    if hashlib.sha224(bytes(u_key, encoding='utf-8')).hexdigest() != os.environ.get('KEY'):
        return flask.render_template('main/error.html'), 403


if __name__ == "__main__":
    app.run(debug=True)
