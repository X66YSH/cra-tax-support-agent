"""
Indexer: stores chunk embeddings into ChromaDB for fast vector search.

ChromaDB is a local vector database — no external service needed.
Data is persisted to disk at chroma_db/ and reloaded on next run.
"""

import logging
from pathlib import Path

import chromadb
from chromadb.config import Settings

from .embedder import embed_all_chunks

CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "cra_tax_knowledge"
BATCH_SIZE = 100  # ChromaDB insert batch size

ALL_FEATURES = [
    "tax_estimate",
    "benefit_eligibility",
    "filing_reminder",
    "book_appointment",
    "international_students",
    "slips_and_forms",
    "backup",
]


def _build_metadata(chunk: dict) -> dict:
    """
    Build ChromaDB metadata for a chunk.

    ChromaDB only supports scalar metadata values (str, int, float, bool).
    To support multi-feature PDF chunks, each feature is stored as a
    boolean flag: feat_tax_estimate, feat_benefit_eligibility, etc.
    """
    raw_feature = chunk.get("feature") or chunk.get("features", [])
    if isinstance(raw_feature, str):
        active_features = {raw_feature}
    else:
        active_features = set(raw_feature)

    meta = {
        "title": chunk.get("title", ""),
        "source_url": chunk.get("source_url", ""),
        "doc_type": chunk.get("doc_type", ""),
        "chunk_index": chunk.get("chunk_index", 0),
        "total_chunks": chunk.get("total_chunks", 1),
    }
    for f in ALL_FEATURES:
        meta[f"feat_{f}"] = f in active_features

    return meta

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def get_chroma_client() -> chromadb.PersistentClient:
    """Return a persistent ChromaDB client (data saved to chroma_db/)."""
    CHROMA_DIR.mkdir(exist_ok=True)
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )


def get_collection(client: chromadb.PersistentClient, reset: bool = False):
    """
    Get (or create) the ChromaDB collection.

    Args:
        reset: if True, delete existing collection and rebuild from scratch.
    """
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            logger.info(f"Deleted existing collection: {COLLECTION_NAME}")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        # Cosine similarity — best for semantic search with normalized embeddings
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def build_index(reset: bool = False) -> None:
    """
    Embed all chunks and insert them into ChromaDB.

    Steps:
    1. Load chunks from data/processed/chunks.json
    2. Compute embeddings with sentence-transformers
    3. Insert into ChromaDB in batches with metadata

    Args:
        reset: wipe existing index before rebuilding (use after re-scraping)
    """
    chunks, embeddings = embed_all_chunks()

    client = get_chroma_client()
    collection = get_collection(client, reset=reset)

    existing = collection.count()
    if existing > 0 and not reset:
        logger.info(
            f"Collection already has {existing} documents. "
            "Use reset=True to rebuild. Skipping insert."
        )
        return

    logger.info(f"Inserting {len(chunks)} chunks into ChromaDB...")

    # Insert in batches to avoid memory issues
    for start in range(0, len(chunks), BATCH_SIZE):
        batch_chunks = chunks[start: start + BATCH_SIZE]
        batch_embeds = embeddings[start: start + BATCH_SIZE]

        collection.add(
            ids=[c["chunk_id"] for c in batch_chunks],
            embeddings=batch_embeds,
            documents=[c["text"] for c in batch_chunks],
            # Metadata stored alongside each chunk for filtering and citation.
            # Each feature is stored as a boolean flag (feat_<name>: True/False)
            # because ChromaDB metadata only supports scalar types, not lists.
            metadatas=[
                _build_metadata(c)
                for c in batch_chunks
            ],
        )
        logger.info(f"  Inserted batch {start // BATCH_SIZE + 1} "
                    f"({min(start + BATCH_SIZE, len(chunks))}/{len(chunks)})")

    logger.info(f"Index built. Total documents in collection: {collection.count()}")


if __name__ == "__main__":
    build_index(reset=False)
