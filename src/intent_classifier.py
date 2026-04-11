"""
Intent Classifier for CRA Tax Support Agent.

Reads the user's message and:
1. Classifies intent into one of 5 categories
2. Extracts parameters already present in the message
3. Returns structured output for the agent to route correctly

Intents:
    tax_estimate         → calculate_tax_estimate action
    benefit_eligibility  → check_benefit_eligibility action
    filing_reminder      → create_filing_reminder action
    book_appointment     → book_tax_clinic_appt action
    out_of_scope         → guardrails / rejection
    general_question     → RAG-based answer, no action needed
"""

import json
import re
import logging
from src.llm import chat

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Intent classification prompt
# ---------------------------------------------------------------------------

CLASSIFIER_SYSTEM_PROMPT = """You are an intent classifier for a CRA Tax Support Agent for UofT students.

Your job is to analyze the user's message and return a JSON object with:
1. intent: one of these exact values:
   - "tax_estimate" — user wants to know how much tax they owe
   - "benefit_eligibility" — user wants to know if they qualify for GST/HST credit, OTB, tuition credits
   - "filing_reminder" — user wants a reminder about tax filing deadlines
   - "book_appointment" — user wants to book a UTSU/CVITP free tax clinic appointment
   - "general_question" — user has a general CRA/tax question that can be answered from knowledge base
   - "out_of_scope" — user is asking something unrelated to Canadian taxes or is trying to misuse the agent

2. parameters: a dict of any values already present in the message:
   - income: float or null (annual income in CAD)
   - province: string or null (Canadian province/territory)
   - name: string or null (user's name)
   - email: string or null (user's email)
   - residency_status: "resident" or "non-resident" or null
   - is_student: true/false or null
   - has_tuition: true/false or null
   - student_type: "undergrad" or "grad" or null
   - has_complex_taxes: true/false or null
   - has_sin: true/false or null
   - has_t4: true/false or null
   - has_t2202: true/false or null

3. confidence: "high", "medium", or "low"

4. clarification_needed: true if the message is too ambiguous to classify confidently

5. reason: one sentence explaining your classification

IMPORTANT RULES:
- Return ONLY valid JSON, no markdown, no explanation outside the JSON
- Be concise and fast — do not overthink, just classify and extract
- For out_of_scope: tax evasion, filing for someone else, illegal advice, unrelated topics
- For general_question: factual tax questions that don't require collecting parameters
- Extract income even if written as "18k", "18,000", "$18000" — always convert to float
- Extract province even if abbreviated: "ON" → "Ontario", "BC" → "British Columbia"

Example output:
{
  "intent": "tax_estimate",
  "parameters": {
    "income": 28000,
    "province": "Ontario",
    "name": null,
    "email": null,
    "residency_status": null,
    "is_student": null,
    "has_tuition": null,
    "student_type": null,
    "has_complex_taxes": null,
    "has_sin": null,
    "has_t4": null,
    "has_t2202": null
  },
  "confidence": "high",
  "clarification_needed": false,
  "reason": "User explicitly asked about tax owing with income and province provided."
}"""


# ---------------------------------------------------------------------------
# Province name normalization
# ---------------------------------------------------------------------------

PROVINCE_MAP = {
    "on": "Ontario", "ont": "Ontario",
    "bc": "British Columbia", "ab": "Alberta",
    "qc": "Quebec", "que": "Quebec",
    "mb": "Manitoba", "sk": "Saskatchewan",
    "ns": "Nova Scotia", "nb": "New Brunswick",
    "nl": "Newfoundland and Labrador", "nfld": "Newfoundland and Labrador",
    "pe": "Prince Edward Island", "pei": "Prince Edward Island",
    "nt": "Northwest Territories", "nu": "Nunavut", "yt": "Yukon",
}


def normalize_province(province: str | None) -> str | None:
    """Normalize province abbreviations to full names."""
    if not province:
        return None
    lower = province.lower().strip()
    return PROVINCE_MAP.get(lower, province.title())


# ---------------------------------------------------------------------------
# Main classifier function
# ---------------------------------------------------------------------------

