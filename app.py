import hashlib
import os
from io import BytesIO

import flask
from flask import Flask, request, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///merive.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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


# noinspection PyUnusedLocal
@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('main/error.html', error_code="404", error_text="Something went wrong, 404..."), 404


# Press1MTimes code
@app.route('/press1mtimes')
def press1mtimes():
    return flask.render_template('press1mtimes/home.html',
                                 version=db.session.query(Base).order_by(Base.id.desc()).first().version_code)


@app.route('/update')
def update():
    return flask.render_template('press1mtimes/update.html')


class Base(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(15), unique=True, nullable=False)
    version_code = db.Column(db.String(6), unique=True, nullable=False)
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
    new = Base(file_name=file.filename, version_code=request.form['v_code'], data=file.read())
    db.session.add(new)
    db.session.commit()

    return flask.render_template('press1mtimes/update.html', result="File has been uploaded successfully.")


@app.route('/download')
def download():
    file_data = db.session.query(Base).order_by(Base.id.desc()).first()
    return send_file(BytesIO(file_data.data), attachment_filename=file_data.file_name, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=False)
