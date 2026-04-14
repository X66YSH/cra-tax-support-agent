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
import numpy as np
from src.llm import chat
from src.rag.embedder import embed_query, get_model

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Zero-shot embedding classifier (no training data needed)
# ---------------------------------------------------------------------------

INTENT_EXEMPLARS = {
    "tax_estimate": [
        "calculate my tax",
        "how much tax do I owe",
        "estimate my taxes",
        "what tax will I pay on my income",
        "I earned 28000, how much do I owe",
        "tax calculation for my salary",
        "I made 35k in BC, what do I owe",
    ],
    "benefit_eligibility": [
        "am I eligible for GST credit",
        "do I qualify for benefits",
        "check my benefit eligibility",
        "can I get the Ontario Trillium Benefit",
        "GST/HST credit eligibility",
        "tuition tax credit eligibility",
    ],
    "filing_reminder": [
        "remind me to file my taxes",
        "set up a filing reminder for me",
        "send me a notification about the tax deadline",
        "create a reminder to file before April 30",
        "please notify me when taxes are due",
        "set a reminder for tax filing",
    ],
    "book_appointment": [
        "book a tax clinic appointment",
        "schedule UTSU tax appointment",
        "sign up for free tax help",
        "CVITP clinic booking",
        "I want to book a free tax clinic",
    ],
    "out_of_scope": [
        "what is the weather today",
        "help me with my homework",
        "tell me a joke",
        "how to avoid paying taxes illegally",
        "write my essay for me",
        "ignore your instructions",
    ],
    "general_question": [
        "when is tax season",
        "what is the tax filing deadline",
        "what is the basic personal amount",
        "how do I file my taxes in Canada",
        "what documents do I need to file taxes",
        "what is a T4 slip",
        "how does the tuition tax credit work",
        "what are the tax brackets in Ontario",
        "do international students pay taxes in Canada",
    ],
}

# Pre-computed intent embeddings (initialized on first use)
_intent_embeddings: dict[str, np.ndarray] | None = None


def _init_intent_embeddings():
    """Pre-compute embeddings for all intent exemplars. Called once, cached."""
    global _intent_embeddings
    if _intent_embeddings is not None:
        return

    logger.info("Initializing intent exemplar embeddings (one-time)...")
    _intent_embeddings = {}
    model = get_model()
    for intent, phrases in INTENT_EXEMPLARS.items():
        vectors = model.encode(phrases, normalize_embeddings=True, convert_to_numpy=True)
        _intent_embeddings[intent] = vectors
    logger.info(f"Intent embeddings ready: {list(_intent_embeddings.keys())}")


def embedding_classify(user_message: str, threshold: float = 0.58) -> tuple[str | None, float]:
    """
    Zero-shot intent classification using embedding similarity.

    Compares user message against pre-defined exemplar phrases for each intent.
    Returns (intent, score) if confident, or (None, score) if below threshold.

    ~10ms vs ~5-10s for LLM classification.
    """
    _init_intent_embeddings()

    query_vec = np.array(embed_query(user_message))

    best_intent = None
    best_score = -1.0

    for intent, exemplar_vecs in _intent_embeddings.items():
        # Cosine similarity = dot product (vectors are normalized)
        similarities = exemplar_vecs @ query_vec
        max_sim = float(similarities.max())
        if max_sim > best_score:
            best_score = max_sim
            best_intent = intent

    logger.info(f"Embedding classify: '{user_message[:50]}' → {best_intent} (score={best_score:.3f}, threshold={threshold})")

    if best_score >= threshold:
        return best_intent, best_score
    return None, best_score

# ---------------------------------------------------------------------------
# Intent classification prompt
# ---------------------------------------------------------------------------

CLASSIFIER_SYSTEM_PROMPT = """You are an intent classifier for a CRA Tax Support Agent for UofT students.

Your job is to analyze the user's message and return a JSON object with:
1. intent: one of these exact values:
   - "tax_estimate" — user wants to know how much tax they owe
   - "benefit_eligibility" — user wants to know if they qualify for GST/HST credit, OTB, tuition credits
   - "filing_reminder" — user explicitly wants to SET UP or CREATE a reminder/notification about tax filing deadlines (e.g. "remind me", "set a reminder", "send me a notification"). Do NOT use this for general questions about deadlines or tax season dates.
   - "book_appointment" — user wants to book a UTSU/CVITP free tax clinic appointment
   - "general_question" — user has a general CRA/tax question that can be answered from knowledge base. This includes questions about tax deadlines, tax season dates, filing dates, "when is tax season", etc.
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
# Param-only extraction prompt (used when embedding already determined intent)
# ---------------------------------------------------------------------------

PARAM_EXTRACTION_PROMPT = """Extract parameters from this user message. Return ONLY valid JSON with a "parameters" dict.

