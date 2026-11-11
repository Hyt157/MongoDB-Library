import gridfs
import os
from mongodb_connect import db

fs = gridfs.GridFS(db)

# 使用动态绝对路径，解决硬编码问题
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRIDFS_DIR = os.path.join(BASE_DIR, "gridfs_files")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

def upload_all_files():
    if not os.path.exists(GRIDFS_DIR):
        os.makedirs(GRIDFS_DIR)
        print(f"⚠️ 缺少文件目录，已自动创建: {GRIDFS_DIR}，请放入PDF和图片后重试。")
        return

    files = [
        ("ebook_1.pdf", "9787115428028", "ebook"),
        ("ebook_2.pdf", "9787111544937", "ebook"),
        ("ebook_3.pdf", "9787121310925", "ebook"),
        ("cover_1.png", "9787115428028", "cover"),
        ("cover_2.png", "9787111544937", "cover"),
        ("cover_3.png", "9787121310925", "cover")
    ]
    for filename, isbn, ftype in files:
        path = os.path.join(GRIDFS_DIR, filename)
        if os.path.exists(path):
            with open(path, "rb") as f:
                if not fs.exists({"filename": filename}):
                    fs.put(f, filename=filename, metadata={"isbn": isbn, "file_type": ftype})
                    print(f"✅ 已上传: {filename}")
                else:
                    print(f"⏩ 已存在跳过: {filename}")

def download_by_title(title):
    book = db.books.find_one({"title": title})
    if not book or "ebook_name" not in book:
        print(f"❌ 未找到 '{title}' 相关的电子书。")
        return
    ebook_name = book["ebook_name"]
    file_data = fs.find_one({"filename": ebook_name})
    if not file_data:
        print(f"❌ GridFS 中未找到文件: {ebook_name}")
        return
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    save_path = os.path.join(DOWNLOAD_DIR, file_data.filename)
    with open(save_path, "wb") as f:
        f.write(file_data.read())
    print(f"📥 下载完成: {save_path}")
    print(f"📊 字节校验: 数据库 {file_data.length} 字节 | 本地 {os.path.getsize(save_path)} 字节")

def list_files():
    print("--- GridFS 文件清单 ---")
    for f in fs.find():
        upload_time = f.upload_date.strftime('%Y-%m-%d %H:%M:%S')
        print(f"📄 {f.filename} | {round(f.length / 1024, 2)} KB | {upload_time}")