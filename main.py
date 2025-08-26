import asyncio, random, pandas as pd, os
from playwright.async_api import async_playwright
from urllib.parse import quote_plus

from config import KEYWORDS, EXCEL_PATH, SCROLL_TIMES
from utils import get_today_info
from excel_utils import load_pages, save_pages, mark_pages_down, upsert_pages_with_ads
from converters import to_pages_rows
from scraper import search_pages, resolve_page_id, scrape_ads_for_page

STATE_PATH = "facebook_state.json"

async def ensure_login_state():
    """若沒有 facebook_state.json，開瀏覽器讓使用者登入並保存 json"""
    if os.path.exists(STATE_PATH):
        print("[login] 找到 facebook_state.json，直接使用")
        return

    print("[login] 未找到 facebook_state.json，請登入 Facebook")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.facebook.com/")
        print("請在開啟的瀏覽器登入 Facebook，登入完成後按 Enter 繼續...")
        input()
        # 儲存登入狀態
        await context.storage_state(path=STATE_PATH)
        await browser.close()
        print(f"[login] 已生成 {STATE_PATH}")

async def jitter_sleep(base: float = 1.0, spread: float = 0.8):
    await asyncio.sleep(base + random.random() * spread)

async def search_with_retries(context, keyword: str, scroll_times: int, attempts: int = 3):
    enc_kw = quote_plus(keyword)
    for i in range(attempts):
        rows = await search_pages(context, enc_kw, scroll_times=scroll_times + i)
        if rows: return rows
        await jitter_sleep(1.2, 1.0)
    return await search_pages(context, keyword, scroll_times=scroll_times + 2)

async def run_cycle():
    detect_month, detect_date = get_today_info()

    try:
        pages_df = load_pages(EXCEL_PATH)
    except Exception:
        pages_df = pd.DataFrame(columns=[
            "偵測日期","粉專名稱","profile_id","page_id",
            "粉專連結","廣告庫連結","下架情況","廣告情況"
        ])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=STATE_PATH, locale="zh-TW")

        # STEP1：搜尋關鍵字 → 新粉專 (同時檢查廣告)
        for kw in KEYWORDS:
            print(f"[pages] 搜尋關鍵字: {kw}")
            rows = await search_with_retries(context, kw, scroll_times=SCROLL_TIMES)
            print(f"[pages]  ➜ 找到 {len(rows)} 個粉專")

            for r in rows:
                r["profile_id"] = str(r["profile_id"])  # 保險措施
                if not r.get("page_id"):
                    r["page_id"] = await resolve_page_id(context, r["profile_id"])
                print(f"    - profile_id={r['profile_id']} → page_id={r['page_id']}")

                # 在這裡就查廣告
                print(f"[ads] 抓取粉專 {r['page_id']} {r['name']} 的廣告...")
                ads_list = await scrape_ads_for_page(context, r["page_id"])
                r["廣告情況"] = "有" if ads_list else "沒有"
                await jitter_sleep(1.0, 1.0)

            pages_rows = to_pages_rows(rows, detect_month, detect_date)
            pages_df = upsert_pages_with_ads(pages_df, pages_rows)
            await jitter_sleep(1.0, 1.0)

        # STEP2：標記下架
        alive_profile_ids = set(pages_df["profile_id"].astype(str))
        pages_df = mark_pages_down(pages_df, alive_profile_ids)

        # 存回 Excel
        save_pages(EXCEL_PATH, pages_df)
        await browser.close()

async def main():
    await ensure_login_state()
    await run_cycle()

if __name__ == "__main__":
    asyncio.run(main())
