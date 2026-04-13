import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

MIN_TEXT_LENGTH = 200
MAX_TEXT_LENGTH = 8000
MAX_PAGES = 3

NEXT_PAGE_SELECTORS = [
    'a:has-text("次へ")',
    'a:has-text("次のページ")',
    'a:has-text("Next")',
    '[aria-label="Next page"]',
    '[aria-label="次のページ"]',
    'a[rel="next"]',
]


def _parse_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


async def _scroll_to_bottom(page) -> None:
    """スクロールして遅延ロードコンテンツを取得する"""
    await page.evaluate("""
        async () => {
            await new Promise(resolve => {
                let last = 0;
                const timer = setInterval(() => {
                    window.scrollBy(0, 600);
                    if (document.body.scrollHeight === last) {
                        clearInterval(timer);
                        resolve();
                    }
                    last = document.body.scrollHeight;
                }, 200);
                setTimeout(() => { clearInterval(timer); resolve(); }, 5000);
            });
        }
    """)
    await page.wait_for_timeout(500)


async def _fetch_with_playwright(url: str) -> str:
    texts = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(user_agent=HEADERS["User-Agent"])
        page = await context.new_page()
        current_url = url

        for page_num in range(MAX_PAGES):
            await page.goto(current_url, wait_until="networkidle", timeout=30000)
            await _scroll_to_bottom(page)

            content = await page.content()
            texts.append(_parse_html(content))

            # 次のページリンクを探す
            if page_num < MAX_PAGES - 1:
                next_url = None
                for selector in NEXT_PAGE_SELECTORS:
                    try:
                        next_link = await page.query_selector(selector)
                        if next_link:
                            href = await next_link.get_attribute("href")
                            if href:
                                next_url = urljoin(current_url, href)
                            break
                    except Exception:
                        continue

                if not next_url:
                    break
                current_url = next_url

        await browser.close()

    combined = "\n\n=== 次のページ ===\n\n".join(texts)
    return combined[:MAX_TEXT_LENGTH]


async def scrape_text(url: str) -> str:
    # まず requests で取得（高速）
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        text = _parse_html(res.text)
        if len(text) >= MIN_TEXT_LENGTH:
            return text[:MAX_TEXT_LENGTH]
    except Exception:
        pass

    # テキストが少ない／取得失敗 → Playwright にフォールバック
    return await _fetch_with_playwright(url)
