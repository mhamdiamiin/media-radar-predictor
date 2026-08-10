from app.models.database import articles_collection, alerts_collection

articles_collection.update_many(
    {},
    {"$set": {
        "tendance.score":         0,
        "tendance.label":         None,
        "tendance.is_emerging":   False,
        "tendance.velocity":      0,
        "tendance.score_history": [],
        "alerted":                False
    }}
)

alerts_collection.delete_many({})
print("Reset complete")