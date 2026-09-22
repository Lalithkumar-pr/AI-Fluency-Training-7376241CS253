import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
PROVIDER = os.getenv("PROVIDER", "ollama").strip().lower()

if PROVIDER == "ollama":
    BASE_URL = "http://localhost:11434/v1"
    API_KEY = "ollama"
    MODEL = os.getenv("MODEL", "qwen2.5:1.5b")
elif PROVIDER == "groq":
    BASE_URL = "https://api.groq.com/openai/v1"
    API_KEY = os.getenv("GROQ_API_KEY")
    MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")
else:
    raise SystemExit("Use PROVIDER=ollama or PROVIDER=groq in .env")

if not API_KEY:
    raise SystemExit("Missing API key for selected provider.")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
