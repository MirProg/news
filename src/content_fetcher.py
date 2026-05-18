import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AIBrief/1.0"

def _extract_og_image(html):
    match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\'](https?://[^"\']+)["\']', html, re.I)
    if match:
        return match.group(1)
    match = re.search(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', html)
    if match:
        return match.group(1)
    return ""

def fetch_image_only(url):
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=8)
        if resp.ok:
            return _extract_og_image(resp.text)
    except Exception:
        pass
    return ""

def fetch_all_texts(articles, max_articles=10):
    to_fetch = articles[:max_articles]
    print(f"  Fetching images for {len(to_fetch)} articles...")
    with ThreadPoolExecutor(max_workers=8) as ex:
        fut = {ex.submit(fetch_image_only, a["url"]): a for a in to_fetch}
        for i, f in enumerate(as_completed(fut), 1):
            a = fut[f]
            img = f.result()
            if img and not a.get("image_url"):
                a["image_url"] = img
    img_count = sum(1 for a in articles if a.get("image_url"))
    print(f"  Found {img_count} images")
    return articles
