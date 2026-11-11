from mongodb_connect import db
from datetime import datetime

def record_log(action, target):
    try:
        db.audit_logs.insert_one({
            "operator": "admin",
            "action": action,
            "target": target,
            "timestamp": datetime.now()
        })
    except Exception as e:
        print(f"⚠️ 日志写入失败: {e}")