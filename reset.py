from app.models.database import articles_collection

result = articles_collection.update_many(
    {
        "status": "nlp_done",
        
    },
    {
        "$set": {"status": "completed"}
    }
)

print(f"Reset {result.modified_count} articles back to 'completed'")