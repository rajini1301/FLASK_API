from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# Connect to local MongoDB instance
client = MongoClient("mongodb://localhost:27017")
db = client["userdb"]
collection = db["users"]

# Helper: Convert MongoDB ObjectId to string without modifying original
def serialize_user(user):
    return {
        "_id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", "")
    }

# Route: Get all users
@app.route('/get_data', methods=['GET'])
def get_data():
    users = list(collection.find())
    users = [serialize_user(user) for user in users]
    return jsonify(users), 200

# Route: Add a new user
@app.route('/add_data', methods=['POST'])
def add_data():
    user = request.get_json()
    if not user.get("name") or not user.get("email"):
        return jsonify({"message": "Name and Email are required"}), 400

    result = collection.insert_one(user)
    return jsonify({
        "message": "User added successfully",
        "id": str(result.inserted_id)
    }), 201

# Route: Update user by ID
@app.route('/update_data/<string:user_id>', methods=['PUT'])
def update_data(user_id):
    updated_user = request.get_json()
    if not updated_user.get("name") or not updated_user.get("email"):
        return jsonify({"message": "Name and Email are required"}), 400

    try:
        result = collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updated_user}
        )
        if result.matched_count == 0:
            return jsonify({"message": "User not found"}), 404
        return jsonify({"message": "User updated"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400

# Route: Delete user by ID
@app.route('/delete_data/<string:user_id>', methods=['DELETE'])
def delete_data(user_id):
    try:
        result = collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"message": "User not found"}), 404
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




import streamlit as st
import requests

BASE_URL = "http://localhost:5000"  # Replace with Render URL when deployed

st.set_page_config(page_title="User Manager", layout="centered")
st.title("📋 User Management Dashboard")

# Utility to fetch all data
def fetch_data():
    res = requests.get(f"{BASE_URL}/get_data")
    return res.json() if res.status_code == 200 else []

# Add new user
def add_user(name, email):
    res = requests.post(f"{BASE_URL}/add_data", json={"name": name, "email": email})
    return res.ok

# Update user
def update_user(user_id, name, email):
    res = requests.put(f"{BASE_URL}/update_data/{user_id}", json={"name": name, "email": email})
    return res.ok

# Delete user
def delete_user(user_id):
    res = requests.delete(f"{BASE_URL}/delete_data/{user_id}")
    return res.ok

# Sidebar for actions
menu = st.sidebar.selectbox("Choose Action", ["View Users", "Add User"])

if menu == "Add User":
    st.subheader("➕ Add New User")
    with st.form("add_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Add")
        if submitted:
            if add_user(name, email):
                st.success("User added successfully!")
            else:
                st.error("Failed to add user")

else:
    st.subheader("👥 User List")
    data = fetch_data()
    if not data:
        st.info("No users found.")
    for item in data:
        user_id = str(item["_id"])  # Ensure ObjectId is converted to string
        with st.expander(f"{item['name']} ({item['email']})"):
            new_name = st.text_input(f"Name_{user_id}", value=item['name'])
            new_email = st.text_input(f"Email_{user_id}", value=item['email'])
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"update_{user_id}"):
                    if update_user(user_id, new_name, new_email):
                        st.success("User updated!")
                    else:
                        st.error("Update failed")
            with col2:
                if st.button("Delete", key=f"delete_{user_id}"):
                    if delete_user(user_id):
                        st.success("User deleted!")

    st.caption("🔁 Refresh the page to load latest changes.")

