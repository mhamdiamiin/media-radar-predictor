import os
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_db():
    client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
    return client["media_radar"]

def get_collections():
    db = get_db()
    return db["articles"], db["alerts"]

@st.cache_data(ttl=300)
def fetch_articles(query=None, limit=0):
    articles, _ = get_collections()
    q = query or {}
    cursor = articles.find(q)
    if limit:
        cursor = cursor.limit(limit)
    return list(cursor)

@st.cache_data(ttl=300)
def fetch_alerts():
    _, alerts = get_collections()
    return list(alerts.find().sort("score", -1))

@st.cache_data(ttl=300)
def fetch_stats():
    articles, alerts = get_collections()
    return {
        "total":     articles.count_documents({}),
        "trend":     articles.count_documents({"tendance.label": "trend"}),
        "fiddling":  articles.count_documents({"tendance.label": "fiddling"}),
        "mimic":     articles.count_documents({"tendance.label": "mimic"}),
        "alerts":    alerts.count_documents({}),
        "unseen":    alerts.count_documents({"seen": False}),
    }