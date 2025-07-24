# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests (needed for Streamlit frontend)

# Simulated "Database"
data_store = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

# Auto-increment ID
next_id = 3


@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify(data_store), 200


@app.route('/add_data', methods=['POST'])
def add_data():
    global next_id
    item = request.get_json()
    item["id"] = next_id
    data_store.append(item)
    next_id += 1
    return jsonify({"message": "Data added successfully"}), 201


@app.route('/update_data/<int:item_id>', methods=['PUT'])
def update_data(item_id):
    updated_item = request.get_json()
    for item in data_store:
        if item["id"] == item_id:
            item["name"] = updated_item.get("name", item["name"])
            item["email"] = updated_item.get("email", item["email"])
            return jsonify({"message": "Data updated"}), 200
    return jsonify({"message": "Item not found"}), 404


@app.route('/delete_data/<int:item_id>', methods=['DELETE'])
def delete_data(item_id):
    global data_store
    data_store = [item for item in data_store if item["id"] != item_id]
    return jsonify({"message": "Item deleted"}), 200


if __name__ == 'main':
    app.run(host='0.0.0.0', port=5000)