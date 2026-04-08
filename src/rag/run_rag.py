"""
RAG pipeline runner.

Usage:
    python -m src.rag.run_rag --index          # embed chunks and build ChromaDB index
    python -m src.rag.run_rag --index --reset  # rebuild index from scratch
    python -m src.rag.run_rag --search "your question here"
"""

import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main():
    parser = argparse.ArgumentParser(description="RAG pipeline")
    parser.add_argument("--index", action="store_true", help="Build ChromaDB index")
    parser.add_argument("--reset", action="store_true", help="Wipe and rebuild index")
    parser.add_argument("--search", type=str, help="Run a test semantic search query")
    args = parser.parse_args()

    if args.index:
        from .indexer import build_index
        build_index(reset=args.reset)

    if args.search:
        from .retriever import semantic_search, format_context_for_llm
        results = semantic_search(args.search, top_k=5)
        context = format_context_for_llm(results)
        print("\n=== Retrieved Context ===")
        print(context)


if __name__ == "__main__":
    main()
