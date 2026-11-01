# backend/utils/db.py
import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

# Global client connection
client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
db = client["media_radar"]
articles_collection = db["articles"]
alerts_collection = db["alerts"]

def serialize_doc(doc):
    """Helper to convert MongoDB ObjectId to string for JSON serialization."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

def fetch_articles(query=None, limit=0):
    q = query or {}
    cursor = articles_collection.find(q)
    if limit:
        cursor = cursor.limit(limit)
    return [serialize_doc(doc) for doc in cursor]

def fetch_alerts():
    cursor = alerts_collection.find().sort("score", -1)
    return [serialize_doc(doc) for doc in cursor]

def fetch_stats():
    return {
        "total":     articles_collection.count_documents({}),
        "trend":     articles_collection.count_documents({"tendance.label": "trend"}),
        "fiddling":  articles_collection.count_documents({"tendance.label": "fiddling"}),
        "mimic":     articles_collection.count_documents({"tendance.label": "mimic"}),
        "alerts":    alerts_collection.count_documents({}),
        "unseen":    alerts_collection.count_documents({"seen": False}),
    }

def mark_alert_as_seen(alert_id: str):
    alerts_collection.update_one(
        {"_id": ObjectId(alert_id)},
        {"$set": {"seen": True}}
    )