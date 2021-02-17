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
    return flask.render_template('press1mtimes/home.html',
                                 version=db.session.query(DataBase).order_by(DataBase.id.desc()).first().version_code)


@app.route('/update')
def update():
    return flask.render_template('main/update.html')


class DataBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(15), unique=False, nullable=False)
    version_code = db.Column(db.String(6), unique=True, nullable=False)
    project = db.Column(db.String(20), unique=False, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return '<Base %r>' % self.id


@app.route('/upload', methods=['POST'])
def upload():
    key = os.environ.get('KEY')
    u_key = request.form['key']

    if hashlib.sha224(bytes(u_key, encoding='utf-8')).hexdigest() != key:
        return flask.render_template('main/error.html', error_code="403", error_text="Access is denied, 403..."), 403

    file = request.files['file']

    DataBase.query.filter_by(id=DataBase.query.filter_by(project=request.form['project']).first().id).delete()
    new = DataBase(file_name=file.filename, version_code=request.form['v_code'], data=file.read(),
                   project=request.form['project'])
    db.session.add(new)
    db.session.commit()

    return flask.render_template('main/update.html', result="File has been uploaded successfully.")


@app.route('/press1mtimes/download')
def download():
    file_data = DataBase.query.filter_by(project="Press1MTimes").first()
    return send_file(BytesIO(file_data.data), attachment_filename=file_data.file_name, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
