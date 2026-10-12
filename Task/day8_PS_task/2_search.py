"""CLI retrieval demo with actual Chroma distances and a configurable guard."""
from pathlib import Path

from langchain_chroma import Chroma
from lc_config import CHROMA_DIR, COLLECTION_NAME, MAX_DISTANCE, get_embeddings

QUERIES = [
    "What is the hostel in-time?",
    "What are the placement eligibility criteria?",
    "What is the international-student refund policy?",
    "What is the minimum exam attendance?",
]


def main():
    if not Path(CHROMA_DIR).exists():
        raise SystemExit("Vector store not found. Run `python .\\1_ingest.py` first.")
    try:
        store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_DIR,
        )
        if store._collection.count() == 0:
            raise SystemExit("The vector store is empty. Run `python .\\1_ingest.py` first.")
    except SystemExit:
        raise
    except Exception as exc:
        raise SystemExit(f"Could not open Chroma store: {exc}") from exc

    print(f"MAX_DISTANCE={MAX_DISTANCE} (inspect and tune for your embedding setup)\n")
    for query in QUERIES:
        print("=" * 78)
        print(f"QUERY: {query}")
        results = store.similarity_search_with_score(query, k=3)
        accepted = False
        for rank, (doc, distance) in enumerate(results, 1):
            print(f"\n[{rank}] source={doc.metadata.get('source', 'unknown')} distance={distance:.4f}")
            print(doc.page_content[:500].replace("\n", " "))
            if distance <= MAX_DISTANCE:
                accepted = True
        print(f"\nRELEVANCE GUARD: {'ACCEPT' if accepted else 'REJECT — no sufficiently relevant evidence'}")


if __name__ == "__main__":
    main()
