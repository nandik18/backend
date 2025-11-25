from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__)
CORS(app, origins=[
    "https://frontend-hu04.onrender.com",
    "https://restaurantexpenses.netlify.app"
], supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
    return response

# 🔗 Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["restaurant_db"]
restaurants_collection = db["restaurants"]
expenses_collection = db["expenses"]

@app.route("/api/restaurants/add", methods=["POST"])
def add_restaurant():
    print("Incoming JSON:", request.json)
    try:
        name = request.json.get("name")
        location = request.json.get("location")
        if not name or not location:
            return jsonify({"error": "Missing name or location"}), 400

        new_restaurant = {
            "name": name,
            "location": location
        }
        result = restaurants_collection.insert_one(new_restaurant)
        new_restaurant["_id"] = str(result.inserted_id)
        return jsonify(new_restaurant), 201
    except Exception as e:
        print("Error in POST /api/restaurants:", str(e))
        return jsonify({"error": "Internal server error"}), 500

# -------------------------------
# 🧠 RESTAURANTS ROUTES 
# -------------------------------

@app.route("/api/restaurants", methods=["GET"])
def get_restaurants():
    try:
        restaurants = list(restaurants_collection.find())
        print("Fetched restaurants:", restaurants)  # Debug print
        for r in restaurants:
            r["_id"] = str(r["_id"])
        return jsonify(restaurants)
    except Exception as e:
        print("Error in GET /api/restaurants:", str(e))  # Error log
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/restaurants", methods=["POST"])
def create_restaurant():
    try:
        data = request.get_json(force=True)
        print("Incoming JSON:", data)

        name = data.get("name")
        location = data.get("location")

        if not name or not location:
            print("Missing fields:", name, location)
            return jsonify({"error": "Missing name or location"}), 400

        new_restaurant = {
            "name": name,
            "location": location
        }

        result = restaurants_collection.insert_one(new_restaurant)
        print("Inserted ID:", result.inserted_id)

        new_restaurant["_id"] = str(result.inserted_id)
        return jsonify(new_restaurant), 201

    except Exception as e:
        print("Exception caught:", str(e))
        return jsonify({"error": "Internal server error"}), 500

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# All route definitions above...

print("Flask app started. Routes:", app.url_map)