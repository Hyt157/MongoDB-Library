from mongodb_connect import MongoDBConnect

class BookManager:
    def __init__(self):
        self.client = MongoDBConnect.getConnect()
        self.db = self.client['library']
        self.collection = self.db['books']

    def add_book(self, book_data):
        result = self.collection.insert_one(book_data)
        print(f"[成功] 添加图书，影响文档数: {result.inserted_id}")

    def add_many_books(self, books_list):
        result = self.collection.insert_many(books_list)
        print(f"[成功] 批量添加图书，影响文档数: {len(result.inserted_ids)}")

    def find_books(self, query):
        results = list(self.collection.find(query))
        if not results:
            print("[提示] 未找到符合条件的图书。")
            return
        for book in results:
            print(f"书名: {book.get('title')}, 价格: {book.get('price')}, 库存: {book.get('stock')}")

    def update_book(self, isbn, update_data):
        result = self.collection.update_one({"isbn": isbn}, {"$set": update_data})
        print(f"[成功] 更新图书，影响文档数: {result.modified_count}")

    def delete_book(self, isbn):
        result = self.collection.delete_one({"isbn": isbn})
        print(f"[成功] 删除图书，影响文档数: {result.deleted_count}")

    def delete_many_books(self, query):
        result = self.collection.delete_many(query)
        print(f"[成功] 批量删除图书，影响文档数: {result.deleted_count}")

    def get_top_books(self, limit=5):
        # 对应评分排行功能
        results = self.collection.find().sort("rating", -1).limit(limit)
        print(f"--- 评分 Top {limit} ---")
        for book in results:
            print(f"《{book.get('title')}》 - 评分: {book.get('rating')}")