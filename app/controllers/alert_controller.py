from app.models.database import articles_collection
from app.utils.alert     import should_alert, create_alert
from app.config          import ALERT_THRESHOLD


def run_alert_pipeline():
    print("[alerts] Starting alert pipeline...")

    # find all trend articles that haven't been alerted yet
    articles = list(articles_collection.find({
        "tendance.label": "trend",
        "tendance.score": {"$gte": ALERT_THRESHOLD},
        "alerted":        {"$ne": True},
    }))

    if not articles:
        print("[alerts] No new alerts to generate.")
        return

    print(f"[alerts] Checking {len(articles)} trend articles...")

    created = 0
    skipped = 0

    for article in articles:
        score = article.get("tendance", {}).get("score", 0)
        label = article.get("tendance", {}).get("label", "")

        if should_alert(score, label):
            created_alert = create_alert(article)

            if created_alert:
                # mark article as alerted so we don't process it again
                articles_collection.update_one(
                    {"_id": article["_id"]},
                    {"$set": {"alerted": True}}
                )
                created += 1
                print(f"[alerts] ✓ ALERT → {article.get('title','')[:55]} ({score})")
            else:
                skipped += 1

    print(f"[alerts] Done — {created} alerts created, {skipped} already existed.")