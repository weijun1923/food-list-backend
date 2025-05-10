"""Flask app to serve a simple HTML page with a button to trigger a Python function."""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager


from auth import auth_bp
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp)

    # Create tables within application context
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
