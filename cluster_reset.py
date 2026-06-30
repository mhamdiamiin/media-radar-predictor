from app.models.database import articles_collection

result = articles_collection.update_many(
    {},
    {"$set": {
        "tendance.cluster_id":       None,
        "tendance.cluster_age_days": None,
        "tendance.label":            None
    }}
)

print(f"Reset clusters for {result.modified_count} articles")