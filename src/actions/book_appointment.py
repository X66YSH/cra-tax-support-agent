"""
Action: book_tax_clinic_appt
Multi-turn action (5-6 turns) that:
1. Checks CVITP eligibility (income, complexity)
2. Collects student info (undergrad/grad, income)
3. Checks for complex tax situations
4. Collects document status (SIN, T4, T2202) separately
5. Generates personalized document checklist
6. Provides UTSU booking link
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.rag.retriever import retrieve, format_context_for_llm
from src.llm import chat

# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------

class AppointmentState(TypedDict):
    student_type: str | None        # "undergrad" or "grad"
    annual_income: float | None     # user's annual income
    has_complex_taxes: bool | None  # self-employed, foreign income > $1k, capital gains
    has_sin: bool | None            # whether user has SIN
    has_t4: bool | None             # whether user has T4 slip
    has_t2202: bool | None          # whether user has T2202
    is_eligible: bool | None        # CVITP eligibility result
    context: str                    # retrieved RAG chunks
    answer: str                     # final response
    messages: list[dict]            # conversation history
    awaiting: str | None            # tracks what we're waiting for

# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def ask_student_type(state: AppointmentState) -> AppointmentState:
    state["messages"].append({
        "role": "assistant",
        "content": "I can help you book a free tax clinic appointment at UTSU! Are you an undergraduate or graduate student?"
    })
    state["awaiting"] = "student_type"
    return state


def ask_income(state: AppointmentState) -> AppointmentState:
    state["messages"].append({
        "role": "assistant",
        "content": "What is your approximate annual income in CAD? (CVITP clinics are for individuals with income under $35,000)"
    })
    state["awaiting"] = "annual_income"
    return state


def ask_complex_taxes(state: AppointmentState) -> AppointmentState:
    state["messages"].append({
        "role": "assistant",
        "content": "Do you have any of the following: self-employment income, foreign income over $1,000, or capital gains? (yes or no)"
    })
    state["awaiting"] = "has_complex_taxes"
    return state


def ask_sin(state: AppointmentState) -> AppointmentState:
    state["messages"].append({
        "role": "assistant",
        "content": "Do you have your Social Insurance Number (SIN) ready? (yes or no)"
    })
    state["awaiting"] = "has_sin"
    return state


def ask_t4(state: AppointmentState) -> AppointmentState:
    state["messages"].append({
        "role": "assistant",
        "content": "Do you have your T4 slip from your employer? (yes or no)"
    })
    state["awaiting"] = "has_t4"
    return state


def ask_t2202(state: AppointmentState) -> AppointmentState:
    state["messages"].append({
        "role": "assistant",
        "content": "Do you have your T2202 tuition certificate from UofT? (yes or no)"
    })
    state["awaiting"] = "has_t2202"
    return state


def check_eligibility(state: AppointmentState) -> AppointmentState:
    """Determine CVITP eligibility based on collected info."""
    income = state.get("annual_income") or 0
    has_complex = state.get("has_complex_taxes", False)
    state["is_eligible"] = income <= 35000 and not has_complex
    state["awaiting"] = None
    return state


def retrieve_context(state: AppointmentState) -> AppointmentState:
    """Retrieve CVITP and UTSU appointment info from ChromaDB."""
    query = "CVITP free tax clinic UTSU appointment booking eligibility documents needed"
    results = retrieve(query, feature="book_appointment", top_k=5)
    state["context"] = format_context_for_llm(results)
    return state


def generate_response(state: AppointmentState) -> AppointmentState:
    """Generate appointment booking response or ineligibility explanation."""

    if not state["is_eligible"]:
        income = state.get("annual_income") or 0
        has_complex = state.get("has_complex_taxes", False)

        # Build specific reason for ineligibility
        reasons = []
        if income > 35000:
            reasons.append(f"your income (${income:,.0f}) exceeds the $35,000 CVITP limit")
        if has_complex:
            reasons.append("you have a complex tax situation (self-employment, foreign income, or capital gains)")
        reason_str = " and ".join(reasons)

        system_prompt = f"""You are a helpful CRA tax assistant for UofT students.
The student is not eligible for the free CVITP tax clinic because {reason_str}.
Explain this clearly and redirect them to:
- CRA's website for self-filing guidance
- NETFILE certified software options
- A professional tax advisor for complex situations
Be empathetic and helpful. Keep response under 150 words."""

        user_message = f"""Student details:
- Student type: {state['student_type']}
- Annual income: ${income:,.0f} CAD
- Complex tax situation: {has_complex}
- Reason ineligible: {reason_str}

CRA Source Documents:
{state['context']}"""

    else:
        has_sin = state.get("has_sin", False)
        has_t4 = state.get("has_t4", False)
        has_t2202 = state.get("has_t2202", False)

        missing_docs = []
        ready_docs = []

        if has_sin:
            ready_docs.append("✅ Social Insurance Number (SIN)")
        else:
            missing_docs.append("❌ Social Insurance Number (SIN) — apply at Service Canada")

        if has_t4:
            ready_docs.append("✅ T4 slip")
        else:
            missing_docs.append("❌ T4 slip — contact your employer")

        if has_t2202:
            ready_docs.append("✅ T2202 tuition certificate")
        else:
            missing_docs.append("❌ T2202 tuition certificate — download from ACORN")

        system_prompt = """You are a helpful CRA tax assistant for UofT students.
