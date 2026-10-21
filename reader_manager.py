from mongodb_connect import MongoDBConnect

class ReaderManager:
    def __init__(self):
        self.client = MongoDBConnect.getConnect()
        self.db = self.client['library']
        self.collection = self.db['readers']

    def get_all_colleges(self):
        # 对应 distinct：获取所有不重复的学院
        colleges = self.collection.distinct("college")
        print(f"[统计] 共有 {len(colleges)} 个学院: {', '.join(colleges)}")

    def get_level_distribution(self):
        # 对应 count_documents：统计各等级人数
        levels = ["普通", "高级", "教师"]
        for level in levels:
            count = self.collection.count_documents({"level": level})
            print(f"[统计] 等级为 '{level}' 的读者人数: {count}")

    def find_readers(self, query):
        results = list(self.collection.find(query))
        if not results:
            print("[提示] 未找到符合条件的读者。")
            return
        for reader in results:
            print(f"姓名: {reader.get('name')}, 学院: {reader.get('college')}, 等级: {reader.get('level')}")