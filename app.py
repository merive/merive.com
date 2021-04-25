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
    """Home page"""
    return flask.render_template('main/home.html')


@app.route('/projects')
def projects():
    """Projects page"""
    return flask.render_template('main/projects.html')


@app.route('/links')
def links():
    """Links page"""
    return flask.render_template('main/links.html')


@app.route('/about')
def about():
    """About page"""
    return flask.render_template('main/about.html')


@app.errorhandler(HTTPException)
def error_handler(e):
    """Return Error page"""
    return flask.render_template('main/error.html', error_code=e.code), e.code


# Press1MTimes code
class P1MTBase(db.Model):
    """P1MT DataBase for files"""

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(25), unique=False, nullable=False)
    version_code = db.Column(db.String(6), unique=False, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return '<P1MTBase %r>' % self.id

    @staticmethod
    def add_elm(filename, version_code, data):
        """Adds new file in database"""
        new = P1MTBase(file_name=filename, version_code=version_code, data=data)
        db.session.add(new)
        db.session.commit()

    @staticmethod
    def remove_elms():
        """Remove all elements of database"""
        P1MTBase.query.delete()


@app.route('/P1MT')
def press1mtimes():
    """P1MT page"""
    try:
        data = P1MTBase.query.filter_by().first()
        return flask.render_template('P1MT/home.html', version=data.version_code)
    except AttributeError:
        return flask.render_template('P1MT/home.html')


@app.route('/P1MT/download')
def download_p1mt():
    """Download P1MT page"""
    data = P1MTBase.query.filter_by().first()
    return send_file(BytesIO(data.data), attachment_filename=data.file_name, as_attachment=True)


@app.route('/P1MT/update')
def update_p1mt():
    """P1MT file update page"""
    return flask.render_template('P1MT/update.html')


@app.route('/P1MT/upload', methods=['POST'])
def upload_p1mt():
    """Uploads P1MT file in database"""
    check_hash(request.form['key'])
    P1MTBase().remove_elms()
    P1MTBase().add_elm(request.files['file'].filename, request.form['version_code'], request.files['file'].read())
    return flask.render_template('P1MT/update.html', result="File has been uploaded successfully.")


# MTools code
class MToolsBase(db.Model):
    """MTools database"""

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(25), unique=False, nullable=False)
    version_code = db.Column(db.String(6), unique=False, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    file_type = db.Column(db.String(3), unique=False, nullable=False)

    def __repr__(self):
        return '<MToolsBase %r>' % self.id

    @staticmethod
    def add_elm(filename, version_code, data):
        """Updates MTools files in database"""
        new = MToolsBase(file_name=filename, version_code=version_code, data=data,
                         file_type=filename[len(filename) - 3:].upper())
        db.session.add(new)
        db.session.commit()

    @staticmethod
    def remove_elm(filename):
        """Removes old element in database"""
        try:
            MToolsBase.query.filter_by(file_type=filename[len(filename) - 3:].upper()).first().delete()
        except AttributeError:
            pass


@app.route('/MTools')
def mtools():
    """MTools page"""
    return flask.render_template('MTools/home.html')


@app.route('/MTools/download')
def download_mtools():
    """Download Page for MTools"""
    try:
        data = MToolsBase.query.filter_by().first()
        return flask.render_template('MTools/download.html', version=data.version_code)
    except AttributeError:
        return flask.render_template('MTools/download.html')


@app.route('/MTools/download/<file_type>')
def save_mtools(file_type):
    """Saves MTools files on your PC"""
    data = MToolsBase.query.filter_by(file_type=file_type).first()
    return send_file(BytesIO(data.data), attachment_filename=data.file_name, as_attachment=True)


@app.route('/MTools/update')
def update_mtools():
    """Update MTools page"""
    return flask.render_template('MTools/update.html')


@app.route('/MTools/upload', methods=['POST'])
def upload_mtools():
    """Uploads new MTools file in database"""
    check_hash(request.form['key'])
    MToolsBase().remove_elm(request.files['file'].filename)
    MToolsBase().add_elm(request.files['file'].filename, request.form['version_code'], request.files['file'].read())
    return flask.render_template('MTools/update.html', result="File has been uploaded successfully.")


# Parzibot code
@app.route('/Parzibot')
def parzibot():
    """Parzibot page"""
    return flask.render_template('Parzibot/home.html', link=os.environ.get('ParzibotLink'))


# SecurePass code
class SecurePassBase(db.Model):
    """SecurePass DataBase for files"""

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(25), unique=False, nullable=False)
    version_code = db.Column(db.String(6), unique=False, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return '<SecurePassBase %r>' % self.id

    @staticmethod
    def add_elm(filename, version_code, data):
        """Adds new file in database"""
        new = SecurePassBase(file_name=filename, version_code=version_code, data=data)
        db.session.add(new)
        db.session.commit()

    @staticmethod
    def remove_elms():
        """Remove all elements of database"""
        SecurePassBase.query.delete()


@app.route('/SecurePass')
def secure_pass():
    """SecurePass Page"""
    try:
        return flask.render_template('SecurePass/home.html',
                                     version=SecurePassBase.query.filter_by().first().version_code)
    except AttributeError:
        return flask.render_template('SecurePass/home.html')


@app.route('/SecurePass/download')
def download_secure_pass():
    """Download SecurePass Application"""
    data = SecurePassBase.query.filter_by().first()
    return send_file(BytesIO(data.data), attachment_filename=data.file_name, as_attachment=True)


@app.route('/SecurePass/update')
def update_secure_pass():
    """SecurePass file update page"""
    try:
        return flask.render_template('SecurePass/update.html',
                                     version=SecurePassBase.query.filter_by().first().version_code)
    except AttributeError:
        return flask.render_template('SecurePass/update.html')


@app.route('/SecurePass/upload', methods=['POST'])
def upload_secure_pass():
    """Uploads SecurePass file in database"""
    check_hash(request.form['key'])
    SecurePassBase().remove_elms()
    SecurePassBase().add_elm(request.files['file'].filename, request.form['version_code'], request.files['file'].read())
    return flask.render_template('SecurePass/update.html', result="File has been uploaded successfully.")


# Hash checker
def check_hash(u_key):
    """Checks password for uploading files"""
    if hashlib.sha224(bytes(u_key, encoding='utf-8')).hexdigest() != os.environ.get('KEY'):
        return flask.render_template('main/error.html'), 403


if __name__ == "__main__":
    app.run(debug=False)
