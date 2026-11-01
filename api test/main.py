from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="TanitWeb Media Radar API")

# Enable CORS for React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Setup
client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
db = client["media_radar"]

@app.get("/")
async def root():
    return {"status": "online", "service": "Media Radar API"}

@app.get("/stats")
async def get_stats():
    articles = db["articles"]
    alerts = db["alerts"]
    return {
        "total":     articles.count_documents({}),
        "trend":     articles.count_documents({"tendance.label": "trend"}),
        "fiddling":  articles.count_documents({"tendance.label": "fiddling"}),
        "mimic":     articles.count_documents({"tendance.label": "mimic"}),
        "alerts":    alerts.count_documents({}),
        "unseen":    alerts.count_documents({"seen": False}),
    }

@app.get("/articles")
async def get_articles(limit: int = 50, skip: int = 0):
    articles = db["articles"]
    # Sort by publication date descending
    cursor = articles.find().sort("published_at", -1).skip(skip).limit(limit)
    res = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if "published_at" in doc and doc["published_at"]:
             doc["published_at"] = doc["published_at"].isoformat()
        res.append(doc)
    return res

@app.get("/alerts")
async def get_alerts():
    alerts = db["alerts"]
    cursor = alerts.find().sort("score", -1)
    res = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if "created_at" in doc and doc["created_at"]:
             doc["created_at"] = doc["created_at"].isoformat()
        res.append(doc)
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