The student is eligible for the free CVITP tax clinic at UTSU.
Generate a response that includes:
1. Confirmation they are eligible
2. Their document checklist (ready and missing items)
3. The UTSU booking link: https://www.utsu.ca/tax
4. A reminder about the April 30 deadline
Be concise and friendly. End with:
'This is general guidance only. Contact UTSU directly for appointment availability.'"""

        user_message = f"""Student details:
- Student type: {state['student_type']}
- Annual income: ${state.get('annual_income', 0):,.0f} CAD

Documents ready:
{chr(10).join(ready_docs) if ready_docs else 'None'}

Documents missing:
{chr(10).join(missing_docs) if missing_docs else 'None - all documents ready!'}

CRA Source Documents:
{state['context']}"""

    response = chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ])

    state["answer"] = response
    state["messages"].append({
        "role": "assistant",
        "content": response
    })
    return state

# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------

def route_after_start(state: AppointmentState) -> str:
    if state.get("student_type") is None:
        return "ask_student_type"
    if state.get("annual_income") is None:
        return "ask_income"
    if state.get("has_complex_taxes") is None:
        return "ask_complex_taxes"
    return "check_eligibility"


def route_after_student_type(state: AppointmentState) -> str:
    if state.get("annual_income") is None:
        return "ask_income"
    if state.get("has_complex_taxes") is None:
        return "ask_complex_taxes"
    return "check_eligibility"


def route_after_income(state: AppointmentState) -> str:
    if state.get("has_complex_taxes") is None:
        return "ask_complex_taxes"
    return "check_eligibility"


def route_after_eligibility(state: AppointmentState) -> str:
    if not state["is_eligible"]:
        return "retrieve_context"
    if state.get("has_sin") is None:
        return "ask_sin"
    if state.get("has_t4") is None:
        return "ask_t4"
    if state.get("has_t2202") is None:
        return "ask_t2202"
    return "retrieve_context"


def route_after_sin(state: AppointmentState) -> str:
    if state.get("has_t4") is None:
        return "ask_t4"
    if state.get("has_t2202") is None:
        return "ask_t2202"
    return "retrieve_context"


def route_after_t4(state: AppointmentState) -> str:
    if state.get("has_t2202") is None:
        return "ask_t2202"
    return "retrieve_context"

# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_appointment_graph():
    graph = StateGraph(AppointmentState)

    graph.add_node("ask_student_type", ask_student_type)
    graph.add_node("ask_income", ask_income)
    graph.add_node("ask_complex_taxes", ask_complex_taxes)
    graph.add_node("check_eligibility", check_eligibility)
    graph.add_node("ask_sin", ask_sin)
    graph.add_node("ask_t4", ask_t4)
    graph.add_node("ask_t2202", ask_t2202)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("generate_response", generate_response)

    graph.set_conditional_entry_point(
        route_after_start,
        {
            "ask_student_type": "ask_student_type",
            "ask_income": "ask_income",
            "ask_complex_taxes": "ask_complex_taxes",
            "check_eligibility": "check_eligibility",
        }
    )

    graph.add_conditional_edges("ask_student_type", route_after_student_type, {
        "ask_income": "ask_income",
        "ask_complex_taxes": "ask_complex_taxes",
        "check_eligibility": "check_eligibility",
    })
    graph.add_conditional_edges("ask_income", route_after_income, {
        "ask_complex_taxes": "ask_complex_taxes",
        "check_eligibility": "check_eligibility",
    })
    graph.add_edge("ask_complex_taxes", "check_eligibility")
    graph.add_conditional_edges("check_eligibility", route_after_eligibility, {
        "retrieve_context": "retrieve_context",
        "ask_sin": "ask_sin",
        "ask_t4": "ask_t4",
        "ask_t2202": "ask_t2202",
    })
    graph.add_conditional_edges("ask_sin", route_after_sin, {
        "ask_t4": "ask_t4",
        "ask_t2202": "ask_t2202",
        "retrieve_context": "retrieve_context",
    })
    graph.add_conditional_edges("ask_t4", route_after_t4, {
        "ask_t2202": "ask_t2202",
        "retrieve_context": "retrieve_context",
    })
    graph.add_edge("ask_t2202", "retrieve_context")
    graph.add_edge("retrieve_context", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()


appointment_graph = build_appointment_graph()

# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_book_appointment(
    student_type: str,
    annual_income: float,
    has_complex_taxes: bool,
    has_sin: bool,
    has_t4: bool,
    has_t2202: bool,
) -> str:
    initial_state: AppointmentState = {
        "student_type": student_type,
        "annual_income": annual_income,
        "has_complex_taxes": has_complex_taxes,
        "has_sin": has_sin,
        "has_t4": has_t4,
        "has_t2202": has_t2202,
        "is_eligible": None,
        "context": "",
        "answer": "",
        "messages": [],
        "awaiting": None,
    }

    final_state = appointment_graph.invoke(initial_state)
    return final_state["answer"]


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Test 1: Eligible student, missing T2202 ===")
    result = run_book_appointment(
        student_type="grad",
        annual_income=25000,
        has_complex_taxes=False,
        has_sin=True,
        has_t4=True,
        has_t2202=False,
    )
    print(result)

    print("\n=== Test 2: Ineligible - complex taxes ===")
    result = run_book_appointment(
        student_type="grad",
        annual_income=25000,
        has_complex_taxes=False,
        has_sin=True,
        has_t4=True,
        has_t2202=True,
    )
    print(result)

    print("\n=== Test 3: Ineligible - income too high ===")
    result = run_book_appointment(
        student_type="undergrad",
        annual_income=20000,
        has_complex_taxes=False,
        has_sin=True,
        has_t4=True,
        has_t2202=True,
    )
    print(result)