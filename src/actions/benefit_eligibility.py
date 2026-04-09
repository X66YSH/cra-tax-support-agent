"""
Action: check_benefit_eligibility
Multi-turn action (4 turns) that checks eligibility for:
- GST/HST Credit
- Ontario Trillium Benefit (OTB)
- Tuition carry-forward credit
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.rag.retriever import retrieve, format_context_for_llm
from src.llm import chat

# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------

class BenefitEligibilityState(TypedDict):
    residency_status: str | None    # "resident" or "non-resident"
    annual_income: float | None     # user's annual income
    is_student: bool | None         # whether user is a student
    has_tuition: bool | None        # whether user has tuition receipts
    context: str                    # retrieved RAG chunks
    answer: str                     # final LLM response
    messages: list[dict]            # conversation history
    awaiting: str | None            # tracks what we're waiting for

# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def ask_residency(state: BenefitEligibilityState) -> BenefitEligibilityState:
    state["messages"].append({
        "role": "assistant",
        "content": "I can check your eligibility for Canadian tax benefits! First, are you a Canadian tax resident or a non-resident? (reply 'resident' or 'non-resident')"
    })
    state["awaiting"] = "residency_status"
    return state


def ask_income(state: BenefitEligibilityState) -> BenefitEligibilityState:
    state["messages"].append({
        "role": "assistant",
        "content": "What is your approximate annual income in CAD? (e.g. 25000)"
    })
    state["awaiting"] = "annual_income"
    return state


def ask_student(state: BenefitEligibilityState) -> BenefitEligibilityState:
    state["messages"].append({
        "role": "assistant",
        "content": "Are you currently enrolled as a student at a Canadian post-secondary institution? (yes or no)"
    })
    state["awaiting"] = "is_student"
    return state


def ask_tuition(state: BenefitEligibilityState) -> BenefitEligibilityState:
    state["messages"].append({
        "role": "assistant",
        "content": "Do you have a T2202 tuition certificate from your institution? (yes or no)"
    })
    state["awaiting"] = "has_tuition"
    return state


def retrieve_context(state: BenefitEligibilityState) -> BenefitEligibilityState:
    query = (
        f"GST/HST credit Ontario Trillium Benefit tuition carry-forward eligibility "
        f"income {state['annual_income']} resident student"
    )
    results = retrieve(query, feature="benefit_eligibility", top_k=5)
    state["context"] = format_context_for_llm(results)
    state["awaiting"] = None
    return state


def generate_eligibility(state: BenefitEligibilityState) -> BenefitEligibilityState:
    system_prompt = """You are a helpful CRA tax assistant for UofT students.
Based on the user's information and CRA source documents, determine eligibility for:
1. GST/HST Credit
2. Ontario Trillium Benefit (OTB)
3. Tuition carry-forward credit (Schedule 11)

For each benefit state in 2-3 lines maximum:
- Eligible / Not Eligible / Possibly Eligible
- One sentence why
- One sentence next step

Be concise. End with: 'This is a general eligibility check only. Visit a CVITP free tax clinic at UTSU for personalized advice.'"""

    user_message = f"""Check benefit eligibility for a student with:
- Residency status: {state['residency_status']}
- Annual income: ${state['annual_income']:,.0f} CAD
- Currently enrolled as student: {state['is_student']}
- Has T2202 tuition certificate: {state['has_tuition']}

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

def route_after_start(state: BenefitEligibilityState) -> str:
    if state.get("residency_status") is None:
        return "ask_residency"
    if state.get("annual_income") is None:
        return "ask_income"
    if state.get("is_student") is None:
        return "ask_student"
    if state.get("has_tuition") is None:
        return "ask_tuition"
    return "retrieve_context"


def route_after_residency(state: BenefitEligibilityState) -> str:
    if state.get("annual_income") is None:
        return "ask_income"
    if state.get("is_student") is None:
        return "ask_student"
    if state.get("has_tuition") is None:
        return "ask_tuition"
    return "retrieve_context"


def route_after_income(state: BenefitEligibilityState) -> str:
    if state.get("is_student") is None:
        return "ask_student"
    if state.get("has_tuition") is None:
        return "ask_tuition"
    return "retrieve_context"


def route_after_student(state: BenefitEligibilityState) -> str:
    if state.get("has_tuition") is None:
        return "ask_tuition"
    return "retrieve_context"

# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_benefit_eligibility_graph():
    graph = StateGraph(BenefitEligibilityState)

    graph.add_node("ask_residency", ask_residency)
    graph.add_node("ask_income", ask_income)
    graph.add_node("ask_student", ask_student)
    graph.add_node("ask_tuition", ask_tuition)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("generate_eligibility", generate_eligibility)

    graph.set_conditional_entry_point(
        route_after_start,
        {
            "ask_residency": "ask_residency",
            "ask_income": "ask_income",
            "ask_student": "ask_student",
            "ask_tuition": "ask_tuition",
            "retrieve_context": "retrieve_context",
        }
    )

    graph.add_conditional_edges("ask_residency", route_after_residency, {
        "ask_income": "ask_income",
        "ask_student": "ask_student",
        "ask_tuition": "ask_tuition",
        "retrieve_context": "retrieve_context",
    })
    graph.add_conditional_edges("ask_income", route_after_income, {
        "ask_student": "ask_student",
        "ask_tuition": "ask_tuition",
        "retrieve_context": "retrieve_context",
    })
    graph.add_conditional_edges("ask_student", route_after_student, {
        "ask_tuition": "ask_tuition",
        "retrieve_context": "retrieve_context",
    })
    graph.add_edge("ask_tuition", "retrieve_context")
    graph.add_edge("retrieve_context", "generate_eligibility")
    graph.add_edge("generate_eligibility", END)

    return graph.compile()


benefit_eligibility_graph = build_benefit_eligibility_graph()

# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_benefit_eligibility(
    residency_status: str,
    annual_income: float,
    is_student: bool,
    has_tuition: bool
) -> str:
    initial_state: BenefitEligibilityState = {
        "residency_status": residency_status,
        "annual_income": annual_income,
        "is_student": is_student,
        "has_tuition": has_tuition,
        "context": "",
        "answer": "",
        "messages": [],
        "awaiting": None,
    }

    final_state = benefit_eligibility_graph.invoke(initial_state)
    return final_state["answer"]


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = run_benefit_eligibility(
        residency_status="resident",
        annual_income=25000,
        is_student=True,
        has_tuition=True
    )
    print(result)