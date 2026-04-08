"""
Text chunker for RAG pipeline.
Reads raw .txt files from data/raw/ and writes chunked JSON to data/processed/.

Splits by token count using all-MiniLM-L6-v2's own tokenizer,
so chunks are guaranteed to stay within the model's 256-token limit.
"""

import json
import logging
import uuid
from pathlib import Path

from sentence_transformers import SentenceTransformer

RAW_HTML_DIR = Path("data/raw/html")
RAW_PDF_DIR = Path("data/raw/pdfs")
PROCESSED_DIR = Path("data/processed")

CHUNK_SIZE = 200        # tokens per chunk (model max is 256, leave headroom)
CHUNK_OVERLAP = 30      # token overlap between consecutive chunks
MODEL_NAME = "all-MiniLM-L6-v2"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Singleton tokenizer — loaded once and reused
_tokenizer = None


def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        logger.info(f"Loading tokenizer from {MODEL_NAME}...")
        model = SentenceTransformer(MODEL_NAME)
        _tokenizer = model.tokenizer
    return _tokenizer


def _count_tokens(text: str) -> int:
    """Count the number of tokens in a string using the model's tokenizer."""
    tokenizer = get_tokenizer()
    return len(tokenizer.encode(text, add_special_tokens=False))


def _split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks measured in tokens.

    Strategy:
    1. Split on paragraph boundaries (\\n\\n) for cleaner semantic chunks
    2. Accumulate paragraphs until the token count approaches chunk_size
    3. If a single paragraph exceeds chunk_size, split it by sentences
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current_paras = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = _count_tokens(para)

        if para_tokens > chunk_size:
            # Paragraph too long — flush current buffer first
            if current_paras:
                chunks.append("\n\n".join(current_paras))
                # Keep last overlap tokens worth of text for continuity
                current_paras = current_paras[-1:]
                current_tokens = _count_tokens(current_paras[0]) if current_paras else 0

            # Split long paragraph by sentences
            sentences = [s.strip() for s in para.replace(".\n", ". ").split(". ") if s.strip()]
            sent_buf = []
            sent_tokens = 0

            for sent in sentences:
                t = _count_tokens(sent)
                if sent_tokens + t > chunk_size and sent_buf:
                    chunks.append(". ".join(sent_buf) + ".")
                    # Overlap: keep last sentence
                    sent_buf = sent_buf[-1:]
                    sent_tokens = _count_tokens(sent_buf[0]) if sent_buf else 0
                sent_buf.append(sent)
                sent_tokens += t

            if sent_buf:
                leftover = ". ".join(sent_buf) + "."
                current_paras = [leftover]
                current_tokens = _count_tokens(leftover)

        elif current_tokens + para_tokens + 2 <= chunk_size:
            current_paras.append(para)
            current_tokens += para_tokens + 2  # +2 for "\n\n" separator

        else:
            # Flush and start new chunk
            if current_paras:
                chunks.append("\n\n".join(current_paras))
            # Overlap: carry last paragraph into new chunk
            if current_paras and _count_tokens(current_paras[-1]) <= overlap:
                current_paras = [current_paras[-1], para]
                current_tokens = _count_tokens(current_paras[-1]) + para_tokens + 2
            else:
                current_paras = [para]
                current_tokens = para_tokens

    if current_paras:
        chunks.append("\n\n".join(current_paras))

    return chunks


def _clean_pdf_text(text: str) -> str:
    """
    Fix common pdfplumber extraction artifacts in CRA PDFs:
    - Single newlines mid-sentence → space (PDF line wrapping)
    - Keep double newlines as paragraph boundaries
    - Collapse 3+ newlines into double newline
    """
    import re
    # Collapse 3+ newlines → paragraph break
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Single newline not followed by another newline → space
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    # Clean up multiple spaces
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def chunk_document(meta: dict) -> list[dict]:
    """
    Load text from meta['text_path'], chunk it by token count,
    and return a list of chunk records ready for ChromaDB insertion.

    PDF text is pre-cleaned to fix line-wrapping artifacts before chunking.
    """
    text_path = Path(meta["text_path"])
    if not text_path.exists():
        logger.warning(f"Text file not found: {text_path}")
        return []

    text = text_path.read_text(encoding="utf-8")

    if meta.get("doc_type") == "pdf":
        text = _clean_pdf_text(text)

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
            "token_count": _count_tokens(chunk_text),
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
