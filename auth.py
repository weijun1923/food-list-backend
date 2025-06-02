from datetime import datetime
from datetime import timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt

from models import db, User, TokenBlocklist

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({"msg": "Unsupported Media Type. Expected application/json"}, 415)
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    email: str = data.get("email")
    if not username or not password or not email:
        return jsonify({"msg": "Missing username, password, or email"}), 400
    # 檢查唯一性
    existing = User.query.filter(
        db.or_(User.email == email, User.username == username)
    ).first()
    if existing:
        field = "email" if existing.email == email else "username"
        return jsonify(msg=f"{field} already exists"), 409

    user = User(username, password, email)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401
    username = user.username

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return (
        jsonify(
            access_token=access_token, refresh_token=refresh_token, username=username
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


# Callback function to check if a JWT exists in the database blocklist
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify(msg="JWT revoked")
