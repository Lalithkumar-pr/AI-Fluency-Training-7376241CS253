from config import client, MODEL

QUESTION = """
I have 90 minutes. Python takes 40 minutes, Computer Networks takes
35 minutes, and SQL takes 30 minutes. Choose the combination that
completes the maximum number of whole study tasks within 90 minutes.
Give the final answer and a short justification.
"""

def run(temp):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Solve carefully and check the arithmetic."},
            {"role": "user", "content": QUESTION},
        ],
        temperature=temp,
    )
    return response.choices[0].message.content.strip()

print("=== SELF-CONSISTENCY: 5 RUNS, TEMPERATURE 0.8 ===")
for i in range(1, 6):
    print(f"\nRun {i}:")
    print(run(0.8))

print("\n=== CONTROL: TEMPERATURE 0 ===")
for i in range(1, 4):
    print(f"\nRun {i}:")
    print(run(0))
