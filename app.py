"""Flask app to serve a simple HTML page with a button to trigger a Python function."""

from flask import Flask, jsonify, request
from models import db, Restaurant


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///food-list.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# # 13. 定義 GET /restaurants 路由
# @app.route("/restaurants", methods=["GET"])
# def get_restaurants():


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
