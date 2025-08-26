import pandas as pd
from typing import List, Dict

# ===== 常數 =====
PAGES_SHEET = "pages"
PAGES_COLS = [
    "偵測日期","粉專名稱","profile_id","page_id",
    "粉專連結","廣告庫連結","下架情況","廣告情況"
]

# ===== 讀寫 =====
def load_pages(excel_path: str) -> pd.DataFrame:
    """只讀 pages 工作表"""
    xls = pd.ExcelFile(excel_path)
    if PAGES_SHEET not in xls.sheet_names:
        raise ValueError(f"Excel 必須包含工作表: {PAGES_SHEET}")
    pages_df = pd.read_excel(excel_path, sheet_name=PAGES_SHEET)
    return pages_df

def save_pages(excel_path: str, pages_df: pd.DataFrame):
    """只寫 pages 工作表"""
    with pd.ExcelWriter(excel_path, engine="openpyxl") as w:
        pages_df.to_excel(w, sheet_name=PAGES_SHEET, index=False)

# ===== pages 操作 =====
def upsert_pages_with_ads(pages_df: pd.DataFrame, new_pages: List[Dict]) -> pd.DataFrame:
    """
    新增/更新粉專資料，並自動更新廣告情況
    規則：profile_id 唯一，新資料覆蓋舊資料
    """
    if not new_pages:
        return pages_df

    add_df = pd.DataFrame(new_pages).copy()

    # 確保所有欄位都有
    cols = ["偵測日期","粉專名稱","profile_id","page_id","粉專連結",
            "下架情況","廣告情況","廣告庫連結","頭像連結"]
    for c in cols:
        if c not in add_df.columns:
            add_df[c] = ""

    add_df = add_df[cols]

    # 統一 profile_id 字串
    add_df["profile_id"] = add_df["profile_id"].astype(str)
    base = pages_df.copy()
    if not base.empty:
        base["profile_id"] = base["profile_id"].astype(str)
        # 將舊資料中同 profile_id 的刪掉
        base = base[~base["profile_id"].isin(set(add_df["profile_id"]))]

        # 更新廣告情況，如果新資料有廣告就覆蓋舊資料
        for i, row in base.iterrows():
            pid = row["profile_id"]
            if pid in add_df["profile_id"].values:
                new_status = add_df.loc[add_df["profile_id"]==pid, "廣告情況"].values[0]
                if new_status == "有":
                    base.at[i, "廣告情況"] = "有"
                elif row["廣告情況"] == "有":
                    base.at[i, "廣告情況"] = "曾有"
                elif row["廣告情況"] not in ("曾有","沒有"):
                    base.at[i, "廣告情況"] = "沒有"

    merged = pd.concat([base, add_df], ignore_index=True)
    return merged


# ===== 下架標記 =====
def mark_pages_down(pages_df: pd.DataFrame, alive_profile_ids: set) -> pd.DataFrame:
    """在 alive 的標 '未下架'；其餘標 '已下架'。"""
    if pages_df.empty:
        return pages_df
    alive = {str(x) for x in alive_profile_ids}
    out = pages_df.copy()
    out["profile_id"] = out["profile_id"].astype(str)
    out["下架情況"] = out["profile_id"].apply(lambda x: "未下架" if x in alive else "已下架")
    return out
