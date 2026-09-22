from config import client, MODEL

QUESTION = """
I have 90 minutes tonight. Python needs 40 minutes, Computer Networks
needs 35 minutes, and SQL needs 30 minutes. Which combination lets me
finish the maximum number of complete tasks within 90 minutes?
Give the final recommendation.
"""

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a study-planning assistant."},
        {"role": "user", "content": QUESTION},
    ],
    temperature=0,
)

print("=== DIRECT PROMPTING ===")
print(response.choices[0].message.content.strip())
