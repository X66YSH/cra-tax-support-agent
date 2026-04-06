"""
Text chunker for RAG pipeline.
Reads raw .txt files from data/raw/ and writes chunked JSON to data/processed/.
"""

import json
import logging
import uuid
from pathlib import Path

RAW_HTML_DIR = Path("data/raw/html")
RAW_PDF_DIR = Path("data/raw/pdfs")
PROCESSED_DIR = Path("data/processed")

CHUNK_SIZE = 800        # characters per chunk
CHUNK_OVERLAP = 150     # overlap between consecutive chunks

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks.
    Tries to split on paragraph boundaries (\n\n) for cleaner chunks.
    """
    # Split on double newlines first (paragraph-level)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}".strip()
        else:
            if current:
                chunks.append(current)
            # Para itself longer than chunk_size → split by character
            if len(para) > chunk_size:
                for start in range(0, len(para), chunk_size - overlap):
                    chunks.append(para[start: start + chunk_size])
                current = para[-(overlap):]
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def chunk_document(meta: dict) -> list[dict]:
    """
    Load text from meta['text_path'], chunk it, and return a list of chunk records.
    Each record is ready to be inserted into ChromaDB.
    """
    text_path = Path(meta["text_path"])
    if not text_path.exists():
        logger.warning(f"Text file not found: {text_path}")
        return []

    text = text_path.read_text(encoding="utf-8")
    raw_chunks = _split_text(text)

    chunks = []
    for i, chunk_text in enumerate(raw_chunks):
        chunk = {
            "chunk_id": str(uuid.uuid4()),
            "text": chunk_text,
            "source_url": meta.get("source_url", ""),
            "title": meta.get("title", ""),
            "doc_type": meta.get("doc_type", ""),
            "feature": meta.get("feature") or meta.get("features", []),
            "chunk_index": i,
            "total_chunks": len(raw_chunks),
        }
        chunks.append(chunk)

    return chunks


def chunk_all() -> list[dict]:
    """
    Process all metadata JSON files from raw html and pdf directories.
    Writes a single chunks.json to data/processed/.
    Returns the full list of chunks.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    all_meta_files = list(RAW_HTML_DIR.glob("*.json")) + list(RAW_PDF_DIR.glob("*.json"))
    if not all_meta_files:
        logger.warning("No metadata files found. Run scraper and pdf_downloader first.")
        return []

    all_chunks = []
    for meta_path in all_meta_files:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        chunks = chunk_document(meta)
        all_chunks.extend(chunks)
        logger.info(f"[OK] {meta.get('title', meta_path.stem):50s} → {len(chunks)} chunks")

    output_path = PROCESSED_DIR / "chunks.json"
    output_path.write_text(
        json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    logger.info(f"\nTotal chunks: {len(all_chunks)} → saved to {output_path}")
    return all_chunks


if __name__ == "__main__":
    chunk_all()
