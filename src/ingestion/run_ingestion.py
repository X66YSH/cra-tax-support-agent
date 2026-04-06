"""
Full ingestion pipeline runner.

Usage:
    python -m src.ingestion.run_ingestion          # run everything
    python -m src.ingestion.run_ingestion --html   # HTML scraping only
    python -m src.ingestion.run_ingestion --pdf    # PDF download only
    python -m src.ingestion.run_ingestion --chunk  # chunking only
"""

import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_html():
    from .scraper import scrape_all
    logger.info("=== Step 1/3: Scraping HTML pages ===")
    records = scrape_all()
    logger.info(f"HTML scraping done: {len(records)} pages\n")
    return records


def run_pdf():
    from .pdf_downloader import download_all_pdfs
    logger.info("=== Step 2/3: Downloading PDFs ===")
    records = download_all_pdfs()
    logger.info(f"PDF processing done: {len(records)} files\n")
    return records


def run_chunk():
    from .chunker import chunk_all
    logger.info("=== Step 3/3: Chunking documents ===")
    chunks = chunk_all()
    logger.info(f"Chunking done: {len(chunks)} chunks\n")
    return chunks


def main():
    parser = argparse.ArgumentParser(description="CRA ingestion pipeline")
    parser.add_argument("--html", action="store_true", help="Run HTML scraping only")
    parser.add_argument("--pdf", action="store_true", help="Run PDF download only")
    parser.add_argument("--chunk", action="store_true", help="Run chunking only")
    args = parser.parse_args()

    run_all = not any([args.html, args.pdf, args.chunk])

    if args.html or run_all:
        run_html()
    if args.pdf or run_all:
        run_pdf()
    if args.chunk or run_all:
        run_chunk()

    logger.info("=== Ingestion pipeline complete ===")


if __name__ == "__main__":
    main()
