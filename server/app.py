#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"
class RestaurantsListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict() for restaurant in restaurants], 200
class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        restaurant_dict = restaurant.to_dict()
        restaurant_dict["restaurant_pizzas"] = [rp.to_dict() for rp in restaurant.restaurant_pizzas]
        return restaurant_dict, 200
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204
class PizzasListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200
class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")
        if price is None or pizza_id is None or restaurant_id is None:
            return {"errors": ["Missing required fields"]}, 400
        if not (1 <= price <= 30):
            return {"errors": ["validation errors"]}, 400
        restaurant = Restaurant.query.get(restaurant_id)
        pizza = Pizza.query.get(pizza_id)
        if not restaurant or not pizza:
            return {"errors": ["Invalid restaurant_id or pizza_id"]}, 400
        try:
            new_rp = RestaurantPizza(price=price, restaurant=restaurant, pizza=pizza)
            db.session.add(new_rp)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 400
        return new_rp.to_dict(), 201  
api.add_resource(RestaurantsListResource, "/restaurants")
api.add_resource(RestaurantResource, "/restaurants/<int:id>")
api.add_resource(PizzasListResource, "/pizzas")
api.add_resource(RestaurantPizzaResource, "/restaurant_pizzas")
if __name__ == "__main__":
    app.run(port=5555, debug=True)