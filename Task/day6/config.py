"""OpenAI-compatible client configuration for Groq or Ollama."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
PROVIDER = os.getenv("PROVIDER", "groq").strip().lower()

if PROVIDER == "groq":
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    # A placeholder lets offline scripts (validator/fault injection) import this
    # module without credentials. Model-backed scripts still require a real key.
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key or "missing-groq-api-key",
    )
    MODEL = os.getenv("MODEL", "openai/gpt-oss-120b")
elif PROVIDER == "ollama":
    client = OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
    )
    MODEL = os.getenv("MODEL", "qwen2.5:1.5b")
else:
    raise RuntimeError("PROVIDER must be 'groq' or 'ollama'.")

def banner(title):
    print("=" * 72)
    print(f"{title} | provider: {PROVIDER} | model: {MODEL}")
    print("=" * 72)
