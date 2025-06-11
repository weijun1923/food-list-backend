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
                "image_keys": restaurant.image_keys,
                "dish_name": restaurant.dish_name,
                "cuisine": restaurant.cuisine,
                "menu_category": restaurant.menu_category,
                "price": restaurant.price
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
            "image_keys": restaurant.image_keys,
            "dish_name": restaurant.dish_name,
            "cuisine": restaurant.cuisine,
            "menu_category": restaurant.menu_category,
            "price": restaurant.price
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
@restaurant_bp.route("/<int:restaurant_id>", methods=["DELETE"])
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

# Optional: GET restaurants by filter (e.g., by cuisine or restaurant name)
@restaurant_bp.route("/search", methods=["GET"])
@jwt_required()
def search_restaurants():
    try:
        # Get query parameters
        restaurant_name = request.args.get("restaurant_name")
        cuisine = request.args.get("cuisine")
        menu_category = request.args.get("menu_category")
        
        # Build query
        query = Restaurant.query
        
        if restaurant_name:
            query = query.filter(Restaurant.restaurant_name.ilike(f"%{restaurant_name}%"))
        
        if cuisine:
            query = query.filter(Restaurant.cuisine.ilike(f"%{cuisine}%"))
        
        if menu_category:
            query = query.filter(Restaurant.menu_category.ilike(f"%{menu_category}%"))
        
        restaurants = query.all()
        restaurant_list = []
        
        for restaurant in restaurants:
            restaurant_data = {
                "id": restaurant.id,
                "restaurant_name": restaurant.restaurant_name,
                "image_keys": restaurant.image_keys,
                "dish_name": restaurant.dish_name,
                "cuisine": restaurant.cuisine,
                "menu_category": restaurant.menu_category,
                "price": restaurant.price
            }
            restaurant_list.append(restaurant_data)
        
        return jsonify({
            "msg": "Search completed successfully",
            "restaurants": restaurant_list,
            "count": len(restaurant_list)
        }), 200
        
    except Exception as e:
        return jsonify({"msg": "Error searching restaurants", "error": str(e)}), 500
