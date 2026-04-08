"""
PDF downloader and text extractor.
Downloads CRA PDF publications to data/raw/pdfs/ and extracts text.
"""

import json
import logging
import time
from pathlib import Path

import pdfplumber
import requests

from .urls import PDF_URLS

RAW_PDF_DIR = Path("data/raw/pdfs")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; CRA-Tax-Bot/1.0; "
        "+https://github.com/X66YSH/cra-tax-support-agent)"
    )
}
REQUEST_DELAY = 2.0

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def download_pdf(url: str, dest: Path) -> bool:
    """Download a PDF from url and save to dest. Returns True on success."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        response.raise_for_status()
        dest.write_bytes(response.content)
        return True
    except requests.RequestException as e:
        logger.warning(f"Failed to download {url}: {e}")
        return False


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract all text from a PDF using pdfplumber.
    Falls back to an empty string if extraction fails.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text.strip())
            return "\n\n".join(pages_text)
    except Exception as e:
        logger.warning(f"Text extraction failed for {pdf_path}: {e}")
        return ""


def process_pdf(entry: dict, delay: float = REQUEST_DELAY) -> dict | None:
    """
    Download and extract text for a single PDF entry.
    Returns a metadata record on success, None on failure.
    """
    RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)

    pdf_path = RAW_PDF_DIR / entry["filename"]
    txt_path = RAW_PDF_DIR / entry["filename"].replace(".pdf", ".txt")
    meta_path = RAW_PDF_DIR / entry["filename"].replace(".pdf", ".json")

    # Download
    if pdf_path.exists():
        logger.info(f"[SKIP] Already downloaded: {entry['filename']}")
    else:
        logger.info(f"[DL]   {entry['title']}")
        success = download_pdf(entry["url"], pdf_path)
        if not success:
            return None
        time.sleep(delay)

    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if not text:
        logger.warning(f"No text extracted from {entry['filename']}")
        return None

    txt_path.write_text(text, encoding="utf-8")

    record = {
        "filename": entry["filename"],
        "title": entry["title"],
        "source_url": entry["url"],
        "features": entry["features"],
        "doc_type": "pdf",
        "page_count": _count_pages(pdf_path),
        "char_count": len(text),
        "text_path": str(txt_path),
    }
    meta_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info(f"[OK]  {entry['title']} | {record['page_count']} pages | {len(text):,} chars")
    return record


def _count_pages(pdf_path: Path) -> int:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages)
    except Exception:
        return 0


def download_all_pdfs(delay: float = REQUEST_DELAY) -> list[dict]:
    """
    Download and extract text for all PDFs defined in urls.py.
    Returns a list of metadata records.
    """
    RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    logger.info(f"Starting download of {len(PDF_URLS)} PDFs...")
    for i, entry in enumerate(PDF_URLS, 1):
        logger.info(f"[{i}/{len(PDF_URLS)}] {entry['title']}")
        record = process_pdf(entry, delay=delay)
        if record:
            results.append(record)

    logger.info(f"Done. {len(results)}/{len(PDF_URLS)} PDFs processed successfully.")
    return results


if __name__ == "__main__":
    download_all_pdfs()
