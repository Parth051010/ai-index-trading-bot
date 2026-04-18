from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client["trading_bot"]

users = db["users"]

def create_user(username, password):
    if users.find_one({"username": username}):
        return False

    users.insert_one({
        "username": username,
        "password": password,
        "balance": 50000,
        "history": [],
        "active_trade": None
    })
    return True


def get_user(username):
    return users.find_one({"username": username})


def update_user(username, data):
    users.update_one({"username": username}, {"$set": data})