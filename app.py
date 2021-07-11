import hashlib
import os
from io import BytesIO

import flask
from flask import Flask, request, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-* Main variables, configs *-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Get link on database from server
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-* Main site pages *-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

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
    """Error page for any Exception"""
    return flask.render_template('main/error.html', error_code=e.code), e.code


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*- Press1MTimes Database -*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
class P1MTBase(db.Model):
    """P1MT DataBase for files"""
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(25), unique=False, nullable=False)
    version_code = db.Column(db.String(8), unique=False, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return '<P1MTBase %r>' % self.id

    @staticmethod
    def add_element_in_base(filename, version_code, data):
        """Adds new file in database"""
        new = P1MTBase(file_name=filename, version_code=version_code, data=data)
        db.session.add(new)
        db.session.commit()

    @staticmethod
    def remove_all_elements():
        """Remove all elements of database"""
        P1MTBase.query.delete()

    @staticmethod
    def get_version():
        """Return version of application"""
        try:
            return P1MTBase.query.filter_by().first().version_code
        except AttributeError:
            return "vx.x.x"


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -*-*-*-*-*-*- Press1MTimes Pages -*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@app.route('/P1MT')
def press1mtimes():
    """P1MT page"""
    return flask.render_template('P1MT/home.html', version=P1MTBase().get_version())


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
def upload_p1mt_file():
    """Uploads P1MT file in database"""
    if check_password(request.form['key']):
        P1MTBase().remove_all_elements()
        P1MTBase().add_element_in_base(request.files['file'].filename, request.form['version_code'],
                                       request.files['file'].read())
        return flask.render_template('P1MT/update.html', result="File has been uploaded successfully.")
    return flask.render_template('main/error.html', error_code=403), 403


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-* MTools Database *-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

class MToolsBase(db.Model):
    """MTools database"""
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(25), unique=False, nullable=False)
    version_code = db.Column(db.String(8), unique=False, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    file_type = db.Column(db.String(3), unique=False, nullable=False)

    def __repr__(self):
        return '<MToolsBase %r>' % self.id

    @staticmethod
    def add_element_in_base(filename, version_code, data):
        """Updates MTools files in database"""
        new = MToolsBase(file_name=filename, version_code=version_code, data=data,
                         file_type=filename[len(filename) - 3:].upper())
        db.session.add(new)
        db.session.commit()

    @staticmethod
    def remove_all_elements(filename):
        """Removes all element in database"""
        try:
            MToolsBase.query.filter_by(file_type=filename[len(filename) - 3:].upper()).first().delete()
        except AttributeError:
            pass

    @staticmethod
    def get_version():
        """Get last version of application"""
        try:
            return MToolsBase.query.filter_by().first().version_code
        except AttributeError:
            return "vx.x.x"


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -*-*-*-*-*-*-*-* MTools Pages *-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@app.route('/MTools')
def mtools():
    """MTools page"""
    return flask.render_template('MTools/home.html')


@app.route('/MTools/about')
def mtools_about():
    """MTools about page"""
    return flask.render_template('MTools/about.html')


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
def upload_mtools_file():
    """Uploads new MTools file in database"""
    if check_password(request.form['key']):
        MToolsBase().remove_all_elements(request.files['file'].filename)
        MToolsBase().add_element_in_base(request.files['file'].filename, request.form['version_code'],
                                         request.files['file'].read())
        return flask.render_template('MTools/update.html', result="File has been uploaded successfully.")
    return flask.render_template('main/error.html', error_code=403), 403


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*- Parzibot Page -*-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

@app.route('/Parzibot')
def parzibot():
    """Parzibot page"""
    return flask.render_template('Parzibot/home.html', link=os.environ.get('ParzibotLink'))


@app.route('/Parzibot/about')
def parzibot_about():
    """Parzibot about page"""
    return flask.render_template('Parzibot/about.html', links=os.environ.get('ParzibotLink'))


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-* SecurePass Database *-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

class SecurePassBase(db.Model):
    """SecurePass DataBase for files"""

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(25), unique=False, nullable=False)
    version_code = db.Column(db.String(8), unique=False, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return '<SecurePassBase %r>' % self.id

    @staticmethod
    def add_element_in_base(filename, version_code, data):
        """Adds new file in database"""
        new = SecurePassBase(file_name=filename, version_code=version_code, data=data)
        db.session.add(new)
        db.session.commit()

    @staticmethod
    def remove_all_elements():
        """Remove all elements of database"""
        SecurePassBase.query.delete()

    @staticmethod
    def get_version():
        """Get last version of application"""
        try:
            return SecurePassBase.query.filter_by().first().version_code
        except AttributeError:
            return "vx.x.x"


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-* SecurePass Page *-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

@app.route('/SecurePass')
def secure_pass():
    """SecurePass Page"""
    return flask.render_template('SecurePass/home.html',
                                 version=SecurePassBase.get_version())


@app.route('/SecurePass/download')
def download_secure_pass():
    """Download SecurePass Application"""
    data = SecurePassBase.query.filter_by().first()
    return send_file(BytesIO(data.data), attachment_filename=data.file_name, as_attachment=True)


@app.route('/SecurePass/update')
def update_secure_pass():
    """SecurePass file update page"""
    return flask.render_template('SecurePass/update.html',
                                 version=SecurePassBase.get_version())


@app.route('/SecurePass/upload', methods=['POST'])
def upload_secure_pass_file():
    """Uploads SecurePass file in database"""
    if check_password(request.form['key']):
        SecurePassBase().remove_all_elements()
        SecurePassBase().add_element_in_base(request.files['file'].filename, request.form['version_code'],
                                             request.files['file'].read())
        return flask.render_template('SecurePass/update.html', version=SecurePassBase.get_version(),
                                     result="File has been uploaded successfully.")
    return flask.render_template('main/error.html', error_code=403), 403


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*-* LinuxSetup Database *-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

class LinuxSetupBase(db.Model):
    """LinuxSetup DataBase for files"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False, nullable=False)
    link = db.Column(db.String(128), unique=False, nullable=False)
    description = db.Column(db.String(128), unique=False, nullable=False)

    def __repr__(self):
        return '<LinuxSetupBase %r>' % self.name

    @staticmethod
    def add_element_in_base(name, link, description):
        """Adds new file in database"""
        new = LinuxSetupBase(name=name, link=link, description=description)
        db.session.add(new)
        db.session.commit()

    @staticmethod
    def get_data():
        """Get All Data"""
        try:
            return LinuxSetupBase.query.all()
        except AttributeError:
            return None

    @staticmethod
    def delete_by_id(setup_id):
        """Delete setup from database using id"""
        try:
            LinuxSetupBase.query.filter_by(id=setup_id).delete()
            db.session.commit()
        except AttributeError:
            pass


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# -*-*-*-*-*-*-* LinuxSetup Pages *-*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

@app.route("/LinuxSetup")
def linux_setup():
    """LinuxSetup main page"""
    return flask.render_template("LinuxSetup/home.html", values=get_values_of_linux_setup())


@app.route("/LinuxSetup/add")
def add_linux_setup():
    """Add LinuxSetup page"""
    return flask.render_template("LinuxSetup/add.html")


@app.route('/LinuxSetup/upload', methods=['POST'])
def upload_linux_setup():
    """Upload LinuxSetup data in DataBase"""
    if check_password(request.form['key']):
        LinuxSetupBase.add_element_in_base(request.form['name'], request.form['link'], request.form['description'])
        return flask.render_template('LinuxSetup/add.html', result="Setup was added successfully.")
    return flask.render_template('main/error.html', error_code=403), 403


@app.route('/LinuxSetup/delete/<setup_id>/<password>')
async def delete_setup(setup_id, password):
    """Delete setup by id"""
    if check_password(password):
        LinuxSetupBase.delete_by_id(setup_id)
        return f"Setup #{setup_id} deleted"
    return flask.render_template('main/error.html', error_code=403), 403


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# -*-*-*-*-*-*- Another functions -*-*-*-*-*-*-
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

def check_password(password):
    """Checks password for uploading files"""
    return hashlib.sha224(bytes(password, encoding='utf-8')).hexdigest() == os.environ.get('KEY')


def get_values_of_linux_setup():
    """Get data of setups from database"""
    try:
        data = LinuxSetupBase.get_data()
        return [[i.name, i.link, i.description] for i in data]
    except TypeError or AttributeError:
        return []


# Run application
if __name__ == "__main__":
    app.run(debug=True)


def make_db():
    db.create_all()
