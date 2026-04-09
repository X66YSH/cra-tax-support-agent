"""
Action: calculate_tax_estimate
Collects income and province from the user, retrieves relevant CRA
tax bracket information, and returns a federal + provincial estimate.
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.rag.retriever import retrieve, format_context_for_llm
from src.llm import chat

# ---------------------------------------------------------------------------
# State definition — carries all information between nodes
# ---------------------------------------------------------------------------

class TaxEstimateState(TypedDict):
    income: float | None          # user's annual income
    province: str | None          # user's province
    context: str                  # retrieved RAG chunks
    answer: str                   # final LLM response
    messages: list[dict]          # conversation history
    awaiting: str | None          # tracks what we're waiting for from user

# ---------------------------------------------------------------------------
# Nodes — each is a single step in the graph
# ---------------------------------------------------------------------------

def ask_income(state: TaxEstimateState) -> TaxEstimateState:
    """Ask the user for their annual income if not provided."""
    state["messages"].append({
        "role": "assistant",
        "content": "Sure! To estimate your taxes, what is your total annual income in CAD? (e.g. 35000)"
    })
    state["awaiting"] = "income"
    return state


def ask_province(state: TaxEstimateState) -> TaxEstimateState:
    """Ask the user for their province if not provided."""
    state["messages"].append({
        "role": "assistant",
        "content": "Which province or territory do you live in? (e.g. Ontario, British Columbia, Alberta)"
    })
    state["awaiting"] = "province"
    return state


def retrieve_context(state: TaxEstimateState) -> TaxEstimateState:
    """Retrieve relevant CRA tax bracket info from ChromaDB."""
    query = f"federal and provincial income tax brackets for income {state['income']} in {state['province']}"
    results = retrieve(query, feature="tax_estimate", top_k=5)
    state["context"] = format_context_for_llm(results)
    state["awaiting"] = None
    return state


def generate_estimate(state: TaxEstimateState) -> TaxEstimateState:
    """Send income, province, and RAG context to LLM to generate estimate."""
    system_prompt = """You are a helpful CRA tax assistant for UofT students in Canada.
Using the provided CRA source documents, give a concise federal and provincial tax estimate.
In 3-4 lines maximum per section, include:
- Approximate federal tax owing (after basic personal amount)
- Approximate provincial tax owing
- Top 2 deductions the student should know about

Be concise. End with: 'This is a general estimate only. Please consult a tax professional or visit a CVITP free tax clinic for personalized advice.'
Cite sources inline."""

    user_message = f"""Please estimate the taxes for a student with the following details:
- Annual income: ${state['income']:,.0f} CAD
- Province: {state['province']}

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
# Routing logic — decides which node to go to next
# ---------------------------------------------------------------------------

def route_after_start(state: TaxEstimateState) -> str:
    """Route based on what information we still need."""
    if state.get("income") is None:
        return "ask_income"
    if state.get("province") is None:
        return "ask_province"
    return "retrieve_context"


def route_after_income(state: TaxEstimateState) -> str:
    if state.get("province") is None:
        return "ask_province"
    return "retrieve_context"

# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_tax_estimate_graph():
    graph = StateGraph(TaxEstimateState)

    # Add nodes
    graph.add_node("ask_income", ask_income)
    graph.add_node("ask_province", ask_province)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("generate_estimate", generate_estimate)

    # Entry point
    graph.set_conditional_entry_point(
        route_after_start,
        {
            "ask_income": "ask_income",
            "ask_province": "ask_province",
            "retrieve_context": "retrieve_context",
        }
    )

    # Edges
    graph.add_conditional_edges(
        "ask_income",
        route_after_income,
        {
            "ask_province": "ask_province",
            "retrieve_context": "retrieve_context",
        }
    )
    graph.add_edge("ask_province", "retrieve_context")
    graph.add_edge("retrieve_context", "generate_estimate")
    graph.add_edge("generate_estimate", END)

    return graph.compile()


# Singleton graph instance
tax_estimate_graph = build_tax_estimate_graph()


# ---------------------------------------------------------------------------
# Public entry point for the agent layer
# ---------------------------------------------------------------------------

def run_tax_estimate(income: float, province: str) -> str:
    """
    Run the tax estimate action.
    Args:
        income: user's annual income in CAD
        province: user's province or territory
    Returns:
        LLM-generated tax estimate as a string
    """
    initial_state: TaxEstimateState = {
        "income": income,
        "province": province,
        "context": "",
        "answer": "",
        "messages": [],
        "awaiting": None,
    }

    final_state = tax_estimate_graph.invoke(initial_state)
    return final_state["answer"]


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = run_tax_estimate(income=35000, province="Ontario")
    print(result)