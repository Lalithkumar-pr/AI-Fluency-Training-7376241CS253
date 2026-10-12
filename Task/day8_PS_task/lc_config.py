"""Central configuration and provider factories for the Day 8 RAG project."""
import hashlib
import math
import os
import re
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")

PROVIDER = os.getenv("PROVIDER", "ollama").strip().lower()
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.1").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
EMBED_PROVIDER = os.getenv("EMBED_PROVIDER", "hash").strip().lower()
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text").strip()
CHROMA_DIR = str((ROOT_DIR / os.getenv("CHROMA_DIR", "chroma_db")).resolve())
MAX_DISTANCE = float(os.getenv("MAX_DISTANCE", "0.6"))
COLLECTION_NAME = "day8_handbook"


class HashEmbeddings(Embeddings):
    """Deterministic feature-hashing embeddings; lightweight, not a trained semantic model."""
    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def _embed(self, text: str) -> List[float]:
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        vector = [0.0] * self.dimensions
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


def get_embeddings() -> Embeddings:
    if EMBED_PROVIDER == "hash":
        return HashEmbeddings()
    if EMBED_PROVIDER == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=EMBED_MODEL)
    raise ValueError("EMBED_PROVIDER must be 'hash' or 'ollama'.")


def get_chat_model():
    if PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=CHAT_MODEL, temperature=0)
    if PROVIDER == "groq":
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            raise RuntimeError(
                "Set GROQ_API_KEY in .env before using PROVIDER=groq."
            )
        from langchain_groq import ChatGroq
        return ChatGroq(model=CHAT_MODEL, api_key=GROQ_API_KEY, temperature=0)
    raise ValueError("PROVIDER must be 'ollama' or 'groq'.")
