# scraper.py
import asyncio, re
from typing import List, Dict, Any
from playwright.async_api import Page, BrowserContext

# -------------------------
# 小工具：捲動
# -------------------------
async def _scroll_down(page: Page, times: int = 5, pause: float = 2.0):
    for _ in range(times):
        await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
        await asyncio.sleep(pause)

# -------------------------
# 搜尋粉專
# -------------------------
_ID_RE = re.compile(r'profile\.php\?id=(\d+)')

async def search_pages(context: BrowserContext, keyword: str, scroll_times: int = 5) -> List[Dict[str, Any]]:
    page = await context.new_page()
    url = f'https://www.facebook.com/search/pages?q={keyword}'
    try:
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        await _scroll_down(page, times=scroll_times)
    except Exception as e:
        print(f"[pages] load error for '{keyword}': {e}")
        await page.close()
        return []

    anchors = await page.locator('a[href*="/profile.php?id="]').all()
    dedup: Dict[str, Dict[str, Any]] = {}
    for a in anchors:
        try:
            href = await a.get_attribute('href')
            if not href or "/search/" in href: continue
            pid_match = _ID_RE.search(href.split("&")[0])
            if not pid_match: continue
            pid = pid_match.group(1)
            clean_url = f"https://www.facebook.com/{pid}"
            name = (await a.inner_text()).strip()

            avatar = ""
            img = a.locator("img")
            if await img.count() > 0:
                avatar = (await img.first.get_attribute("src")) or ""

            if pid not in dedup:
                dedup[pid] = {"name": name, "profile_id": pid, "url": clean_url, "avatar": avatar}
            else:
                if name: dedup[pid]["name"] = name
                if avatar: dedup[pid]["avatar"] = avatar
        except Exception as e:
            print(f"[pages] parse anchor error: {e}")

    await page.close()
    return list(dedup.values())

# -------------------------
# 解析 page_id（優先資訊透明度）
# -------------------------
_RX_PAGEID_JSON  = re.compile(r'"pageID"\s*:\s*"(\d+)"')

async def resolve_page_id(context: BrowserContext, profile_id: str) -> str:
    urls = [
        f"https://www.facebook.com/profile.php?id={profile_id}&sk=about_profile_transparency",
        f"https://m.facebook.com/profile.php?id={profile_id}&sk=about_profile_transparency",
    ]
    for url in urls:
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(1.5)
            spans = page.locator("span")
            for i in range(await spans.count()):
                text = await spans.nth(i).text_content()
                if text and re.fullmatch(r"\d{15,16}", text.strip()):
                    return text.strip()
        except Exception:
            pass
        finally:
            await page.close()
    return profile_id  # 回退原 profile_id

# -------------------------
# 抓廣告（已解析 page_id）
# -------------------------
from playwright.async_api import BrowserContext
import asyncio
import re

async def scrape_ads_for_page(context: BrowserContext, profile_id: str) -> bool:
    """
    判斷粉專是否有廣告：
    - 直接使用 profile_id 進資訊透明度頁
    - 回傳 True / False
    """
    if not profile_id:
        print(f"[ads] profile_id 空值")
        return False

    urls = [
        f"https://www.facebook.com/profile.php?id={profile_id}&sk=about_profile_transparency",
        f"https://m.facebook.com/profile.php?id={profile_id}&sk=about_profile_transparency"
    ]

    for url in urls:
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(1.5)  # 等頁面渲染

            # 讀 body 文字
            body_text = (await page.locator("body").inner_text()).lower()

            # 判斷是否有廣告
            if "此粉絲專頁目前正在刊登廣告。" in body_text:
                return True
        except Exception as e:
            print(f"[ads] load error for profile_id={profile_id}: {e}")
        finally:
            await page.close()

    return False

