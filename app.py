import hashlib
import os

import flask
from flask import Flask, request
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


@app.route('/P1MT')
def press1mtimes():
    data = P1MTBase.query.filter_by().first()
    return flask.render_template('P1MT/home.html', version=data.version_code)


@app.route('/P1MT/update')
def update():
    return flask.render_template('P1MT/update.html')


@app.route('/P1MT/upload', methods=['POST'])
def upload():
    check_hash(request.form['key'])
    remove_rows()
    add_in_db(request.files['file'].filename, request.form['version_code'], request.files['file'].read())
    return flask.render_template('P1MT/update.html', result="File has been uploaded successfully.")


def check_hash(u_key):
    if hashlib.sha224(bytes(u_key, encoding='utf-8')).hexdigest() != os.environ.get('KEY'):
        return flask.render_template('main/error.html'), 403


def add_in_db(filename, version_code, data):
    new = P1MTBase(file_name=filename, version_code=version_code, data=data)
    db.session.add(new)
    db.session.commit()


def remove_rows():
    P1MTBase.query.delete()


if __name__ == "__main__":
    app.run(debug=True)
