"""LangGraph agent with handbook retrieval, fee, calculator, and eligibility tools."""
from pathlib import Path
import re

from langchain_chroma import Chroma
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from lc_config import CHROMA_DIR, COLLECTION_NAME, MAX_DISTANCE, get_chat_model, get_embeddings
from utils import (
    COURSE_FEES, MAX_LATE_FEE, check_exam_eligibility as eligibility_rule,
    late_fee, safe_calculate,
)

SYSTEM_PROMPT = """You are a careful campus handbook assistant.
Use search_handbook for policy/handbook questions and answer only from returned evidence.
If it says NO MATCH, clearly say the knowledge base does not contain enough information;
never invent missing policies. Use get_course_fee for course fees, calculator for arithmetic,
and check_exam_eligibility for attendance rules. Do not guess fee values.
For the fee total question, look up both course fees, use the maximum late fee from the fee
policy, and calculate the total. For the follow-up 'And if I pay only 5 days late instead?',
use the prior turn's context: keep CS101 and AI202, replace only the late fee with five days
at ₹100/day (capped at ₹2,000), and calculate the new total. Explain the arithmetic briefly.
Attendance rule: >=75% eligible under attendance rule; >=65% and <75% may apply for
condonation at ₹500 per course, requiring approval; <65% not eligible under these rules.
"""


def open_store():
    if not Path(CHROMA_DIR).exists():
        raise RuntimeError("Vector store missing. Run `python .\\1_ingest.py` first.")
    store = Chroma(collection_name=COLLECTION_NAME, embedding_function=get_embeddings(),
                   persist_directory=CHROMA_DIR)
    if store._collection.count() == 0:
        raise RuntimeError("Vector store is empty. Run `python .\\1_ingest.py` first.")
    return store


@tool
def search_handbook(query: str) -> str:
    """Search handbook Markdown and return evidence only when a retrieved chunk passes the relevance guard."""
    try:
        results = open_store().similarity_search_with_score(query, k=3)
    except Exception as exc:
        return f"NO MATCH: handbook retrieval is unavailable ({exc})."
    if not results:
        return "NO MATCH: the knowledge base contains no matching documents."
    accepted = [(doc, float(score)) for doc, score in results if float(score) <= MAX_DISTANCE]
    if not accepted:
        score_text = ", ".join(f"{float(score):.4f}" for _, score in results)
        return ("NO MATCH: no retrieved chunk passed the relevance threshold. "
                f"Observed distances: {score_text}. Do not infer a policy.")
    return "\n\n".join(
        f"[source={doc.metadata.get('source', 'unknown')}; distance={score:.4f}]\n{doc.page_content}"
        for doc, score in accepted
    )


@tool
def get_course_fee(course_code: str) -> str:
    """Return the fee for a known course code such as CS101 or AI202, from the task fee policy."""
    amount = COURSE_FEES.get(course_code.strip().upper())
    return f"{course_code.upper()}: ₹{amount:,}" if amount is not None else f"Unknown course code: {course_code}"


@tool
def calculator(expression: str) -> str:
    """Safely calculate basic arithmetic with numbers and +, -, *, /, //, %, and parentheses."""
    try:
        return str(safe_calculate(expression))
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        return f"Calculation rejected: {exc}"


@tool
def check_exam_eligibility(attendance_percentage: float) -> str:
    """Check exam attendance eligibility using the task's 75%, 65%, and ₹500-per-course rules."""
    try:
        result = eligibility_rule(attendance_percentage)
    except ValueError as exc:
        return f"Invalid attendance: {exc}"
    fee = result["condonation_fee_per_course"]
    return (f"{result['attendance']:g}%: {result['status']}. {result['message']} "
            f"Condonation fee: ₹{fee:,} per course.")


def direct_eligibility_tests():
    print("Direct eligibility tool checks:")
    for value in (82, 70, 50):
        print(f"  {value}% -> {check_exam_eligibility.invoke({'attendance_percentage': value})}")


def main():
    direct_eligibility_tests()
    try:
        model = get_chat_model()
        tools = [search_handbook, get_course_fee, calculator, check_exam_eligibility]
        agent = create_react_agent(model, tools, prompt=SYSTEM_PROMPT, checkpointer=MemorySaver())
    except Exception as exc:
        raise SystemExit(
            f"Could not configure the agent: {exc}\n"
            "Check dependencies and .env. For Ollama, start the server and pull CHAT_MODEL; "
            "for Groq, set GROQ_API_KEY. Retrieval/eligibility tests can be run separately."
        ) from exc

    questions = [
        "What is the hostel in-time?",
        "What are the eligibility criteria for placements?",
        "What is the refund policy for international students?",
        "What is the total amount for CS101 and AI202 course fees, plus the maximum late fee?",
        "And if I pay only 5 days late instead?",
    ]
    config = {"configurable": {"thread_id": "day8-demo-thread"}}
    for number, question in enumerate(questions, 1):
        print("\n" + "=" * 78)
        print(f"QUESTION {number}: {question}")
        try:
            result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config)
            for message in result["messages"]:
                if getattr(message, "type", "") == "tool":
                    print(f"[TOOL {message.name}] {message.content}")
            print("ANSWER:", result["messages"][-1].content)
        except Exception as exc:
            print(f"Agent turn failed: {exc}")
            print("Check provider availability, model name, and API configuration.")
            break


if __name__ == "__main__":
    main()
