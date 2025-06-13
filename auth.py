from datetime import datetime
from datetime import timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import set_refresh_cookies
from flask_jwt_extended import unset_jwt_cookies
from sqlalchemy import or_
from models import db, User, TokenBlocklist

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({"msg": "Unsupported Media Type. Expected application/json"}, 415)
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not username or not password or not email:
        return jsonify({"msg": "Missing username, password, or email"}), 400
    existing = User.query.filter(
        or_(User.email == email, User.username == username)
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
    if not request.is_json:
        return jsonify({"msg": "Unsupported Media Type. Expected application/json"}), 415

    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    # 把 JWT 寫進 Cookie
    resp = jsonify(
        login=True,
        user_id=user.id,
        username=user.username,   # 加上 username
        role=user.role
    )
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)

    return resp, 200            # 只回傳 Response 與狀態碼


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)

    resp = jsonify(refresh=True)
    set_access_cookies(resp, access_token)
    return resp, 200


@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    resp = jsonify(logout=True)
    # 同時清掉 access & refresh (及 CSRF) cookies
    unset_jwt_cookies(resp)
    return resp, 200
