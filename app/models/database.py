from pymongo import MongoClient, ASCENDING
from app.config import MONGODB_URL, DB_NAME, COLLECTION_NAME


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DB_NAME]
        self.articles_collection = self.db[COLLECTION_NAME]
        self._ensure_indexes()

    def _ensure_indexes(self):
        self.articles_collection.create_index(
            [("url", ASCENDING)], unique=True
        )
        print("[db] MongoDB connected — unique URL index active.")

    def get_articles_collection(self):
        return self.articles_collection

    def close(self):
        self.client.close()


db_instance = Database()
articles_collection = db_instance.get_articles_collection()
