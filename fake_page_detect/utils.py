from datetime import datetime

def get_today_info():
    now = datetime.now()
    detect_month = now.strftime("%Y-%m")             # 例如 2025-08
    detect_date = now.strftime("%Y-%m-%d %H:%M")  # 例如 2025-08-07 15:30
    return detect_month, detect_date