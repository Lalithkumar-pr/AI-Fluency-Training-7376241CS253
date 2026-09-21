from config import client, MODEL, QUESTIONS, banner

def chatbot(question):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful college assistant. Answer clearly and do not claim access to private databases."},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return (response.choices[0].message.content or "").strip()

if __name__ == "__main__":
    banner("PLAIN CHATBOT")
    for q in QUESTIONS:
        print("Q:", q)
        print("A:", chatbot(q))
        print("-" * 70)
