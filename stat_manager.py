from mongodb_connect import MongoDBConnect


class StatManager:
    def __init__(self):
        self.client = MongoDBConnect.getConnect()
        self.db = self.client['library']
        self.books = self.db['books']
        self.borrows = self.db['borrow_logs']

    def category_statistics(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "total_stock": {"$sum": "$stock"},
                    "avg_price": {"$avg": "$price"},
                    "book_count": {"$sum": 1}
                }
            },
            {"$sort": {"total_stock": -1}}
        ]

        results = list(self.books.aggregate(pipeline))
        print("\n=== 分类统计报表 ===")
        if not results:
            print("[提示] 无数据")
            return

        for item in results:
            # 【修复点】安全处理可能为空的价格
            avg_price = item.get('avg_price')
            if avg_price is None:
                avg_price_str = "未知"
            else:
                avg_price_str = f"{avg_price:.2f}"

            print(
                f"类别: {item['_id']} | 库存: {item['total_stock']} | 均价: {avg_price_str} | 数量: {item['book_count']}")

    def borrow_trend(self):
        pipeline = [
            {
                "$group": {
                    "_id": {"$year": "$borrow_date"},
                    "borrow_count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]

        results = list(self.borrows.aggregate(pipeline))
        print("\n=== 借阅趋势报表 ===")
        if not results:
            print("[提示] 无数据")
            return

        for item in results:
            # 防止因为没有年份导致 _id 为 None
            year = item['_id'] if item['_id'] is not None else "未知年份"
            print(f"年份: {year} 年 | 借阅量: {item['borrow_count']} 次")

    def bestsellers(self):
        # 畅销榜直接利用 books 里的 borrow_count 字段
        results = self.books.find({}, {"title": 1, "borrow_count": 1, "_id": 0}).sort("borrow_count", -1).limit(10)

        print("\n=== 畅销榜 TOP 10 ===")
        count = 0
        for item in results:
            count += 1
            title = item.get('title', '未知书名')
            borrow_count = item.get('borrow_count', 0)
            print(f"第 {count} 名: 《{title}》 | 借阅量: {borrow_count} 次")

        if count == 0:
            print("[提示] 无数据")