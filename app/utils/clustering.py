import numpy as np
import hdbscan
from datetime import datetime, timezone
from sklearn.metrics.pairwise import cosine_similarity
from app.models.database import articles_collection
from app.config import (
    CLUSTER_SIMILARITY_THRESHOLD,
    MIMIC_WINDOW_DAYS,
    REVISIT_WINDOW_DAYS
)
import uuid


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize_embeddings(embeddings):
    """L2 normalize embeddings to unit length."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms


# ── Operation 1 — Batch clustering of all existing articles ──────────────────

def build_clusters_from_existing():
    """
    Runs HDBSCAN on all nlp_done articles to discover natural topic groups.
    Assigns cluster_id to each article.
    Called once to initialize clusters from historical data.
    """
    articles = list(articles_collection.find({
        "status":        "nlp_done",
        "nlp.embedding": {"$ne": []}
    }))

    if not articles:
        print("[clustering] No articles found.")
        return

    print(f"[clustering] Building clusters from {len(articles)} articles...")

    embeddings = np.array([a["nlp"]["embedding"] for a in articles])
    embeddings = _normalize_embeddings(embeddings)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=2,
        metric="euclidean",
        cluster_selection_method="eom",
        allow_single_cluster=False
    )
    labels = clusterer.fit_predict(embeddings)

    success = 0
    for article, cluster_id in zip(articles, labels):
        try:
            articles_collection.update_one(
                {"_id": article["_id"]},
                {"$set": {
                    "tendance.cluster_id": int(cluster_id),
                    "tendance.label":      None
                }}
            )
            success += 1
        except Exception as e:
            print(f"[clustering] ✗ {article.get('url')} — {e}")

    unique = len(set(labels)) - (1 if -1 in labels else 0)
    noise  = list(labels).count(-1)
    print(f"[clustering] Done — {success} articles processed.")
    print(f"[clustering] {unique} clusters found, {noise} ungrouped articles.")


# ── Operation 2 — Real time assignment for new articles ──────────────────────

def get_cluster_data():
    """
    Fetches all members of each existing cluster.
    Returns: { cluster_id: { "embeddings": [...], "latest": date, "size": int } }
    """
    pipeline = [
        {
            "$match": {
                "tendance.cluster_id": {"$ne": None, "$gt": -1},
                "nlp.embedding":       {"$ne": []}
            }
        },
        {
            "$group": {
                "_id":        "$tendance.cluster_id",
                "embeddings": {"$push": "$nlp.embedding"},
                "latest":     {"$max": "$published_at"},
                "size":       {"$sum": 1}
            }
        }
    ]

    results = list(articles_collection.aggregate(pipeline))
    cluster_data = {}

    for r in results:
        cluster_id = r["_id"]
        embeddings = np.array(r["embeddings"])
        embeddings = _normalize_embeddings(embeddings)
        cluster_data[cluster_id] = {
            "embeddings": embeddings,
            "centroid":   embeddings.mean(axis=0),
            "latest":     r["latest"],
            "size":       r["size"]
        }

    return cluster_data


def assign_new_article(article):
    """
    Assigns a single new article to an existing cluster or creates a new one.
    Computes max similarity across ALL cluster members (not just centroid).
    Returns the label: "mimic", "revisit", or None (new topic → scoring decides)
    """
    embedding = article.get("nlp", {}).get("embedding", [])

    if not embedding:
        print(f"[clustering] No embedding for {article.get('url')}")
        return

    new_vector = np.array(embedding).reshape(1, -1)
    new_vector = _normalize_embeddings(new_vector)
    cluster_data = get_cluster_data()
    now = datetime.now(timezone.utc)

    best_cluster_id = None
    best_similarity = 0.0
    best_cluster_age = None

    # Compare new article against all existing cluster members
    for cluster_id, data in cluster_data.items():
        embeddings = data["embeddings"]
        # Compute similarity to every member; take the max (best match in cluster)
        similarities = cosine_similarity(new_vector, embeddings)[0]
        max_sim = similarities.max()

        if max_sim > best_similarity:
            best_similarity = max_sim
            best_cluster_id = cluster_id
            latest = data["latest"]

            if latest:
                if latest.tzinfo is None:
                    latest = latest.replace(tzinfo=timezone.utc)
                best_cluster_age = (now - latest).days
            else:
                best_cluster_age = 0

    # Decision: similarity threshold + age-based weighting
    if best_similarity >= CLUSTER_SIMILARITY_THRESHOLD:
        # Article is similar enough to join an existing cluster
        if best_cluster_age <= MIMIC_WINDOW_DAYS:
            label = "mimic"
        elif best_cluster_age <= REVISIT_WINDOW_DAYS:
            label = "revisit"
        else:
            # Cluster too old → treat as new topic
            best_cluster_id = _create_new_cluster_id()
            label = None

    else:
        # No similar cluster found → brand new topic
        best_cluster_id = _create_new_cluster_id()
        label = None

    # Update MongoDB
    articles_collection.update_one(
        {"_id": article["_id"]},
        {"$set": {
            "tendance.cluster_id": best_cluster_id,
            "tendance.cluster_age_days": best_cluster_age,
            "tendance.label": label,
            "tendance.match_confidence": float(best_similarity)
        }}
    )

    return label


def _create_new_cluster_id():
    """
    Generates a new unique cluster ID using UUID string prefix.
    Avoids collisions and scales better than max+1 approach.
    """
    return f"new_{uuid.uuid4().hex[:12]}"