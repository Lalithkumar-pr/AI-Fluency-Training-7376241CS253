import re
from config import COURSE_FEES, QUESTIONS

def workflow(question):
    text = question.lower()
    codes = re.findall(r"[A-Z]{2}\d{3}", question.upper())
    fees = [COURSE_FEES[c] for c in codes if c in COURSE_FEES]

    if "welcome" in text:
        return "Welcome to the AI programme!\nKeep learning, experimenting, and building."

    if not fees:
        return "Sorry, I can only answer supported course-fee questions."

    if "more expensive" in text or "more costly" in text:
        if len(fees) == 2:
            difference = abs(fees[0] - fees[1])
            if fees[0] > fees[1]:
                return f"Yes. {codes[0]} is more expensive by Rs. {difference:,.0f}."
            if fees[1] > fees[0]:
                return f"Yes. {codes[1]} is more expensive by Rs. {difference:,.0f}."
            return "Neither course is more expensive; both have the same fee."

    if "total" in text and "scholarship" in text:
        match = re.search(r"(\d+)\s*(?:%|percent)", text)
        if match:
            percentage = int(match.group(1))
            total = sum(fees) * (1 - percentage / 100)
            return f"Total fee after scholarship: Rs. {total:,.0f}"

    if len(fees) == 1 and ("fee" in text or "cost" in text):
        return f"Fee for {codes[0]}: Rs. {fees[0]:,}"

    return "Sorry, I do not have a rule for this wording or task."

if __name__ == "__main__":
    print("\n=== RULE-BASED WORKFLOW ===\n")
    for q in QUESTIONS:
        print("Q:", q)
        print("A:", workflow(q))
        print("-" * 70)
