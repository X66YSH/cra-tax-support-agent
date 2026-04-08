"""
Retriever: given a user query, find the most relevant chunks from ChromaDB.

Retrieval strategy:
1. Expand query with CRA domain terminology (query_expander)
2. If feature is known, filtered_search first (precise)
3. Fall back to full semantic_search if filtered results are weak
4. Fetch more candidates than needed, deduplicate, return top_k
"""

import logging

from .embedder import embed_query
from .indexer import get_chroma_client, get_collection
from .query_expander import expand_query

TOP_K = 5               # number of chunks to return to the agent
FETCH_K = 12            # over-fetch before dedup and trimming to top_k
SCORE_THRESHOLD = 0.35  # discard chunks with cosine similarity below this
FALLBACK_TRIGGER = 0.5  # fall back to full search if top filtered score < this

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _format_results(query_result: dict) -> list[dict]:
    """
    Convert raw ChromaDB query output into clean result dicts.

    Each result contains:
        text        — chunk text (fed to LLM as context)
        score       — cosine similarity 0–1 (higher = more relevant)
        title       — page/document title
        source_url  — original URL (used for citations)
        doc_type    — "html" or "pdf"
    """
    results = []
    documents = query_result["documents"][0]
    metadatas = query_result["metadatas"][0]
    distances = query_result["distances"][0]

    for doc, meta, dist in zip(documents, metadatas, distances):
        score = 1 - dist  # cosine distance → cosine similarity
        if score < SCORE_THRESHOLD:
            continue
        results.append({
            "text": doc,
            "score": round(score, 4),
            "title": meta.get("title", ""),
            "source_url": meta.get("source_url", ""),
            "doc_type": meta.get("doc_type", ""),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def _dedup(results: list[dict]) -> list[dict]:
    """
    Remove near-duplicate chunks from the same source page.
    Keeps the highest-scoring chunk per (source_url, chunk_index).
    """
    seen = set()
    deduped = []
    for r in results:
        key = r["source_url"] + r["text"][:80]
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped


def semantic_search(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Full knowledge base semantic search with query expansion.

    Embeds the expanded query and finds the top-k most similar chunks
    across all documents using cosine similarity (ChromaDB HNSW index).
    """
    client = get_chroma_client()
    collection = get_collection(client)

    if collection.count() == 0:
        raise RuntimeError(
            "ChromaDB collection is empty. Build the index first:\n"
            "  python -m src.rag.run_rag --index"
        )

    expanded = expand_query(query)
    query_vector = embed_query(expanded)

    raw = collection.query(
        query_embeddings=[query_vector],
        n_results=min(FETCH_K, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    results = _dedup(_format_results(raw))[:top_k]
    logger.debug(f"semantic_search: '{query}' → {len(results)} results")
    return results


def filtered_search(query: str, feature: str, top_k: int = TOP_K) -> list[dict]:
    """
    Semantic search restricted to chunks tagged with a specific feature.

    Uses boolean metadata flags (feat_<feature>) stored at index time.
    Fetches more candidates than needed (FETCH_K) then deduplicates.

    Args:
        query:   user's question
        feature: one of tax_estimate | benefit_eligibility |
                 filing_reminder | book_appointment |
                 international_students | slips_and_forms
        top_k:   number of results to return
    """
    client = get_chroma_client()
    collection = get_collection(client)

    expanded = expand_query(query)
    query_vector = embed_query(expanded)

    raw = collection.query(
        query_embeddings=[query_vector],
        n_results=min(FETCH_K, collection.count()),
        where={f"feat_{feature}": {"$eq": True}},
        include=["documents", "metadatas", "distances"],
    )

    results = _dedup(_format_results(raw))[:top_k]
    logger.debug(f"filtered_search ({feature}): '{query}' → {len(results)} results")
    return results


def retrieve(
    query: str,
    feature: str | None = None,
    top_k: int = TOP_K,
) -> list[dict]:
    """
    Main retrieval entry point for the agent layer.

    Pipeline:
    1. Expand query with CRA terminology
    2. Try filtered_search (feature-scoped) if feature is known
    3. If filtered results are weak (< 2 results or top score < FALLBACK_TRIGGER),
       merge with full semantic_search results
    4. Deduplicate and return top_k

    Args:
        query:   user's question in natural language
        feature: intent label from the agent — pass None for full search
        top_k:   number of chunks to return
    """
    if not feature:
        return semantic_search(query, top_k=top_k)

    filtered = filtered_search(query, feature=feature, top_k=top_k)
    top_score = filtered[0]["score"] if filtered else 0

    if len(filtered) >= 2 and top_score >= FALLBACK_TRIGGER:
        return filtered

    # Filtered results are weak — merge with full search
    logger.debug(
        f"Filtered weak ({len(filtered)} results, top={top_score:.3f}), "
        "merging with full semantic search"
    )
    fallback = semantic_search(query, top_k=top_k)

    # Merge: filtered first (more precise), then fallback
    merged = filtered[:]
    seen = {r["source_url"] + r["text"][:80] for r in merged}
    for r in fallback:
        key = r["source_url"] + r["text"][:80]
        if key not in seen:
            merged.append(r)
            seen.add(key)

    return sorted(merged, key=lambda x: x["score"], reverse=True)[:top_k]


def format_context_for_llm(results: list[dict]) -> str:
    """
    Format retrieved chunks into a prompt context block for the LLM.
    Each chunk is labelled with its source URL for citations.
    """
    if not results:
        return "No relevant information found in the knowledge base."

    parts = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[Source {i}] {r['title']} ({r['source_url']})\n{r['text']}"
        )
    return "\n\n---\n\n".join(parts)


if __name__ == "__main__":
    tests = [
        ("I earned 18000 as a TA, how much federal tax do I owe?", "tax_estimate"),
        ("Am I eligible for the GST/HST credit as an international student?", "benefit_eligibility"),
        ("How do I carry forward my tuition tax credit?", "benefit_eligibility"),
        ("When is the tax filing deadline in Canada?", "filing_reminder"),
        ("What documents do I need for the UTSU tax clinic?", "book_appointment"),
        ("I am a student from China, do I need to pay tax on my Chinese income?", "international_students"),
    ]
    for query, feature in tests:
        print(f"[{feature}] {query}")
        results = retrieve(query, feature=feature, top_k=3)
        for r in results:
            print(f"  {r['score']:.3f} | {r['title'][:60]}")
        print()
