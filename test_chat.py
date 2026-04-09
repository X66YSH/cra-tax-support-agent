"""
Quick interactive chat test for multi-turn conversations.
Run with: python test_chat.py
Type 'quit' to exit, 'reset' to start a new conversation.
"""

from src.intent_classifier import classify_intent, route_to_action
from src.actions.tax_estimate import run_tax_estimate
from src.actions.filing_reminder import run_filing_reminder
from src.actions.benefit_eligibility import run_benefit_eligibility
from src.actions.book_appointment import run_book_appointment

# Conversation state
state = {
    "action": None,
    "params": {},
    "awaiting": None,
}

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


def parse_response(param_name: str, response: str):
    """Parse user response into the correct type for each parameter."""
    import re
    response_lower = response.lower().strip()

    bool_params = ["has_complex_taxes", "has_sin", "has_t4", "has_t2202",
                   "is_student", "has_tuition"]
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
    """Return the next parameter we still need to collect."""
    if action == "tax_estimate":
        order = ["income", "province"]
    elif action == "filing_reminder":
        order = ["name", "email"]
    elif action == "benefit_eligibility":
        order = ["residency_status", "annual_income", "is_student", "has_tuition"]
    elif action == "book_appointment":
        order = ["student_type", "annual_income", "has_complex_taxes",
                 "has_sin", "has_t4", "has_t2202"]
    else:
        return None

    for param in order:
        if params.get(param) is None:
            return param
    return None


def call_action(action: str, params: dict) -> str:
    """Call the appropriate action with collected parameters."""
    print("\n🤖 Agent: Let me look that up for you...\n")

    if action == "tax_estimate":
        return run_tax_estimate(
            income=params.get("income"),
            province=params.get("province")
        )
    elif action == "filing_reminder":
        return run_filing_reminder(
            name=params.get("name"),
            email=params.get("email")
        )
    elif action == "benefit_eligibility":
        return run_benefit_eligibility(
            residency_status=params.get("residency_status"),
            annual_income=params.get("annual_income"),
            is_student=params.get("is_student"),
            has_tuition=params.get("has_tuition")
        )
    elif action == "book_appointment":
        return run_book_appointment(
            student_type=params.get("student_type"),
            annual_income=params.get("annual_income"),
            has_complex_taxes=params.get("has_complex_taxes"),
            has_sin=params.get("has_sin"),
            has_t4=params.get("has_t4"),
            has_t2202=params.get("has_t2202")
        )
    return "I'm not sure how to help with that."


def reset_state():
    state["action"] = None
    state["params"] = {}
    state["awaiting"] = None
    print("\n🔄 Conversation reset. Start a new query!\n")


def process_message(user_input: str) -> str:
    """Process a user message and return agent response."""

    # If we're mid-conversation collecting params
    if state["action"] and state["awaiting"]:
        # Parse and store the user's response
        parsed = parse_response(state["awaiting"], user_input)
        state["params"][state["awaiting"]] = parsed
        print(f"   [Collected: {state['awaiting']} = {parsed}]")

        # Check what's still missing
        next_param = get_next_missing_param(state["action"], state["params"])

        if next_param:
            state["awaiting"] = next_param
            return PARAM_QUESTIONS[next_param]
        else:
            # All params collected — run the action
            state["awaiting"] = None
            result = call_action(state["action"], state["params"])
            reset_state()
            return result

    # New conversation — classify intent
    classification = classify_intent(user_input)
    intent = classification["intent"]
    params = classification["parameters"]

    print(f"   [Intent: {intent} | Confidence: {classification['confidence']}]")

    # Handle out of scope
    if intent == "out_of_scope":
        return ("I'm sorry, I can only help with Canadian tax questions for UofT students. "
                "I can help with tax estimates, benefit eligibility, filing reminders, "
                "or booking a UTSU tax clinic appointment.")

    # Handle clarification needed
    if classification.get("clarification_needed"):
        return ("I'm not sure what you need help with. I can help you with:\n"
                "1. Tax estimates\n"
                "2. Benefit eligibility (GST/HST, OTB, tuition credits)\n"
                "3. Filing reminders\n"
                "4. Booking a UTSU tax clinic appointment\n"
                "What would you like help with?")

    # Handle general questions
    if intent == "general_question":
        from src.rag.retriever import retrieve, format_context_for_llm
        from src.llm import chat
        results = retrieve(user_input, top_k=3)
        context = format_context_for_llm(results)
        response = chat([
            {"role": "system", "content": "You are a helpful CRA tax assistant for UofT students. Answer based on the provided CRA documents. Always add a disclaimer."},
            {"role": "user", "content": f"Question: {user_input}\n\nCRA Documents:\n{context}"}
        ])
        return response

    # Map intent to action name
    action_map = {
        "tax_estimate": "tax_estimate",
        "benefit_eligibility": "benefit_eligibility",
        "filing_reminder": "filing_reminder",
        "book_appointment": "book_appointment",
    }

    state["action"] = action_map[intent]

    # Pre-fill params already extracted from the message
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

    state["params"] = param_mapping[state["action"]]
    print(f"   [Pre-filled params: {state['params']}]")

    # Check what's still missing
    next_param = get_next_missing_param(state["action"], state["params"])

    if next_param:
        state["awaiting"] = next_param
        return PARAM_QUESTIONS[next_param]
    else:
        # All params already provided — run action directly
        state["awaiting"] = None
        result = call_action(state["action"], state["params"])
        reset_state()
        return result


# ---------------------------------------------------------------------------
# Main chat loop
# ---------------------------------------------------------------------------

print("=" * 60)
print("🍁 CRA Tax Support Agent — Interactive Test")
print("=" * 60)
print("Commands: 'quit' to exit, 'reset' to start over")
print("Try: 'I want to book a tax clinic appointment'")
print("=" * 60)

while True:
    try:
        user_input = input("\n👤 You: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        break

    if not user_input:
        continue

    if user_input.lower() == "quit":
        print("Goodbye!")
        break

    if user_input.lower() == "reset":
        reset_state()
        continue

    response = process_message(user_input)
    print(f"\n🤖 Agent: {response}")