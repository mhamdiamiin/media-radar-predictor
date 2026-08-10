import time
from datetime import datetime, timezone
from app.models.database import articles_collection
from app.utils.scoring   import (
    calculate_initial_score,
    determine_label,
    update_confidence
)
from app.utils.ai_agent import review_score
from app.config         import TREND_THRESHOLD


def run_scoring_pipeline():
    print("[scoring] Starting scoring pipeline...")

    articles = list(articles_collection.find({
        "status":              "nlp_done",
        "tendance.cluster_id": {"$ne": None},
        "tendance.label":      {"$in": [None, "revisit"]},
        "tendance.score":      0,
    }))
    if not articles:
        print("[scoring] No articles pending scoring.")
        return

    print(f"[scoring] Scoring {len(articles)} articles...")

    success = 0
    failed  = 0

    for article in articles:
        try:
            sentiment     = article.get("nlp", {}).get("sentiment", {})
            entities      = article.get("nlp", {}).get("entities", [])
            description   = article.get("description", "")
            keywords      = article.get("nlp", {}).get("keywords", [])
            published_at  = article.get("published_at")
            cluster_id    = article.get("tendance", {}).get("cluster_id")
            cluster_label = article.get("tendance", {}).get("label")

            # Step 1 — internal scoring
            initial_score = calculate_initial_score(
                sentiment, entities, description, keywords, published_at
            )
            

            cluster_size = articles_collection.count_documents({
                "tendance.cluster_id": cluster_id
            })  if cluster_id and cluster_id != -1 else 1

            internal_score = update_confidence(initial_score, cluster_size, description)
            if internal_score == 0:
                continue
            # Step 2 — AI agent reviews the score
            # temporarily save internal score so agent can read it
            article["tendance"]["score"] = internal_score

            verdict = review_score(article)

            final_score = verdict["revised_score"]

            if verdict["changed"]:
                print(f"[agent] {article.get('title','')[:45]} "
                      f"| {internal_score} → {final_score} "
                      f"| {verdict['reason']}")

            # Step 3 — determine label from final score
            label = determine_label(final_score, cluster_label)

            score_entry = {
                "score":          final_score,
                "internal_score": internal_score,
                "agent_changed":  verdict["changed"],
                "agent_reason":   verdict["reason"],
                "at":             datetime.now(timezone.utc).isoformat()
            }

            articles_collection.update_one(
                {"_id": article["_id"]},
                {
                    "$set": {
                        "tendance.score":          final_score,
                        "tendance.internal_score": internal_score,
                        "tendance.label":          label,
                        "tendance.is_emerging":    label == "trend",
                        "tendance.velocity":       cluster_size,
                        "tendance.agent_reason":   verdict["reason"],
                        "tendance.agent_changed":  verdict["changed"]
                    },
                    "$push": {
                        "tendance.score_history": score_entry
                    }
                }
            )
            # determine novelty signal
            cluster_id   = article.get("tendance", {}).get("cluster_id")
            cluster_size = articles_collection.count_documents({
                "tendance.cluster_id": cluster_id
            }) if cluster_id and cluster_id != -1 else 1

            # novelty based on cluster size and age
            cluster_age = article.get("tendance", {}).get("cluster_age_days")

            if cluster_id == -1:
                novelty = "sujet entièrement nouveau"
            elif cluster_age is not None and cluster_age > 30:
                novelty = "ancien sujet (plus de 30 jours)"
            elif cluster_age is not None and cluster_age > 7:
                novelty = "sujet en retour (7-30 jours)"
            else:
                novelty = "sujet récent déjà couvert"

            # pass to article dict so agent can read it
            article["_novelty"]      = novelty
            article["_cluster_size"] = cluster_size
            success += 1
            print(f"[scoring] ✓ {article.get('title','')[:50]} → {label} ({final_score})")

            time.sleep(1)  # respect Mistral rate limits

        except Exception as e:
            failed += 1
            print(f"[scoring] ✗ {article.get('url')} — {e}")

    print(f"[scoring] Done — {success} succeeded, {failed} failed.")