from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Restaurant
restaurant_bp = Blueprint("restaurant", __name__, url_prefix="/api/restaurant")


@restaurant_bp.route("/add", methods=["POST"])
@jwt_required()
def add_restaurant():
    if not request.is_json:
        return jsonify({"msg": "Unsupported Media Type. Expected application/json"}), 415

    data = request.get_json(silent=True) or {}
    restaurant_name = data.get("restaurant_name")
    image_keys= data.get("image_keys")
    dish_name = data.get("dish_name")
    cuisine = data.get("cuisine")
    menu_category = data.get("menu_category")
    price = data.get("price")


    if not restaurant_name or not dish_name or not cuisine or not menu_category:
        return jsonify({"msg": "Missing restaurant name, dish name, or cuisine"}), 400
    try:
        price = int(price) if price is not None else 0
    except (ValueError, TypeError):
        return jsonify({"msg": "Price must be a valid integer"}), 400

    new_restaurant = Restaurant(
        restaurant_name=restaurant_name,
        image_keys=image_keys,
        dish_name=dish_name,
        cuisine=cuisine,
        menu_category=menu_category,
        price=price
    )

    db.session.add(new_restaurant)
    db.session.commit()

    return jsonify({"msg": "Restaurant added successfully"}), 201


@restaurant_bp.route("/list", methods=["GET"])
@jwt_required()
def list_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = [
        {
            "id": str(restaurant.id),
            "restaurant_name": restaurant.restaurant_name,
            "image_url": restaurant.image_url,
            "dish_name": restaurant.dish_name,
            "cuisine": restaurant.cuisine,
            "created_at": restaurant.created_at.isoformat(),
            "updated_at": restaurant.updated_at.isoformat()
        } for restaurant in restaurants
    ]
    return jsonify(restaurant_list), 200


@restaurant_bp.route("/delete/<uuid:restaurant_id>", methods=["DELETE"])
@jwt_required()
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return jsonify({"msg": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()

    return jsonify({"msg": "Restaurant deleted successfully"}), 200


@restaurant_bp.route("/update/<uuid:restaurant_id>", methods=["PUT"])
@jwt_required()
def update_restaurant(restaurant_id):
    if not request.is_json:
        return jsonify({"msg": "Unsupported Media Type. Expected application/json"}), 415

    data = request.get_json(silent=True) or {}
    restaurant = Restaurant.query.get(restaurant_id)

    if not restaurant:
        return jsonify({"msg": "Restaurant not found"}), 404

    restaurant_name = data.get("restaurant_name", restaurant.restaurant_name)
    image_url = data.get("image_url", restaurant.image_url)
    dish_name = data.get("dish_name", restaurant.dish_name)
    cuisine = data.get("cuisine", restaurant.cuisine)

    restaurant.restaurant_name = restaurant_name
    restaurant.image_url = image_url
    restaurant.dish_name = dish_name
    restaurant.cuisine = cuisine

    db.session.commit()

    return jsonify({"msg": "Restaurant updated successfully"}), 200


@restaurant_bp.route("/search", methods=["GET"])
@jwt_required()
def search_restaurants():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"msg": "Query parameter is required"}), 400

    restaurants = Restaurant.query.filter(
        Restaurant.restaurant_name.ilike(f"%{query}%") |
        Restaurant.dish_name.ilike(f"%{query}%") |
        Restaurant.cuisine.ilike(f"%{query}%")
    ).all()

    restaurant_list = [
        {
            "id": str(restaurant.id),
            "restaurant_name": restaurant.restaurant_name,
            "image_url": restaurant.image_url,
            "dish_name": restaurant.dish_name,
            "cuisine": restaurant.cuisine,
            "created_at": restaurant.created_at.isoformat(),
            "updated_at": restaurant.updated_at.isoformat()
        } for restaurant in restaurants
    ]

    return jsonify(restaurant_list), 200
