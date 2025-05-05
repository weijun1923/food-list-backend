"""Flask app to serve a simple HTML page with a button to trigger a Python function."""

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
