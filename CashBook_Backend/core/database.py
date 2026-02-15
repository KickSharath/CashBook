from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .config import settings

MONGO_USERNAME = settings.MONGO_USERNAME
MONGO_PASSWORD = settings.MONGO_PASSWORD
MONGO_HOST = settings.MONGO_HOST
MONGO_DB = settings.MONGO_DB

uri = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}/{MONGO_DB}?retryWrites=true&w=majority"

def conn_mongo_client():
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        return client
    except Exception as e:
        print(e)
        return None