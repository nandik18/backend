from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__)
CORS(app)

# 🔗 Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["restaurant_db"]
restaurants_collection = db["restaurants"]
expenses_collection = db["expenses"]

# -------------------------------
# 🧠 RESTAURANTS ROUTES
# -------------------------------

@app.route("/api/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = list(restaurants_collection.find())
    for r in restaurants:
        r["_id"] = str(r["_id"])
    return jsonify(restaurants)

@app.route("/api/restaurants", methods=["POST"])
def add_restaurant():
    data = request.json  # expects { name, location }
    result = restaurants_collection.insert_one(data)
    new_restaurant = restaurants_collection.find_one({"_id": result.inserted_id})
    new_restaurant["_id"] = str(new_restaurant["_id"])
    return jsonify(new_restaurant)

@app.route("/api/restaurants/<id>", methods=["DELETE"])
def delete_restaurant(id):
    result = restaurants_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Deleted"}), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# -------------------------------
# 💰 EXPENSES ROUTES
# -------------------------------

@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    expenses = list(expenses_collection.find())
    for e in expenses:
        e["_id"] = str(e["_id"])
    return jsonify(expenses)

@app.route("/api/expenses", methods=["POST"])
def add_expense():
    data = request.json  # expects { restaurantId, amount, paymentMethod, mode}   
    required_fields = ["restaurantId", "amount", "paymentMethod","mode"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    result = expenses_collection.insert_one(data)
    new_expense = expenses_collection.find_one({"_id": result.inserted_id})
    new_expense["_id"] = str(new_expense["_id"])
    return jsonify(new_expense)

@app.route("/api/expenses/<id>", methods=["DELETE"])
def delete_expense(id):
    result = expenses_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Deleted"}), 200
    else:
        return jsonify({"error": "Expense not found"}), 404

# -------------------------------
# 🚀 Run Server
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True)