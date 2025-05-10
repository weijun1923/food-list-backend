import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import boto3
from botocore.config import Config
from models import db, Restaurant

restaurant_bp = Blueprint("restaurant", __name__, url_prefix="/api/products")

R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_KEY = os.getenv("R2_KEY")
R2_SECRET = os.getenv("R2_SECRET")
R2_TOKEN = os.getenv("R2_TOKEN")

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


@restaurant_bp.route("", methods=["POST"])
@jwt_required()
def create_product():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    product = Product(
        name=data.get("name"),
        description=data.get("description"),
        price=data.get("price"),
        owner_id=current_user_id,
    )
    db.session.add(product)
    db.session.commit()
    return (
        jsonify(
            {
                "msg": "Product created",
                "product": {"id": product.id, "name": product.name},
            }
        ),
        201,
    )


@restaurant_bp.route("", methods=["GET"])
@jwt_required()
def list_products():
    current_user_id = get_jwt_identity()
    items = Product.query.filter_by(owner_id=current_user_id).all()
    result = [
        {"id": p.id, "name": p.name, "description": p.description, "price": p.price}
        for p in items
    ]
    return jsonify(result), 200
