from config import client, MODEL

QUESTION = """
I have 90 minutes tonight. Python needs 40 minutes, Computer Networks
needs 35 minutes, and SQL needs 30 minutes. Which combination lets me
finish the maximum number of complete tasks within 90 minutes?

Reason through the possible combinations step by step, check the arithmetic,
and then give the final recommendation.
"""

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a careful study-planning assistant."},
        {"role": "user", "content": QUESTION},
    ],
    temperature=0,
)

print("=== CHAIN-OF-THOUGHT STYLE PROMPTING ===")
print(response.choices[0].message.content.strip())
