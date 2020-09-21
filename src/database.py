from pymongo import MongoClient
from config import DB_URL

# Creo la conexión con las base de datos
client = MongoClient(DB_URL)
db = client.get_database()