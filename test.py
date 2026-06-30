from app.models.database import articles_collection

pipeline = [
    {"$match": {"tendance.cluster_id": {"$ne": None}}},
    {"$group": {
        "_id": "$tendance.cluster_id",
        "count": {"$sum": 1},
        "titles": {"$push": "$title"}
    }},
    {"$sort": {"count": -1}}
]

results = list(articles_collection.aggregate(pipeline))
for r in results:
    label = "NOISE" if r["_id"] == -1 else f"Cluster {r['_id']}"
    print(f"\n{label} → {r['count']} articles")
    for t in r["titles"][:5]:
        print(f"   - {t[:70]}")