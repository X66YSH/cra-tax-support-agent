"""
Agent orchestrator: routes user messages through intent classification,
RAG retrieval, and action execution.

Extracted from test_chat.py into a reusable, stateful class.
"""

import sys
import os
import re
import json

# Add project root to path so we can import src.*
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.intent_classifier import classify_intent
from src.actions.tax_estimate import run_tax_estimate
from src.actions.filing_reminder import run_filing_reminder
from src.actions.benefit_eligibility import run_benefit_eligibility
from src.actions.book_appointment import run_book_appointment
from src.rag.retriever import retrieve, format_context_for_llm
from src.llm import chat


PARAM_QUESTIONS = {
    "income":            "What is your annual income in CAD?",
    "annual_income":     "What is your annual income in CAD?",
    "province":          "Which province do you live in?",
    "name":              "What is your name?",
    "email":             "What is your email address?",
    "residency_status":  "Are you a Canadian tax resident or non-resident?",
    "is_student":        "Are you currently enrolled as a student? (yes/no)",
    "has_tuition":       "Do you have a T2202 tuition certificate? (yes/no)",
    "student_type":      "Are you an undergraduate or graduate student?",
    "has_complex_taxes": "Do you have self-employment, foreign income >$1k, or capital gains? (yes/no)",
    "has_sin":           "Do you have your SIN ready? (yes/no)",
    "has_t4":            "Do you have your T4 slip? (yes/no)",
    "has_t2202":         "Do you have your T2202 tuition certificate? (yes/no)",
}

PARAM_ORDER = {
    "tax_estimate": ["income", "province"],
    "filing_reminder": ["name", "email"],
    "benefit_eligibility": ["residency_status", "annual_income", "is_student", "has_tuition"],
    "book_appointment": ["student_type", "annual_income", "has_complex_taxes", "has_sin", "has_t4", "has_t2202"],
}


def parse_response(param_name: str, response: str):
    response_lower = response.lower().strip()

    bool_params = ["has_complex_taxes", "has_sin", "has_t4", "has_t2202", "is_student", "has_tuition"]
    if param_name in bool_params:
        return response_lower in ["yes", "y", "yeah", "yep", "true", "i do", "i have"]

    if param_name in ["income", "annual_income"]:
        cleaned = response_lower.replace("k", "000").replace(",", "")
        numbers = re.findall(r"\d+", cleaned)
        return float(numbers[0]) if numbers else None

    if param_name == "student_type":
        if "grad" in response_lower and "under" not in response_lower:
            return "grad"
        if "under" in response_lower:
            return "undergrad"
        return response.strip()

    if param_name == "residency_status":
        return "non-resident" if "non" in response_lower else "resident"

    return response.strip()


def get_next_missing_param(action: str, params: dict):
    order = PARAM_ORDER.get(action, [])
    for param in order:
        if params.get(param) is None:
            return param
    return None


def call_action(action: str, params: dict) -> str:
    if action == "tax_estimate":
        return run_tax_estimate(income=params.get("income"), province=params.get("province"))
    elif action == "filing_reminder":
        return run_filing_reminder(name=params.get("name"), email=params.get("email"))
    elif action == "benefit_eligibility":
        return run_benefit_eligibility(
            residency_status=params.get("residency_status"),
            annual_income=params.get("annual_income"),
            is_student=params.get("is_student"),
            has_tuition=params.get("has_tuition"),
        )
    elif action == "book_appointment":
        return run_book_appointment(
            student_type=params.get("student_type"),
            annual_income=params.get("annual_income"),
            has_complex_taxes=params.get("has_complex_taxes"),
            has_sin=params.get("has_sin"),
            has_t4=params.get("has_t4"),
            has_t2202=params.get("has_t2202"),
        )
    return "I'm not sure how to help with that."


def process_message(user_input: str, state: dict) -> tuple[str, list[dict] | None]:
    """
    Process a user message given conversation state.

    Args:
        user_input: the user's message
        state: dict with keys action, params, awaiting

    Returns:
        (response_text, sources_or_none)
        Also mutates state in place.
    """
    sources = None

    # Mid-conversation: collecting parameters
    if state.get("action") and state.get("awaiting"):
        parsed = parse_response(state["awaiting"], user_input)
        state["params"][state["awaiting"]] = parsed

        next_param = get_next_missing_param(state["action"], state["params"])
        if next_param:
            state["awaiting"] = next_param
            return PARAM_QUESTIONS[next_param], None
        else:
            state["awaiting"] = None
            result = call_action(state["action"], state["params"])
            state["action"] = None
            state["params"] = {}
            return result, None

    # New message: classify intent
    classification = classify_intent(user_input)
    intent = classification["intent"]
    params = classification["parameters"]

    if intent == "out_of_scope":
        return (
            "I'm sorry, I can only help with Canadian tax questions for UofT students. "
            "I can help with tax estimates, benefit eligibility, filing reminders, "
            "or booking a UTSU tax clinic appointment."
        ), None

    if classification.get("clarification_needed"):
        return (
            "I'm not sure what you need help with. I can help you with:\n"
            "1. **Tax estimates** — calculate your federal/provincial tax\n"
            "2. **Benefit eligibility** — GST/HST credit, OTB, tuition credits\n"
            "3. **Filing reminders** — deadlines and checklist\n"
            "4. **Book appointment** — UTSU tax clinic\n\n"
            "What would you like help with?"
        ), None

    if intent == "general_question":
        results = retrieve(user_input, top_k=3)
        context = format_context_for_llm(results)
        response = chat([
            {
                "role": "system",
                "content": (
                    "You are a helpful CRA tax assistant for University of Toronto students. "
                    "Answer based on the provided CRA documents. Use markdown formatting. "
                    "Always cite your sources using [Source N] references. "
                    "Always add a disclaimer that this is general info, not professional tax advice."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {user_input}\n\nCRA Documents:\n{context}",
            },
        ])
        sources = [
            {"title": r["title"], "url": r["source_url"], "score": r["score"]}
            for r in results
        ]
        return response, sources

    # Action intent
    action_name = intent
    state["action"] = action_name

    param_mapping = {
        "tax_estimate": {
            "income": params.get("income"),
            "province": params.get("province"),
        },
        "filing_reminder": {
            "name": params.get("name"),
            "email": params.get("email"),
        },
        "benefit_eligibility": {
            "residency_status": params.get("residency_status"),
            "annual_income": params.get("income"),
            "is_student": params.get("is_student"),
            "has_tuition": params.get("has_tuition"),
        },
        "book_appointment": {
            "student_type": params.get("student_type"),
            "annual_income": params.get("income"),
            "has_complex_taxes": params.get("has_complex_taxes"),
            "has_sin": params.get("has_sin"),
            "has_t4": params.get("has_t4"),
            "has_t2202": params.get("has_t2202"),
        },
    }

    state["params"] = param_mapping.get(action_name, {})

    next_param = get_next_missing_param(action_name, state["params"])
    if next_param:
        state["awaiting"] = next_param
        return PARAM_QUESTIONS[next_param], None
    else:
        state["awaiting"] = None
        result = call_action(action_name, state["params"])
        state["action"] = None
        state["params"] = {}
        return result, None
