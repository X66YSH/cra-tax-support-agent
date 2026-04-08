"""
HTML scraper for CRA and UofT pages.
Saves raw HTML and extracts clean text to data/raw/html/.
"""

import hashlib
import json
import logging
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .urls import get_all_html_urls

RAW_HTML_DIR = Path("data/raw/html")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; CRA-Tax-Bot/1.0; "
        "+https://github.com/X66YSH/cra-tax-support-agent)"
    )
}
REQUEST_DELAY = 1.5  # seconds between requests — be polite to CRA servers

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _url_to_filename(url: str) -> str:
    """Convert a URL to a safe filename using a short hash suffix."""
    slug = url.rstrip("/").split("/")[-1] or "index"
    slug = slug[:60].replace(".", "_").replace("-", "_")
    suffix = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{slug}_{suffix}"


def _extract_main_content(soup: BeautifulSoup) -> str:
    """
    Extract readable text from a page, stripping nav/header/footer/scripts.
    Works for both canada.ca and UofT layouts.
    """
    # Remove noise elements
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "noscript", "form", "button"]):
        tag.decompose()

    # canada.ca wraps main content in <main> or <div id="wb-cont">
    main = (
        soup.find("main")
        or soup.find("div", id="wb-cont")
        or soup.find("div", class_="container")
        or soup.body
    )
    if main is None:
        return soup.get_text(separator="\n", strip=True)

    text = main.get_text(separator="\n", strip=True)
    # Collapse excessive blank lines
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


def scrape_page(url: str, title: str, feature: str) -> dict | None:
    """
    Download a single HTML page and return a structured record.
    Returns None if the request fails.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "lxml")
    page_title = soup.title.string.strip() if soup.title else title
    text = _extract_main_content(soup)

    filename = _url_to_filename(url)
    html_path = RAW_HTML_DIR / f"{filename}.html"
    text_path = RAW_HTML_DIR / f"{filename}.txt"
    meta_path = RAW_HTML_DIR / f"{filename}.json"

    html_path.write_text(response.text, encoding="utf-8")
    text_path.write_text(text, encoding="utf-8")

    record = {
        "filename": filename,
        "title": page_title,
        "source_url": url,
        "feature": feature,
        "doc_type": "html",
        "char_count": len(text),
        "text_path": str(text_path),
    }
    meta_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info(f"[OK] {feature:25s} | {len(text):6d} chars | {url}")
    return record


def scrape_all(delay: float = REQUEST_DELAY) -> list[dict]:
    """
    Scrape all HTML pages defined in urls.py.
    Returns a list of metadata records for successfully scraped pages.
    """
    RAW_HTML_DIR.mkdir(parents=True, exist_ok=True)
    urls = get_all_html_urls()
    results = []

    logger.info(f"Starting scrape of {len(urls)} pages...")
    for i, entry in enumerate(urls, 1):
        logger.info(f"[{i}/{len(urls)}] {entry['title']}")
        record = scrape_page(entry["url"], entry["title"], entry["feature"])
        if record:
            results.append(record)
        time.sleep(delay)

    logger.info(f"Done. {len(results)}/{len(urls)} pages scraped successfully.")
    return results


if __name__ == "__main__":
    scrape_all()
