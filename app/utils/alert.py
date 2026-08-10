from datetime import datetime, timezone
from app.models.database import alerts_collection
from app.config          import ALERT_THRESHOLD


def should_alert(score: float, label: str) -> bool:
    return label == "trend" and score >= ALERT_THRESHOLD


def create_alert(article: dict) -> bool:
    """
    Creates an alert document for a trending article.
    Returns True if alert was created, False if it already existed.
    """
    try:
        alert = {
            "article_id":   article.get("article_id"),
            "url":          article.get("url"),
            "title":        article.get("title"),
            "category":     article.get("category_normalized", "autre"),
            "score":        article.get("tendance", {}).get("score"),
            "published_at": article.get("published_at"),
            "image_url":    article.get("image_url", ""),
            "alerted_at":   datetime.now(timezone.utc),
            "seen":         False
        }

        alerts_collection.insert_one(alert)
        return True

    except Exception as e:
        # duplicate key error means alert already exists for this article
        if "duplicate" in str(e).lower() or "E11000" in str(e):
            return False
        print(f"[alert] Error creating alert: {e}")
        return False