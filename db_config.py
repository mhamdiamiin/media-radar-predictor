from pymongo import MongoClient, ASCENDING
 
client               = MongoClient("mongodb://localhost:27017/")
db                   = client["media_radar"]
articles_collection  = db["articles"]
 
# Unique index on URL — prevents duplicate articles at DB level
articles_collection.create_index([("url", ASCENDING)], unique=True)
 
print("[db_config] MongoDB connected — unique URL index active.")