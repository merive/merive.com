import flask
from flask import Flask, send_from_directory

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return flask.render_template('home.html')


@app.route('/about')
def about():
    return flask.render_template('about.html')


@app.route('/projects')
def projects():
    return flask.render_template('projects.html')


@app.route('/links')
def links():
    return flask.render_template('links.html')


@app.route('/press1mtimes')
def press1mtimes():
    return flask.render_template('press1mtimes.html')


@app.route('/download', methods=['GET'])
def download():
    return send_from_directory(directory='files', filename='app_v1.2.5.apk', as_attachment=True)


@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=False)
