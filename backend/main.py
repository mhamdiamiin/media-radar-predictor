# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.db import fetch_articles, fetch_alerts, fetch_stats, mark_alert_as_seen

app = FastAPI(title="EcoTrend API")

# Allow React (which will run on port 5173) to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"status": "EcoTrend API is running! 🚀", "docs": "/docs"}

@app.get("/api/stats")
def get_dashboard_stats():
    return fetch_stats()

@app.get("/api/alerts")
def get_alerts():
    return fetch_alerts()

@app.post("/api/alerts/{alert_id}/seen")
def mark_alert_seen(alert_id: str):
    mark_alert_as_seen(alert_id)
    return {"message": "Alert marked as seen", "id": alert_id}

@app.get("/api/articles")
def get_articles(limit: int = 100):
    return fetch_articles(limit=limit)
    
@app.get("/api/clusters")
def get_clusters():
    query = {"tendance.cluster_id": {"$nin": [None, -1]}}
    return fetch_articles(query=query)