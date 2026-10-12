"""Configuration for an OpenAI-compatible API provider."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "groq").lower()
MODEL = os.getenv("MODEL", "openai/gpt-oss-120b")
BASE_URL = os.getenv("BASE_URL", "https://api.groq.com/openai/v1")

if PROVIDER == "groq":
    api_key = os.getenv("GROQ_API_KEY")
else:
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key or api_key == "put_your_api_key_here":
    raise RuntimeError(
        "API key missing. Copy .env.example to .env and set GROQ_API_KEY "
        "(or adapt config.py for your provider)."
    )

client = OpenAI(api_key=api_key, base_url=BASE_URL)

def banner(title):
    print("=" * 68)
    print(title)
    print("=" * 68)
    print(f"Provider: {PROVIDER} | Model: {MODEL}")
