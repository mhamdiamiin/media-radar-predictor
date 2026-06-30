from app.models.database import articles_collection
from app.utils.sentiment import analyze_sentiment
from app.utils.keywords import extract_keywords
from app.utils.entities import extract_entities
from app.utils.embeddings import generate_embedding
from datetime import datetime, timezone
from app.utils.category_classifier import classify_category


def run_nlp_pipeline():
    # Fetch all articles that completed scraping but not yet NLP processed
    pending = list(articles_collection.find({"status": "completed"}))

    if not pending:
        print("[nlp] No articles pending NLP processing.")
        return

    print(f"[nlp] Processing {len(pending)} articles...")

    success = 0
    failed  = 0

    for article in pending:
        try:
            title       = article.get("title", "")
            description = article.get("description", "")
            tags        = article.get("tags", [])

            # Run all four NLP tasks
            sentiment  = analyze_sentiment(description)
            keywords   = extract_keywords(title, description, tags)
            entities   = extract_entities(title, description)
            embedding  = generate_embedding(description)
            category_normalized = classify_category(article.get("category", ""))

            # Update MongoDB document
            articles_collection.update_one(
                {"_id": article["_id"]},
                {"$set": {
                    "nlp.sentiment":  sentiment,
                    "nlp.keywords":   keywords,
                    "nlp.entities":   entities,
                    "nlp.embedding":  embedding,
                    "status":         "nlp_done",
                    "nlp_processed_at": datetime.now(timezone.utc),
                    "category_normalized": category_normalized
                }}
            )
            success += 1
            print(f"[nlp] ✓ {article.get('title', article['url'])[:60]}")

        except Exception as e:
            failed += 1
            print(f"[nlp] ✗ Failed on {article.get('url')} — {e}")
            articles_collection.update_one(
                {"_id": article["_id"]},
                {"$set": {"status": "nlp_failed"}}
            )

    print(f"[nlp] Done — {success} succeeded, {failed} failed.")