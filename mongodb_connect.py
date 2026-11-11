import os
from pymongo import MongoClient

class MongoDBConnect:
    # 默认连本地，允许通过环境变量 MONGO_URI 覆盖
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    
    @staticmethod
    def getConnect(uri=MONGO_URI):
        client = MongoClient(uri, serverSelectionTimeoutMS=2000) # 缩短超时
        return client

client = MongoDBConnect.getConnect()
db = client['library']