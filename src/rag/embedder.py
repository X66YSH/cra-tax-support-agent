"""
Embedder: converts text chunks into dense vectors using sentence-transformers.

Model: all-MiniLM-L6-v2
- 384-dimensional vectors
- Fast and lightweight, good for semantic search
- Pretrained on 1B+ sentence pairs
"""

import json
import logging
from pathlib import Path

from sentence_transformers import SentenceTransformer

CHUNKS_PATH = Path("data/processed/chunks.json")
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64  # number of chunks embedded at once

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Singleton — load model once and reuse
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of strings into embedding vectors.

    Uses batch encoding for efficiency. Returns a list of float lists
    (one vector per input text).
    """
    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=len(texts) > 100,
        convert_to_numpy=True,
        normalize_embeddings=True,  # cosine similarity = dot product after normalization
    )
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string for retrieval."""
    model = get_model()
    vector = model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return vector.tolist()


def load_chunks() -> list[dict]:
    """Load all chunks from data/processed/chunks.json."""
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"{CHUNKS_PATH} not found. Run the ingestion pipeline first:\n"
            "  python -m src.ingestion.run_ingestion"
        )
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    logger.info(f"Loaded {len(chunks)} chunks from {CHUNKS_PATH}")
    return chunks


def embed_all_chunks() -> tuple[list[dict], list[list[float]]]:
    """
    Load all chunks and compute their embeddings.

    Returns:
        chunks: the original chunk dicts
        embeddings: parallel list of embedding vectors
    """
    chunks = load_chunks()
    texts = [c["text"] for c in chunks]

    logger.info(f"Embedding {len(texts)} chunks with {MODEL_NAME}...")
    embeddings = embed_texts(texts)
    logger.info("Embedding complete.")

    return chunks, embeddings


if __name__ == "__main__":
    chunks, embeddings = embed_all_chunks()
    print(f"Chunks: {len(chunks)}")
    print(f"Embedding dim: {len(embeddings[0])}")
