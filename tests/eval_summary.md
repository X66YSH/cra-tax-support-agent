# Evaluation Summary — CRA Tax Support Agent

**Date:** 2026-04-10
**Model:** qwen3-30b-a3b-fp8 (course endpoint)
**Knowledge Base:** 69 sources (61 HTML + 8 PDF) → 1,493 chunks in ChromaDB

---

## Overall Results

| Metric | Result |
|---|---|
| **Total Test Cases** | 35 |
| **Passed** | 33 |
| **Failed** | 2 |
| **Overall Accuracy** | **94.3%** |

## Category Breakdown

| Category | Tests | Passed | Accuracy |
|---|---|---|---|
| Intent Classification (1–10) | 10 | 10 | **100%** |
| Action Execution (11–18) | 8 | 8 | **100%** |
| Guardrails (19–24) | 6 | 6 | **100%** |
| Robustness / Edge Cases (25–30) | 6 | 4 | **66.7%** |
| Hallucination Checks (31–35) | 5 | 5 | **100%** |

## Proposal KPI Comparison

| KPI (from proposal) | Target | Actual | Status |
|---|---|---|---|
| Retrieval Accuracy | ≥ 85% | 100% (8/8 action tests produced relevant RAG results) | ✅ Exceeded |
| Answer Faithfulness | ≥ 90% | 100% (5/5 hallucination checks passed — disclaimers, correct facts) | ✅ Exceeded |
| Guardrail Compliance | ≥ 95% | 100% (6/6 — tax evasion, prompt injection, out-of-scope all blocked) | ✅ Exceeded |
| Tool Routing | ≥ 80% | 100% (10/10 intent classification correct) | ✅ Exceeded |
| Latency (e2e) | < 4s | ~2-5s per query (varies with RAG retrieval) | ⚠️ Borderline |

## Failure Analysis

### Test 28: Empty input
- **Input:** `""` (empty string)
- **Expected:** `clarification_needed: True`
- **Actual:** `clarification_needed: False`
- **Root cause:** LLM classified empty string as a valid query instead of asking for clarification. Edge case — empty input should ideally be caught before reaching the classifier.
- **Impact:** Low — users rarely send empty messages in a real UI (input validation prevents it).

### Test 29: Mixed intent — "I want to know my taxes AND also book an appointment at UTSU"
- **Input:** Two intents in one message
- **Expected:** `tax_estimate` (prioritize first intent)
- **Actual:** `general_question`
- **Root cause:** LLM couldn't pick a single intent when two are present, defaulted to general_question.
- **Impact:** Medium — user would get a RAG-based answer instead of starting the tax estimate flow. Could add multi-intent handling in future.

## Key Findings

1. **Core capabilities are solid:** All 10 intent classification tests, all 8 action execution tests, and all 6 guardrail tests passed with 100% accuracy.
2. **Guardrails are robust:** Tax evasion, prompt injection ("ignore your instructions"), fraud requests, and off-topic questions all correctly rejected.
3. **Hallucination prevention works:** Every LLM response included disclaimers, correct tax figures were within expected ranges, non-residents correctly flagged as ineligible, source citations present.
4. **Edge cases are the weakness:** Empty input and multi-intent queries are the only failures — both are uncommon in real usage and could be mitigated with input preprocessing.
