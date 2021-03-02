import flask
from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    return flask.render_template('main/home.html')


if __name__ == "__main__":
    app.run(debug=True)