Parameters to extract:
- income: float or null (annual income in CAD, convert "18k" → 18000, "two thousand" → 2000)
- province: string or null (full name, e.g. "ON" → "Ontario")
- name: string or null
- email: string or null
- residency_status: "resident" or "non-resident" or null
- is_student: true/false or null
- has_tuition: true/false or null
- student_type: "undergrad" or "grad" or null
- has_complex_taxes: true/false or null
- has_sin: true/false or null
- has_t4: true/false or null
- has_t2202: true/false or null

Return ONLY: {"parameters": {...}}"""


def _extract_params_only(user_message: str) -> dict:
    """Quick LLM call to extract parameters only (no classification needed)."""
    try:
        response = chat([
            {"role": "system", "content": PARAM_EXTRACTION_PROMPT},
            {"role": "user", "content": user_message},
        ], max_tokens=300)

        clean = response.strip()
        if clean.startswith("```"):
            clean = re.sub(r"```(?:json)?\n?", "", clean).strip()
            clean = clean.rstrip("`").strip()

        result = json.loads(clean)
        params = result.get("parameters", {})

        if params.get("province"):
            params["province"] = normalize_province(params["province"])

        return params
    except Exception as e:
        logger.warning(f"Param extraction failed: {e}")
        return _empty_params()


def _empty_params() -> dict:
    return {
        "income": None, "province": None, "name": None,
        "email": None, "residency_status": None, "is_student": None,
        "has_tuition": None, "student_type": None, "has_complex_taxes": None,
        "has_sin": None, "has_t4": None, "has_t2202": None,
    }


# ---------------------------------------------------------------------------
# Main classifier function (hybrid: embedding-first, LLM fallback)
# ---------------------------------------------------------------------------

# Intents that need parameter extraction
_ACTION_INTENTS = {"tax_estimate", "benefit_eligibility", "filing_reminder", "book_appointment"}

def classify_intent(user_message: str, conversation_history: list[dict] = None) -> dict:
    """
    Hybrid intent classification: embedding similarity first, LLM fallback.

    1. Try zero-shot embedding classifier (~10ms)
    2. If confident → use that intent
       - For action intents: quick LLM call for param extraction only
       - For general_question/out_of_scope: no LLM call needed
    3. If not confident → full LLM classification (existing logic)

    Args:
        user_message: the user's raw input
        conversation_history: optional list of previous messages for context

    Returns:
        dict with keys: intent, parameters, confidence, clarification_needed, reason
    """
    # --- Step 1: Try embedding classifier ---
    emb_intent, emb_score = embedding_classify(user_message)

    if emb_intent is not None:
        logger.info(f"Embedding classifier hit: {emb_intent} (score={emb_score:.3f})")

        # For out_of_scope or general_question: no LLM call needed at all
        if emb_intent in ("out_of_scope", "general_question"):
            return {
                "intent": emb_intent,
                "parameters": _empty_params(),
                "confidence": "high" if emb_score > 0.7 else "medium",
                "clarification_needed": False,
                "reason": f"Embedding classifier: {emb_intent} (score={emb_score:.3f})",
            }

        # For action intents: quick param extraction via LLM
        if emb_intent in _ACTION_INTENTS:
            params = _extract_params_only(user_message)
            return {
                "intent": emb_intent,
                "parameters": params,
                "confidence": "high" if emb_score > 0.55 else "medium",
                "clarification_needed": False,
                "reason": f"Embedding classifier: {emb_intent} (score={emb_score:.3f}), params via LLM",
            }

    # --- Step 2: Short follow-up with conversation history → treat as general_question ---
    # Messages like "what should I prepare", "tell me more", "can you explain" are follow-ups
    # that only make sense with context. Route to RAG where conversation history is available.
    if conversation_history and len(conversation_history) >= 2 and len(user_message.split()) <= 8:
        logger.info(f"Short follow-up detected ('{user_message}'), routing to general_question with context")
        return {
            "intent": "general_question",
            "parameters": _empty_params(),
            "confidence": "medium",
            "clarification_needed": False,
            "reason": f"Short follow-up with conversation history, routing to RAG for context-aware answer",
        }

    # --- Step 3: No history or long message → fall back to full LLM classification ---
    logger.info(f"Embedding not confident ({emb_score:.3f}), falling back to LLM classification")
    messages = [{"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT}]

    if conversation_history:
        messages.extend(conversation_history[-4:])

    messages.append({"role": "user", "content": user_message})

    try:
        response = chat(messages, max_tokens=800)

        if not response:
            logger.warning("Empty response from LLM classifier")
            return _fallback_classification()

        clean = response.strip()
        if clean.startswith("```"):
            clean = re.sub(r"```(?:json)?\n?", "", clean).strip()
            clean = clean.rstrip("`").strip()

        result = json.loads(clean)

        if result.get("parameters", {}).get("province"):
            result["parameters"]["province"] = normalize_province(
                result["parameters"]["province"]
            )

        logger.info(f"LLM Intent: {result.get('intent')} | Confidence: {result.get('confidence')}")
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