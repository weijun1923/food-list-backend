from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from models import db, Restaurant
restaurant_bp = Blueprint("restaurant", __name__, url_prefix="/api/restaurant")


@restaurant_bp.route("/add", methods=["POST"])
@jwt_required()
def add_restaurant():
    if not request.is_json:
        return jsonify({"msg": "Unsupported Media Type. Expected application/json"}), 415

    data = request.get_json(silent=True) or {}
    restaurant_name = data.get("restaurant_name")
    image_key = data.get("image_key")
    print(image_key)

    if not restaurant_name:
        return jsonify({"msg": "Missing restaurant name, dish name, or cuisine"}), 400

    new_restaurant = Restaurant(
        restaurant_name=restaurant_name,
        image_key=image_key,
    )

    db.session.add(new_restaurant)

    try:
        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()

        if 'restaurant_restaurant_name_key' in str(err.orig):
            return jsonify({ "msg": "the restaurant name is aleady exity" }), 409

        return jsonify({ "msg": "database error" }), 400

    return jsonify({"msg": "Restaurant added successfully"}), 201


@restaurant_bp.route("/all", methods=["GET"])
@jwt_required()
def get_all_restaurants():
    try:
        restaurants = Restaurant.query.all()
        restaurant_list = []

        for restaurant in restaurants:
            restaurant_data = {
                "id": restaurant.id,
                "restaurant_name": restaurant.restaurant_name,
                "image_key": restaurant.image_key,
                "created_at": restaurant.created_at.isoformat(),
                "updated_at": restaurant.updated_at.isoformat(),
            }
            restaurant_list.append(restaurant_data)

        return jsonify({
            "msg": "Restaurants retrieved successfully",
            "restaurants": restaurant_list,
            "count": len(restaurant_list)
        }), 200

    except Exception as e:
        return jsonify({"msg": "Error retrieving restaurants", "error": str(e)}), 500

# GET single restaurant by ID


@restaurant_bp.route("/<int:restaurant_id>", methods=["GET"])
@jwt_required()
def get_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            return jsonify({"msg": "Restaurant not found"}), 404

        restaurant_data = {
            "id": restaurant.id,
            "restaurant_name": restaurant.restaurant_name,
            "image_key": restaurant.image_key,
        }

        return jsonify({
            "msg": "Restaurant retrieved successfully",
            "restaurant": restaurant_data
        }), 200

    except Exception as e:
        return jsonify({"msg": "Error retrieving restaurant", "error": str(e)}), 500

# UPDATE restaurant


@restaurant_bp.route("/<int:restaurant_id>", methods=["PUT"])
@jwt_required()
def update_restaurant(restaurant_id):
    if not request.is_json:
        return jsonify({"msg": "Unsupported Media Type. Expected application/json"}), 415

    try:
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            return jsonify({"msg": "Restaurant not found"}), 404

        data = request.get_json(silent=True) or {}

        # Update fields if provided
        if "restaurant_name" in data:
            restaurant.restaurant_name = data["restaurant_name"]

        if "image_key" in data:
            restaurant.image_key = data["image_key"]

        # Validate required fields
        if not restaurant.restaurant_name:
            return jsonify({"msg": "Missing required fields: restaurant_name"}), 400

        db.session.commit()

        return jsonify({"msg": "Restaurant updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error updating restaurant", "error": str(e)}), 500

# DELETE restaurant


@restaurant_bp.route("/<uuid:restaurant_id>", methods=["DELETE"])
@jwt_required()
def delete_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            return jsonify({"msg": "Restaurant not found"}), 404

        db.session.delete(restaurant)
        db.session.commit()

        return jsonify({"msg": "Restaurant deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting restaurant", "error": str(e)}), 500
    



@restaurant_bp.route("/with-menus", methods=["GET"])
@jwt_required()
def restaurants_with_menus():
    try:
        # 使用 joinedload 一次撈取餐廳及其菜單
        restaurants = (
            db.session.query(Restaurant)
            .options(joinedload(Restaurant.restaurant_menu))
            .all()
        )
        # 組裝回傳資料
        data = []
        for r in restaurants:
            data.append({
                "id": str(r.id),
                "restaurant_name": r.restaurant_name,
                "image_key": r.image_key,
                "created_at": str(r.created_at) if r.created_at else None,
                "updated_at": str(r.updated_at) if r.updated_at else None,
                "menus": [
                    {
                        "id": str(m.id),
                        "restaurant_id": str(r.id),
                        "image_key": m.image_key,
                        "dish_name": m.dish_name,
                        "cuisine": m.cuisine,
                        "menu_category": m.menu_category,
                        "price": m.price,
                    }
                    for m in (r.restaurant_menu or [])
                ]
            })

        return jsonify({
            "msg": "Restaurants with menus retrieved successfully",
            "restaurants": data,
            "count": len(data)
        }), 200

    except Exception as e:
        return jsonify({"msg": "Error retrieving restaurants with menus", "error": str(e)}), 500
