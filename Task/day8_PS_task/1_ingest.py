"""Read Markdown, split it, embed it, and persist a Chroma collection."""
from pathlib import Path
import sys

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from lc_config import CHROMA_DIR, COLLECTION_NAME, ROOT_DIR, get_embeddings


def main():
    data_dir = ROOT_DIR / "data"
    if not data_dir.is_dir():
        raise SystemExit(f"Data directory not found: {data_dir}")
    paths = sorted(data_dir.glob("*.md"))
    if not paths:
        raise SystemExit(f"No Markdown files found in {data_dir}")

    docs = []
    for path in paths:
        content = path.read_text(encoding="utf-8")
        if content.strip():
            docs.append(Document(page_content=content, metadata={"source": path.name}))

    if not docs:
        raise SystemExit("Markdown files exist, but all are empty.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    try:
        embeddings = get_embeddings()
        # Recreate collection to avoid duplicate chunks on repeated ingestion.
        Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_DIR,
        ).delete_collection()
    except Exception:
        # Collection may not exist on first run; continue to create it below.
        pass

    try:
        Chroma.from_documents(
            documents=chunks,
            embedding=get_embeddings(),
            collection_name=COLLECTION_NAME,
            persist_directory=CHROMA_DIR,
        )
    except Exception as exc:
        raise SystemExit(
            f"Ingestion failed: {exc}\nCheck requirements, embedding configuration, "
            "and (for Ollama embeddings) that Ollama is running and the model is pulled."
        ) from exc

    print(f"Source documents loaded: {len(docs)}")
    print(f"Chunks stored: {len(chunks)}")
    print(f"Chroma directory: {CHROMA_DIR}")
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
