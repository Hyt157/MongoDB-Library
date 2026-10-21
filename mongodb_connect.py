from pymongo import MongoClient

class MongoDBConnect:
    # 这里使用的是你虚拟机的 IP 和 MongoDB 默认端口
    default_uri = "mongodb://192.168.121.134:27017"

    @staticmethod
    def getConnect(uri=default_uri):
        client = MongoClient(uri)
        return client