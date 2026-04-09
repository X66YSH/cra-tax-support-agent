"""
Action: create_filing_reminder
Collects the user's name and email over 2 turns, then generates
a mock filing reminder for the April 30 CRA tax deadline.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.rag.retriever import retrieve, format_context_for_llm
from src.llm import chat

# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------

class FilingReminderState(TypedDict):
    name: str | None          # user's name
    email: str | None         # user's email
    context: str              # retrieved RAG chunks
    answer: str               # final reminder message
    messages: list[dict]      # conversation history
    awaiting: str | None      # tracks what we're waiting for

# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def ask_name(state: FilingReminderState) -> FilingReminderState:
    """Ask the user for their name."""
    state["messages"].append({
        "role": "assistant",
        "content": "Sure! I can set up a tax filing reminder for you. What is your name?"
    })
    state["awaiting"] = "name"
    return state


def ask_email(state: FilingReminderState) -> FilingReminderState:
    """Ask the user for their email."""
    state["messages"].append({
        "role": "assistant",
        "content": f"Thanks {state['name']}! What email address should I send the reminder to?"
    })
    state["awaiting"] = "email"
    return state


def retrieve_context(state: FilingReminderState) -> FilingReminderState:
    """Retrieve relevant CRA deadline information from ChromaDB."""
    query = "tax filing deadline April 30 Canada late filing penalty"
    results = retrieve(query, feature="filing_reminder", top_k=3)
    state["context"] = format_context_for_llm(results)
    state["awaiting"] = None
    return state


def generate_reminder(state: FilingReminderState) -> FilingReminderState:
    """Generate a mock filing reminder email using the LLM."""
    system_prompt = """You are a helpful CRA tax assistant for UofT students.
Generate a friendly reminder email for the Canadian tax filing deadline.
The reminder should include:
- The April 30 filing deadline
- Key documents needed (T4, T2202, SIN)
- Late filing penalties if they miss the deadline
- Mention of free CVITP tax clinics at UTSU
Keep it friendly, concise and helpful.
Always end with a disclaimer that this is a general reminder only."""

    user_message = f"""Generate a tax filing reminder email for:
- Name: {state['name']}
- Email: {state['email']}

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

def route_after_start(state: FilingReminderState) -> str:
    if state.get("name") is None:
        return "ask_name"
    if state.get("email") is None:
        return "ask_email"
    return "retrieve_context"


def route_after_name(state: FilingReminderState) -> str:
    if state.get("email") is None:
        return "ask_email"
    return "retrieve_context"

# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_filing_reminder_graph():
    graph = StateGraph(FilingReminderState)

    graph.add_node("ask_name", ask_name)
    graph.add_node("ask_email", ask_email)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("generate_reminder", generate_reminder)

    graph.set_conditional_entry_point(
        route_after_start,
        {
            "ask_name": "ask_name",
            "ask_email": "ask_email",
            "retrieve_context": "retrieve_context",
        }
    )

    graph.add_conditional_edges(
        "ask_name",
        route_after_name,
        {
            "ask_email": "ask_email",
            "retrieve_context": "retrieve_context",
        }
    )
    graph.add_edge("ask_email", "retrieve_context")
    graph.add_edge("retrieve_context", "generate_reminder")
    graph.add_edge("generate_reminder", END)

    return graph.compile()


filing_reminder_graph = build_filing_reminder_graph()

# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_filing_reminder(name: str, email: str) -> str:
    """
    Run the filing reminder action.
    Args:
        name: user's name
        email: user's email address
    Returns:
        LLM-generated reminder email as a string
    """
    initial_state: FilingReminderState = {
        "name": name,
        "email": email,
        "context": "",
        "answer": "",
        "messages": [],
        "awaiting": None,
    }

    final_state = filing_reminder_graph.invoke(initial_state)
    return final_state["answer"]

# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = run_filing_reminder(name="Krishitha", email="krishitha@mail.utoronto.ca")
    print(result)