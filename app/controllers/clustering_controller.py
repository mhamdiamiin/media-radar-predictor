from app.utils.clustering import build_clusters_from_existing, assign_new_article
from app.models.database  import articles_collection


def run_clustering_pipeline():
    print("[clustering] Starting clustering pipeline...")

    # Step 1 — find articles that have never been clustered
    unclustered = list(articles_collection.find({
        "status":              "nlp_done",
        "nlp.embedding":       {"$ne": []},
        "tendance.cluster_id": None
    }))

    if not unclustered:
        print("[clustering] No new articles to cluster.")
        return

    print(f"[clustering] {len(unclustered)} new articles to assign...")

    # Step 2 — check if any clusters exist already
    existing = articles_collection.count_documents({
        "tendance.cluster_id": {"$gt": -1}
    })

    if existing == 0:
        # First run ever — build clusters from scratch using HDBSCAN
        print("[clustering] No existing clusters — running full batch clustering...")
        build_clusters_from_existing()
    else:
        # Clusters exist — assign each new article individually
        for article in unclustered:
            label = assign_new_article(article)
            title = article.get("title", article["url"])[:60]
            print(f"[clustering] ✓ {title} → {label if label else 'new topic'}")

    print("[clustering] Clustering pipeline complete.")