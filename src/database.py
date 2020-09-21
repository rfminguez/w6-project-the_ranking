from pymongo import MongoClient
from src.config import DB_URL

client = MongoClient(DB_URL)
db = client.get_database()