from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from models import db, Restaurant, RestaurantMenu
restaurant_menu_bp = Blueprint(
    "restaurant_menu", __name__, url_prefix="/api/restaurant-menus")


@restaurant_menu_bp.route("/add/<uuid:restaurant_id>", methods=["POST"])
@jwt_required()
def add_restaurant_menu(restaurant_id):

    restaurant = Restaurant.query.filter_by(
        id=restaurant_id).first()
    if not restaurant:
        return jsonify({"msg": "Restaurant not found"}), 404

    if not request.is_json:
        return jsonify({"msg": "Unsupported Media Type. Expected application/json"}), 415

    data = request.get_json(silent=True) or {}
    image_key = data.get("image_key")
    dish_name = data.get("dish_name")
    cuisine = data.get("cuisine")
    menu_category = data.get("menu_category")
    price_raw = data.get("price")
    print("price", price_raw)

    if not dish_name or not cuisine or not menu_category:
        return jsonify({"msg": "Missing dish name, or cuisine"}), 400
    if price_raw in (None, ""):
        return jsonify({"msg": "Price is required"}), 400
    try:
        price = int(price_raw) if price_raw is not None else 0
    except (ValueError, TypeError):
        return jsonify({"msg": "Price must be a valid integer"}), 400

    new_restaurant_menu = RestaurantMenu(
        restaurant_id=restaurant_id,
        image_key=image_key,
        dish_name=dish_name,
        cuisine=cuisine,
        menu_category=menu_category,
        price=price
    )
    try:
        restaurant.restaurant_menu.append(new_restaurant_menu)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": "Error adding restaurant menu", "error": str(e)}), 500

    return jsonify({"msg": "Restaurant menu added successfully"}), 201


@restaurant_menu_bp.route("/get/<uuid:restaurant_id>", methods=["GET"])
@jwt_required()
def get_restaurant_menu(restaurant_id):
    try:
        restaurant = db.session.get(Restaurant, restaurant_id)
        if restaurant is None:
            return jsonify({"msg": "Restaurant not found"}), 404

        menus = restaurant.restaurant_menu

        if not menus:
            return jsonify({"msg": "No menus found for this restaurant"}), 404

        menu_list = [{
            "id": m.id,
            "restaurant_name": restaurant.restaurant_name,
            "restaurant_id": restaurant_id,
            "image_key": m.image_key,
            "dish_name": m.dish_name,
            "cuisine": m.cuisine,
            "menu_category": m.menu_category,
            "price": m.price
        } for m in menus]

        return jsonify({
            "msg": "Menus retrieved successfully",
            "menus": menu_list,
            "count": len(menu_list)
        }), 200

    except Exception as e:
        return jsonify({"msg": "Error retrieving menus", "error": str(e)}), 500


# UPDATE restaurant

@restaurant_menu_bp.route("/<int:restaurant_id>", methods=["PUT"])
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

        if "image_keys" in data:
            restaurant.image_keys = data["image_keys"]

        if "dish_name" in data:
            restaurant.dish_name = data["dish_name"]

        if "cuisine" in data:
            restaurant.cuisine = data["cuisine"]

        if "menu_category" in data:
            restaurant.menu_category = data["menu_category"]

        if "price" in data:
            try:
                restaurant.price = int(data["price"])
            except (ValueError, TypeError):
                return jsonify({"msg": "Price must be a valid integer"}), 400

        # Validate required fields
        if not restaurant.restaurant_name or not restaurant.dish_name or not restaurant.cuisine or not restaurant.menu_category:
            return jsonify({"msg": "Missing required fields: restaurant_name, dish_name, cuisine, or menu_category"}), 400

        db.session.commit()

        return jsonify({"msg": "Restaurant updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error updating restaurant", "error": str(e)}), 500

# DELETE restaurant


@restaurant_menu_bp.route("/<int:restaurant_id>", methods=["DELETE"])
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
