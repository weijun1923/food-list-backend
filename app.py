"""Flask app to serve a simple HTML page with a button to trigger a Python function."""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from auth import auth_bp
from image_manager import image_bp
from restaurant import restaurant_bp
from restaurant_menu import restaurant_menu_bp
from config import Config
from models import db, TokenBlocklist

jwt = JWTManager()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(_jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    return db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar() is not None


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000"       # ← 兩種都允許最保險
        ]}},
        supports_credentials=True,               # ← 讓 Set-Cookie 能用
        allow_headers=["Content-Type", "X-CSRF-TOKEN"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(restaurant_menu_bp)

    # Create tables within application context
    with app.app_context():
        db.create_all()

    return app
