import sys
from mongodb_connect import MongoDBConnect
from book_manager import BookManager
from reader_manager import ReaderManager
from borrow_manager import BorrowManager
from stat_manager import StatManager


def main():
    client = MongoDBConnect.getConnect()
    db = client['library']

    # 启动时打印状态与各集合文档总数
    print("=" * 40)
    print("欢迎使用图书管理系统")
    try:
        print(f"[状态] 数据库连接成功！")
        print(f"[数据] books: {db['books'].count_documents({})} 条")
        print(f"[数据] readers: {db['readers'].count_documents({})} 条")
        print(f"[数据] borrow_logs: {db['borrow_logs'].count_documents({})} 条")
    except Exception as e:
        print(f"[错误] 数据库连接失败: {e}")
        sys.exit(1)
    print("=" * 40)

    book_mgr = BookManager()
    reader_mgr = ReaderManager()
    borrow_mgr = BorrowManager()
    stat_mgr = StatManager()

    while True:
        print("\n--- 菜单 ---")
        print("1. 检索图书 (价格>50)")
        print("2. 图书评分排行 Top 5")
        print("3. 统计各学院人数")
        print("4. 统计读者等级分布")
        print("5. 借阅登记 (测试)")
        print("6. 归还处理 (测试)")
        print("7. 查询逾期记录")
        print("8. 生成统计报表 (分类/趋势/畅销榜)")
        print("0. 退出")

        choice = input("请选择功能 (0-8): ")

        if choice == '1':
            book_mgr.find_books({"price": {"$gt": 50}})
        elif choice == '2':
            book_mgr.get_top_books(5)
        elif choice == '3':
            reader_mgr.get_all_colleges()
        elif choice == '4':
            reader_mgr.get_level_distribution()
        elif choice == '5':
            # 测试用例，使用真实的isbn和card_no
            borrow_mgr.borrow_book("R20240001", "9787115428028")
        elif choice == '6':
            borrow_mgr.return_book("R20240001", "9787115428028")
        elif choice == '7':
            borrow_mgr.find_overdue()
        elif choice == '8':
            stat_mgr.category_statistics()
            stat_mgr.borrow_trend()
            stat_mgr.bestsellers()
        elif choice == '0':
            print("退出系统...")
            break
        else:
            print("[错误] 输入无效，请重新输入！")

    # 退出前关闭数据库连接
    client.close()
    print("数据库连接已安全关闭。")


if __name__ == '__main__':
    main()