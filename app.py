"""Flask app to serve a simple HTML page with a button to trigger a Python function."""

import os
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
import boto3
from botocore.config import Config

from models import db, Restaurant

R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_KEY = os.getenv("R2_KEY")
R2_SECRET = os.getenv("R2_SECRET")
R2_TOKEN = os.getenv("R2_TOKEN")


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///food-list.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

with app.app_context():
    db.create_all()

my_config = Config(
    request_checksum_calculation="WHEN_REQUIRED",
    response_checksum_validation="WHEN_REQUIRED",
)


s3 = boto3.client(
    service_name="s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_KEY,
    aws_secret_access_key=R2_SECRET,
    region_name="auto",
    config=my_config,
)


# # 13. 定義 GET /restaurants 路由
# @app.route("/restaurants", methods=["GET"])
# def get_restaurants():


@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    username: str = request.json.get("username")
    password: str = request.json.get("password")
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    if username != "test" or password != "test":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route("/add")
def hello_world():
    new_mem = Restaurant(
        name="test",
        image_url="https://example.com/image.jpg",
        short_description="This is a test restaurant.",
        is_published=False,
    )
    db.session.add(new_mem)
    db.session.commit()
    return "it's ok"


@app.route("/get")
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = [
        {
            "id": restaurant.id,
            "name": restaurant.name,
            "image_url": restaurant.image_url,
            "short_description": restaurant.short_description,
            "is_published": restaurant.is_published,
            "created_at": restaurant.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for restaurant in restaurants
    ]
    return jsonify(restaurant_list)


# 22. 啟動 Flask 開發伺服器（debug 模式）
if __name__ == "__main__":
    app.run(debug=True)
