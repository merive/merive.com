import flask
from flask import Flask
from werkzeug.exceptions import HTTPException

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(debug=True)