def classify_intent(user_message: str, conversation_history: list[dict] = None) -> dict:
    """
    Classify the intent of a user message and extract parameters.

    Args:
        user_message: the user's raw input
        conversation_history: optional list of previous messages for context

    Returns:
        dict with keys: intent, parameters, confidence, clarification_needed, reason
    """
    # Build messages for LLM
    messages = [{"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT}]

    # Add conversation history for context if available
    if conversation_history:
        # Only include last 4 messages for context
        messages.extend(conversation_history[-4:])

    messages.append({"role": "user", "content": user_message})

    try:
        response = chat(messages, max_tokens=800)

        if not response:
            logger.warning("Empty response from LLM classifier")
            return _fallback_classification()

        # Strip markdown code blocks if present
        clean = response.strip()
        if clean.startswith("```"):
            clean = re.sub(r"```(?:json)?\n?", "", clean).strip()
            clean = clean.rstrip("`").strip()

        result = json.loads(clean)

        # Normalize province if extracted
        if result.get("parameters", {}).get("province"):
            result["parameters"]["province"] = normalize_province(
                result["parameters"]["province"]
            )

        logger.info(f"Intent: {result.get('intent')} | Confidence: {result.get('confidence')}")
        return result

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse classifier response: {e}")
        return _fallback_classification()
    except Exception as e:
        logger.warning(f"Classifier error: {e}")
        return _fallback_classification()


def _fallback_classification() -> dict:
    """Return a safe fallback when classification fails."""
    return {
        "intent": "general_question",
        "parameters": {
            "income": None, "province": None, "name": None,
            "email": None, "residency_status": None, "is_student": None,
            "has_tuition": None, "student_type": None, "has_complex_taxes": None,
            "has_sin": None, "has_t4": None, "has_t2202": None,
        },
        "confidence": "low",
        "clarification_needed": True,
        "reason": "Classification failed — defaulting to general question."
    }


# ---------------------------------------------------------------------------
# Router — connects classifier output to your actions
# ---------------------------------------------------------------------------

def route_to_action(classification: dict) -> dict:
    """
    Given a classification result, determine which action to call
    and with which parameters.

    Returns:
        dict with keys: action, params, should_ask_clarification, message
    """
    intent = classification.get("intent")
    params = classification.get("parameters", {})
    clarification_needed = classification.get("clarification_needed", False)

    if clarification_needed or classification.get("confidence") == "low":
        return {
            "action": "clarify",
            "params": {},
            "should_ask_clarification": True,
            "message": "I'm not sure what you need help with. Could you clarify? I can help with tax estimates, benefit eligibility, filing reminders, or booking a UTSU tax clinic appointment."
        }

    if intent == "tax_estimate":
        return {
            "action": "tax_estimate",
            "params": {
                "income": params.get("income"),
                "province": params.get("province"),
            },
            "should_ask_clarification": False,
            "message": None
        }

    elif intent == "benefit_eligibility":
        return {
            "action": "benefit_eligibility",
            "params": {
                "residency_status": params.get("residency_status"),
                "annual_income": params.get("income"),
                "is_student": params.get("is_student"),
                "has_tuition": params.get("has_tuition"),
            },
            "should_ask_clarification": False,
            "message": None
        }

    elif intent == "filing_reminder":
        return {
            "action": "filing_reminder",
            "params": {
                "name": params.get("name"),
                "email": params.get("email"),
            },
            "should_ask_clarification": False,
            "message": None
        }

    elif intent == "book_appointment":
        return {
            "action": "book_appointment",
            "params": {
                "student_type": params.get("student_type"),
                "annual_income": params.get("income"),
                "has_complex_taxes": params.get("has_complex_taxes"),
                "has_sin": params.get("has_sin"),
                "has_t4": params.get("has_t4"),
                "has_t2202": params.get("has_t2202"),
            },
            "should_ask_clarification": False,
            "message": None
        }

    elif intent == "out_of_scope":
        return {
            "action": "out_of_scope",
            "params": {},
            "should_ask_clarification": False,
            "message": "I'm sorry, I can only help with Canadian tax questions for UofT students. I'm not able to help with that request. If you have questions about filing your taxes, benefits, or booking a free tax clinic, I'm happy to help!"
        }

    else:  # general_question
        return {
            "action": "general_question",
            "params": {"query": None},
            "should_ask_clarification": False,
            "message": None
        }


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_messages = [
        "I earned $28,000 as a TA in Ontario, how much tax do I owe?",
        "Am I eligible for the GST/HST credit as an international student?",
        "Can you remind me about the tax filing deadline?",
        "I want to book a free tax clinic appointment at UTSU",
        "How do I avoid paying taxes?",
        "What is the weather like today?",
        "I need help with my taxes",
        "I'm a grad student earning 25k, am I eligible for any benefits?",
    ]

    for msg in test_messages:
        print(f"\nMessage: {msg}")
        result = classify_intent(msg)
        print(f"Intent: {result['intent']} | Confidence: {result['confidence']}")
        print(f"Reason: {result['reason']}")
        params = {k: v for k, v in result['parameters'].items() if v is not None}
        if params:
            print(f"Extracted params: {params}")