import sys
from datetime import datetime
from mongodb_connect import MongoDBConnect
import file_manager
import log_manager

def main():
    client = MongoDBConnect.getConnect()
    db = client['library']

    print("=" * 55)
    print("欢迎使用智慧图书馆数字资源平台")
    
    try:
        client.admin.command('ping') # 测试连接
        print(f"[状态] 数据库连接成功！")
        print(f"[数据] books: {db['books'].count_documents({})} 条")
        print(f"[数据] readers: {db['readers'].count_documents({})} 条")
        print(f"[数据] borrow_logs: {db['borrow_logs'].count_documents({})} 条")
    except Exception as e:
        print(f"[警告] 数据库未连接，请检查环境变量 MONGO_URI 配置。")
        print(f"[提示] 程序将继续显示菜单，但部分功能可能无法使用。")
    print("=" * 55)
    
    # 后面的 while True: 等等代码保持原样不动...

    while True:
        print("\n--- 智慧图书馆平台 菜单 ---")
        print("1. 基础检索 (价格>50)")
        print("2. 高级组合检索 (类别+价格)")
        print("3. 高级组合检索 (多标签匹配)")
        print("4. 高级组合检索 (书名模糊)")
        print("5. 高级组合检索 (年份范围)")
        print("6. 数据质量核查 (查缺少 tags 的图书)")
        print("7. 图书评分排行 Top 10")
        print("8. 统计各学院借阅总量 Top 5")
        print("9. 生成分类统计并写入新集合")
        print("10. 上传电子书与封面至 GridFS")
        print("11. 按书名下载电子书并校验")
        print("12. 查看 GridFS 文件清单")
        print("13. 新增图书 (记录操作日志)")
        print("14. 删除图书 (记录操作日志)")
        print("0. 退出")

        choice = input("请选择功能 (0-14): ")

        if choice == '1':
            print("\n[基础检索] 价格 > 50 的图书：")
            for b in db.books.find({"price": {"$gt": 50}}, {"title": 1, "price": 1, "_id": 0}).limit(5):
                print(f"  - {b['title']} (￥{b['price']})")
            print(f"  ...共找到 {db.books.count_documents({'price': {'$gt': 50}})} 条")

        elif choice == '2':
            count = db.books.count_documents({"category": "文学", "price": {"$gte": 30, "$lte": 80}})
            print(f"\n[组合检索] 文学类且价格30-80的图书共: {count} 条")

        elif choice == '3':
            count = db.books.count_documents({"tags": {"$all": ["编程", "入门"]}})
            print(f"\n[组合检索] 同时包含'编程'和'入门'标签的图书共: {count} 条")

        elif choice == '4':
            count = db.books.count_documents({"title": {"$regex": "计算机"}})
            print(f"\n[组合检索] 书名包含'计算机'的图书共: {count} 条")

        elif choice == '5':
            count = db.books.count_documents(
                {"publish_date": {"$gte": datetime(2020, 1, 1), "$lte": datetime(2023, 12, 31)}})
            print(f"\n[组合检索] 2020-2023年出版的图书共: {count} 条")

        elif choice == '6':
            count = db.books.count_documents({"tags": {"$exists": False}})
            print(f"\n[数据质量] 缺少 tags 字段的图书共: {count} 条")

        elif choice == '7':
            print("\n[评分排行] Top 10 图书：")
            for b in db.books.find({}, {"title": 1, "author": 1, "rating": 1, "_id": 0}).sort("rating", -1).limit(10):
                print(f"  《{b['title']}》 | 作者: {b['author']} | 评分: {b['rating']}")

        elif choice == '8':
            print("\n[学院统计] 借阅总量 Top 5：")
            pipeline = [
                {"$group": {"_id": "$reader_card", "count": {"$sum": 1}}},
                {"$lookup": {"from": "readers", "localField": "_id", "foreignField": "card_no", "as": "r"}},
                {"$unwind": "$r"},
                {"$group": {"_id": "$r.college", "total": {"$sum": "$count"}}},
                {"$sort": {"total": -1}}, {"$limit": 5}
            ]
            for res in db.borrow_logs.aggregate(pipeline):
                print(f"  - {res['_id']}: {res['total']} 次")

        elif choice == '9':
            print("\n[数据导出] 正在统计各类别藏书量并写入 category_stats 集合...")
            db.books.aggregate([
                {"$group": {"_id": "$category", "stock": {"$sum": "$stock"}}},
                {"$out": "category_stats"}
            ])
            print("  ✅ 分类统计结果已成功写入新集合！")
            log_manager.record_log("导出数据", "分类统计category_stats")

        elif choice == '10':
            file_manager.upload_all_files()
            log_manager.record_log("批量上传文件", "gridfs_files")

        elif choice == '11':
            t = input("请输入要下载的书名 (例如: 深入理解计算机系统（第3版）): ")
            file_manager.download_by_title(t)
            log_manager.record_log("下载电子书", t)

        elif choice == '12':
            file_manager.list_files()

        elif choice == '13':
            print("\n--- 新增图书 ---")
            new_isbn = input("请输入13位ISBN: ")
            new_title = input("请输入书名: ")

            # 简单的输入校验
            try:
                new_price = float(input("请输入价格: "))
            except ValueError:
                print("❌ 价格输入错误，请输入数字！")
                continue

            # 检查是否已存在
            if db.books.find_one({"isbn": new_isbn}):
                print(f"❌ 新增失败：ISBN {new_isbn} 已存在！")
            else:
                # 真实插入
                new_book = {"isbn": new_isbn, "title": new_title, "price": new_price}
                db.books.insert_one(new_book)
                print(f"✅ 成功新增图书：《{new_title}》")

                # 真实写入日志
                log_manager.record_log("新增图书", f"《{new_title}》(ISBN:{new_isbn})")

        elif choice == '14':
            print("\n--- 删除图书 ---")
            del_isbn = input("请输入要删除的图书ISBN: ")

            # 真实删除
            res = db.books.delete_one({"isbn": del_isbn})
            if res.deleted_count > 0:
                print(f"✅ 成功删除 ISBN 为 {del_isbn} 的图书")

                # 真实写入日志
                log_manager.record_log("删除图书", f"ISBN:{del_isbn}")
            else:
                print(f"❌ 删除失败：未找到 ISBN 为 {del_isbn} 的图书")

        elif choice == '0':
            print("退出系统...")
            break
        else:
            print("[错误] 输入无效，请重新输入！")

    client.close()
    print("数据库连接已安全关闭。")


if __name__ == '__main__':
    main()