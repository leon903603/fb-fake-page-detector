import pandas as pd
from typing import List, Dict, Any

# ===== pages(sheet1) =====
def to_pages_rows(rows: List[Dict[str, Any]], detect_month: str, detect_date: str) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        page_id = str(r.get("page_id", ""))
        out.append({
            "偵測月份": detect_month,
            "偵測日期": detect_date,
            "粉專名稱": r.get("name", ""),
            "profile_id": str(r.get("profile_id", "")),
            "page_id": page_id,
            "粉專連結": r.get("url", ""),
            "廣告庫連結": f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=TW&view_all_page_id={page_id}",
            "下架情況": "未下架",
            "廣告情況": r.get("廣告情況", "沒有"),   # 直接帶上抓到的值
        })
    return out

