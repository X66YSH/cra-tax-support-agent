"""
Query expander for CRA tax domain.

all-MiniLM-L6-v2 is a general-purpose model that doesn't understand
CRA-specific terms like "T2202", "CVITP", "GST/HST", or student slang
like "TA", "carry forward", "Chinese income".

This module expands user queries by appending relevant CRA terminology
before embedding, so the query vector lands closer to the right chunks.
"""

import re

# ---------------------------------------------------------------------------
# Term expansion map: trigger phrase → extra terms to append
# Ordered from most specific to most general to avoid false matches
# ---------------------------------------------------------------------------

EXPANSION_MAP = [
    # --- Abbreviations & student slang ---
    (r"\bTA\b|\bRA\b|teaching assistant|research assistant",
     "teaching assistant employment income T4 box 14 employment income"),

    (r"\bGST\b|\bHST\b|goods and services tax|harmonized sales tax",
     "GST/HST credit quarterly payment Canada Revenue Agency"),

    (r"\bOTB\b|ontario trillium",
     "Ontario Trillium Benefit energy property tax sales tax credit ON-BEN"),

    (r"\bCCB\b|child benefit",
     "Canada Child Benefit monthly payment eligible families"),

    (r"\bCWB\b|workers benefit",
     "Canada Workers Benefit low income refundable tax credit"),

    (r"\bCVITP\b|tax clinic|volunteer tax|free tax",
     "CVITP Community Volunteer Income Tax Program free tax clinic"),

    (r"\bUTSU\b|student union tax",
     "UTSU tax clinic CVITP University of Toronto Students Union"),

    (r"\bSIN\b|social insurance",
     "Social Insurance Number SIN required for tax filing"),

    (r"\bNETFILE\b|file online|online tax",
     "NETFILE certified software online tax return Canada"),

    (r"\bFHSA\b|first home savings",
     "First Home Savings Account FHSA registered account"),

    (r"\bTFSA\b|tax.free savings",
     "Tax-Free Savings Account TFSA contribution room"),

    (r"\bRRSP\b|registered retirement",
     "RRSP Registered Retirement Savings Plan deduction contribution"),

    # --- Income types ---
    (r"scholarship|bursary|fellowship|award",
     "scholarship bursary fellowship T4A box 105 line 13010 exempt income"),

    (r"tuition|t2202|enrolment certificate",
     "T2202 tuition enrolment certificate Schedule 11 line 32300 carry forward"),

    (r"carry.?forward|unused tuition",
     "carry forward unused federal tuition Schedule 11 line 32300"),

    (r"employment income|salary|wage|paycheck|paycheque",
     "employment income T4 box 14 line 10100"),

    (r"self.employ|freelance|contract work|gig",
     "self-employment income T2125 business professional activities"),

    (r"rental income|rent out|subleas",
     "rental income T776 real estate statement"),

    (r"foreign income|overseas income|income from (china|india|korea|us|uk)",
     "foreign income tax treaty non-resident T4058 line 10400"),

    (r"chinese income|china.*income|income.*china",
     "China foreign income Canada-China tax treaty Article 20 students exempt"),

    (r"korean income|korea.*income|income.*korea",
     "Korea foreign income Canada-Korea tax treaty non-resident"),

    (r"indian income|india.*income|income.*india",
     "India foreign income Canada-India tax treaty non-resident"),

    # --- Tax concepts ---
    (r"residency status|resident|non.resident|183 day",
     "residency status determination 183 days resident non-resident tax purposes"),

    (r"tax treaty|tax convention|double tax",
     "tax treaty convention Canada foreign country non-resident withholding"),

    (r"filing deadline|due date|april 30|when.*file",
     "tax filing deadline April 30 Canada Revenue Agency personal income tax"),

    (r"late.fil|missed.*deadline|overdue.*tax",
     "late filing penalty interest balance owing CRA"),

    (r"first time.*fil|never.*fil|new.*canada.*tax",
     "first time filing newcomer Canada tax return SIN NETFILE"),

    (r"notice of assessment|NOA",
     "notice of assessment CRA result tax return refund balance"),

    (r"tax refund|get money back|overpaid",
     "tax refund direct deposit CRA my account"),

    (r"medical expense|medical receipt|health cost",
     "medical expenses tax credit lines 33099 33199 eligible receipts"),

    (r"moving expense|relocation|moved.*school|school.*moved",
     "moving expenses line 21900 students new work location eligible"),

    (r"home office|work from home|remote work",
     "work-space-in-home expenses T2200 employment conditions"),

    (r"student loan interest|osap interest|loan interest",
     "student loan interest line 31900 OSAP federal provincial"),

    (r"disability|DTC|disabled",
     "disability tax credit DTC T2201 eligibility certificate"),

    # --- Benefits & eligibility ---
    (r"eligib|qualify|do i get|am i eligible|can i claim",
     "eligibility requirements criteria income threshold Canada"),

    (r"international student|study permit|student visa|foreign student",
     "international student Canada tax resident non-resident SIN work permit"),

    (r"osap|student loan|ontario assistance",
     "OSAP Ontario Student Assistance Program repayment income tax"),

    # --- Appointment & document prep ---
    (r"document.*need|what.*bring|prepare.*tax|checklist",
     "documents needed SIN T4 T2202 T4A notice of assessment CVITP"),

    (r"book.*appointment|make.*appointment|schedule.*tax",
     "book appointment UTSU tax clinic CVITP eligibility income limit"),

    # --- Guardrail adjacent queries ---
    (r"avoid.*tax|evade.*tax|not pay.*tax|reduce.*tax",
     "legal tax deductions credits reduce taxable income Canada"),
]


def expand_query(query: str) -> str:
    """
    Expand a user query with relevant CRA terminology.

    Scans the query for known patterns and appends domain-specific terms.
    The original query is preserved; expansions are appended so the
    embedding captures both the user's intent and the technical vocabulary.

    Example:
        "I earned 18k as a TA, how much tax do I owe?"
        → "I earned 18k as a TA, how much tax do I owe?
           teaching assistant employment income T4 box 14 employment income"
    """
    query_lower = query.lower()
    additions = []

    for pattern, expansion in EXPANSION_MAP:
        if re.search(pattern, query_lower):
            additions.append(expansion)

    if not additions:
        return query

    expanded = query + "\n" + " ".join(additions)
    return expanded


if __name__ == "__main__":
    tests = [
        "I earned 18000 as a TA, how much federal tax do I owe?",
        "Am I eligible for the GST/HST credit as an international student?",
        "How do I carry forward my tuition tax credit?",
        "I am a student from China, do I need to pay tax on my Chinese income?",
        "What documents do I need for the UTSU tax clinic?",
        "When is the tax filing deadline?",
    ]
    for q in tests:
        print(f"Original: {q}")
        print(f"Expanded: {expand_query(q)}")
        print()
