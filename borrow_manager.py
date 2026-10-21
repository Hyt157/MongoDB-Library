from mongodb_connect import MongoDBConnect
from datetime import datetime, timezone

class BorrowManager:
    def __init__(self):
        self.client = MongoDBConnect.getConnect()
        self.db = self.client['library']
        self.collection = self.db['borrow_logs']

    def borrow_book(self, reader_card, book_isbn):
        # 借阅登记：插入一条新数据
        record = {
            "reader_card": reader_card,
            "book_isbn": book_isbn,
            "borrow_date": datetime.now(timezone.utc),
            "status": "借出"
        }
        result = self.collection.insert_one(record)
        print(f"[成功] 借阅登记完成，新记录ID: {result.inserted_id}")

    def return_book(self, reader_card, book_isbn):
        # 归还处理：将状态从“借出”改为“已归还”
        result = self.collection.update_many(
            {"reader_card": reader_card, "book_isbn": book_isbn, "status": "借出"},
            {"$set": {
                "status": "已归还",
                "return_date": datetime.now(timezone.utc)
            }}
        )
        if result.modified_count > 0:
            print(f"[成功] 归还处理完成，影响文档数: {result.modified_count}")
        else:
            print("[提示] 未找到该借阅记录，或该书已处于已归还状态。")

    def find_overdue(self):
        # 逾期查询：直接查状态为“逾期”的记录
        results = list(self.collection.find({"status": "逾期"}))
        if not results:
            print("[提示] 暂无逾期记录。")
            return
        for r in results:
            print(f"读者卡号: {r.get('reader_card')}, 图书ISBN: {r.get('book_isbn')}, 借阅日期: {r.get('borrow_date')}")