from datetime import datetime, timezone
from app.models.database import articles_collection, alerts_collection
from app.config          import ALERT_THRESHOLD


def should_alert(score: float, label: str) -> bool:
    return label == "trend" and score >= ALERT_THRESHOLD


def create_alert(article: dict) -> bool:
    try:
        alert = {
            "article_id":   article.get("article_id"),
            "url":          article.get("url"),
            "title":        article.get("title"),
            "category":     article.get("category_normalized", "autre"),
            "score":        article.get("tendance", {}).get("score"),
            "published_at": article.get("published_at"),
            "alerted_at":   datetime.now(timezone.utc),
            "image_url":    article.get("image_url", ""),
            "seen":         False
        }
        alerts_collection.insert_one(alert)
        return True

    except Exception as e:
        if "duplicate" in str(e).lower() or "E11000" in str(e):
            return False
        print(f"[alert] Error creating alert: {e}")
        return False