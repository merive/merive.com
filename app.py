import flask
from flask import Flask, send_from_directory, request

from werkzeug.utils import secure_filename

import os
from os import listdir

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'files/'


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
	return flask.render_template('press1mtimes/press1mtimes.html', version=listdir("files/")[0].split("_")[1].split(".apk")[0])


@app.route('/download', methods=['GET'])
def download():
	file = listdir("files/")
	return flask.send_from_directory(directory='files', filename=str(file[0]), as_attachment=True)


@app.route('/update')
def update():
	return flask.render_template('press1mtimes/update.html')
	
@app.route('/load', methods = ['POST'])
def load():
	if request.method == 'POST':
		key = os.environ.get('KEY')
		u_key = request.form['key']

		if u_key != key:
			return "Wrong password."

		f = request.files['file']

		files = listdir("files/")
		for file in files:
			os.remove(f'files/{file}')

		filename = secure_filename(f.filename)
		f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		return "File update."


@app.errorhandler(404)
def page_not_found(e):
	return flask.render_template('main/404.html'), 404


if __name__ == "__main__":
	app.run(debug=True)
