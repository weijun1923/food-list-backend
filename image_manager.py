import os
from dotenv import load_dotenv

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import boto3

load_dotenv()

# 專門處理圖片功能的 Blueprint
image_bp = Blueprint("image", __name__, url_prefix="/api/images")

R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
EXPIRY = 15*60

s3 = boto3.client(
    service_name="s3",
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",  # Must be one of: wnam, enam, weur, eeur, apac, auto
)


def _presign_put(key: str):
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": BUCKET_NAME, "Key": key},
        ExpiresIn=EXPIRY,
    )


def _presign_delete(key: str):
    return s3.generate_presigned_url(
        "delete_object",
        Params={"Bucket": BUCKET_NAME, "Key": key},
        ExpiresIn=EXPIRY,
    )

def _presign_get(key: str) -> str:
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": key,
        },
        ExpiresIn=EXPIRY,
    )



@image_bp.route("/presigned/upload", methods=["POST"])
@jwt_required()
def presigned_upload():
    # [{"name":"a.png"}, ...]
    if not request.json:
        return jsonify({"error": "Invalid JSON data"}), 400
    files = request.json.get("files")
    if not isinstance(files, list):
        files = [files]
    urls = []
    for data in files:
        key = data['name']  # e.g. "restaurant_name/xxx.png"
        urls.append({"key": key, "url": _presign_put(key)})
    return jsonify(urls)


@image_bp.route("/presigned/update", methods=["POST"])
@jwt_required()
def presigned_update():
    if not request.json:
        return jsonify({"error": "Invalid JSON data"}), 400
    datas = request.get_json(silent=True) or {}
    keys = datas.get("keys")             # ["uploads/xxx.png", ...]
    if not isinstance(keys, list):
        keys = [keys]
    urls = []
    for key in keys:
        if key is not None and isinstance(key, str):
            urls.append({"key": key, "url": _presign_put(key)})
    return jsonify(urls)


@image_bp.route("/presigned/delete", methods=["POST"])
@jwt_required()
def presigned_delete():
    if not request.json:
        return jsonify({"error": "Invalid JSON data"}), 400
    datas = request.get_json(silent=True) or {}
    keys = datas.get("keys")             # ["uploads/xxx.png", ...]
    if not isinstance(keys, list):
        keys = [keys]
    urls = []
    for key in keys:
        if key is not None and isinstance(key, str):
            urls.append({"key": key, "url": _presign_delete(key)})
    return jsonify(urls)

@image_bp.route("/presigned/get", methods=["POST"])
@jwt_required()
def presigned_get():
    if not request.json:
        return jsonify({"error": "Invalid JSON data"}), 400
    datas = request.get_json(silent=True) or {}
    keys = datas.get("keys")             # ["uploads/xxx.png", ...]
    if not isinstance(keys, list):
        keys = [keys]
    urls = []
    for key in keys:
        if key is not None and isinstance(key, str):
            urls.append( _presign_get(key))
    return jsonify({ "urls": urls })