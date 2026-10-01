
"""
Day 5 Task: Compare three scenarios using the Groq API.

Scenarios:
1. Cybersecurity Incident Explainer
2. Photography Mentor
3. Placement Aptitude Tutor

Measurements:
- Non-streaming response time
- Streaming time to first token (TTFT)
- Total streaming time
- Output tokens and approximate generation speed
- System prompt override comparison
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE = "https://api.groq.com/openai/v1"
API_KEY = os.getenv("GROQ_API_KEY")

MODELS = {
    "Cybersecurity Incident Explainer": os.getenv("MODEL1"),
    "Photography Mentor": os.getenv("MODEL2"),
    "Placement Aptitude Tutor": os.getenv("MODEL")
}

if not API_KEY:
    raise SystemExit("Error: GROQ_API_KEY not found in .env file.")

for name, model in MODELS.items():
    if not model:
        raise SystemExit(f"Error: Model not configured for {name}")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


# ==========================================
# 2. SCENARIOS
# ==========================================

SCENARIOS = {
    "Cybersecurity Incident Explainer": {
        "system": (
            "You are a cybersecurity incident explainer. "
            "Explain security alerts in simple language. "
            "Separate confirmed facts from possible threats. "
            "Never claim an attack is confirmed without evidence. "
            "Give practical, safe next steps."
        ),
        "prompts": [
            "I received an email asking me to reset my bank password. "
            "The link looks unusual. What should I do?",
            "My account shows a login from an unfamiliar location. "
            "Explain what this could mean.",
            "My computer's antivirus detected a suspicious file. "
            "What steps should I take?"
        ]
    },

    "Photography Mentor": {
        "system": (
            "You are a photography mentor for beginners. "
            "Give practical explanations with clear steps. "
            "Explain camera settings such as ISO, shutter speed, "
            "and aperture when relevant. Avoid unnecessary jargon."
        ),
        "prompts": [
            "How can I photograph stars using a beginner camera?",
            "My photos of moving people are blurry. How can I fix this?",
            "How should I set up my camera for a portrait outdoors?"
        ]
    },

    "Placement Aptitude Tutor": {
        "system": (
            "You are a placement aptitude tutor. "
            "When a learner asks a problem, give a small hint first "
            "instead of immediately revealing the full solution. "
            "If the learner asks for the solution, explain the steps "
            "and show the calculation clearly."
        ),
        "prompts": [
            "Two trains of lengths 150 m and 250 m travel in opposite "
            "directions at 54 km/h and 36 km/h. Find the crossing time.",
            "A person completes a job in 12 days. Another completes it "
            "in 18 days. Give me a hint to find their combined time.",
            "Give me one practice question on percentages."
        ]
    }
}


# ==========================================
# 3. NON-STREAMING API REQUEST
# ==========================================

def chat_once(system_prompt, user_prompt, model):
    """Send a non-streaming request and measure response time."""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0,
        "stream": False
    }

    print(f"Model: {model}")

    start = time.perf_counter()

    response = requests.post(
        f"{BASE}/chat/completions",
        headers=HEADERS,
        json=payload,
        timeout=120
    )

    elapsed = time.perf_counter() - start
    response.raise_for_status()

    data = response.json()
    answer = data["choices"][0]["message"]["content"]

    usage = data.get("usage", {})
    tokens = usage.get("completion_tokens")

    print(f"Response time: {elapsed:.2f} seconds")

    if tokens is not None:
        speed = tokens / elapsed if elapsed else 0
        print(f"Output tokens: {tokens}")
        print(f"Approx. output speed: {speed:.2f} tokens/sec")

    print("\nResponse:")
    print(answer)

    return elapsed, answer


# ==========================================
# 4. STREAMING API REQUEST
# ==========================================

def chat_stream(system_prompt, user_prompt, model):
    """Stream a response and measure TTFT and total time."""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0,
        "stream": True,
        "stream_options": {"include_usage": True}
    }

    start = time.perf_counter()
    first_token_time = None
    pieces = []
    usage = {}

    print(f"Model: {model}")
    print("Streaming response:\n")

    with requests.post(
        f"{BASE}/chat/completions",
        headers=HEADERS,
        json=payload,
        stream=True,
        timeout=120
    ) as response:

        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            if line.startswith("data: "):
                content = line[6:]

                if content == "[DONE]":
                    break

                chunk = json.loads(content)

                if chunk.get("usage"):
                    usage = chunk["usage"]

                choices = chunk.get("choices", [])

                if not choices:
                    continue

                piece = choices[0].get("delta", {}).get("content", "")

                if piece:
                    if first_token_time is None:
                        first_token_time = time.perf_counter() - start

                    pieces.append(piece)
                    print(piece, end="", flush=True)

    total_time = time.perf_counter() - start
    answer = "".join(pieces)

    print("\n")

    if first_token_time is not None:
        print(f"TTFT: {first_token_time:.2f} seconds")
    else:
        print("TTFT: Not available")

    print(f"Total streaming time: {total_time:.2f} seconds")

    tokens = usage.get("completion_tokens")

    if tokens is not None:
        speed = tokens / total_time if total_time else 0
        print(f"Output tokens: {tokens}")
        print(f"Approx. output speed: {speed:.2f} tokens/sec")

    return first_token_time, total_time, answer


# ==========================================
# 5. RUN A SCENARIO
# ==========================================

def run_scenario(name, scenario):
    """Run all prompts for one scenario."""

    print("\n" + "=" * 65)
    print(f"SCENARIO: {name}")
    print("=" * 65)

    system_prompt = scenario["system"]
    prompts = scenario["prompts"]
    model = MODELS[name]

    print(f"Assigned model: {model}")

    for index, prompt in enumerate(prompts, start=1):
        print(f"\n--- Test {index}: Non-streaming ---")
        print(f"Prompt: {prompt}")

        try:
            chat_once(system_prompt, prompt, model)

        except requests.RequestException as error:
            print(f"API request failed: {error}")
            continue

        if index == 1:
            print("\n--- Streaming test ---")

            try:
                chat_stream(system_prompt, prompt, model)

            except requests.RequestException as error:
                print(f"Streaming request failed: {error}")


# ==========================================
# 6. SYSTEM PROMPT OVERRIDE TEST
# ==========================================

def test_prompt_override():
    """Compare two system prompts using the same model."""

    print("\n" + "=" * 65)
    print("SYSTEM PROMPT OVERRIDE TEST")
    print("=" * 65)

    user_prompt = (
        "Explain what to do when an unfamiliar login is detected."
    )

    model = MODELS["Cybersecurity Incident Explainer"]

    prompts_to_test = [
        (
            "Original cybersecurity system prompt",
            SCENARIOS["Cybersecurity Incident Explainer"]["system"]
        ),
        (
            "Override: exactly two short bullet points",
            "You are a concise assistant. "
            "Answer using exactly two short bullet points."
        )
    ]

    for label, system_prompt in prompts_to_test:
        print(f"\n--- {label} ---")

        try:
            chat_once(system_prompt, user_prompt, model)

        except requests.RequestException as error:
            print(f"API request failed: {error}")


# ==========================================
# 7. MAIN
# ==========================================

if __name__ == "__main__":
    print("Using Groq models:")

    for name, model in MODELS.items():
        print(f"  {name}: {model}")

    for name, scenario in SCENARIOS.items():
        run_scenario(name, scenario)

    test_prompt_override()

    print("\nAll experiments completed.")
