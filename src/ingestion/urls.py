"""
All target URLs organized by feature and source type.
Update URLs here if CRA restructures their site.

Current count: ~65 HTML pages + 10 PDFs = ~75 total sources
"""

# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------

HTML_URLS = {

    # --- Feature 1: Tax Estimate -------------------------------------------
    # Income + province → federal & provincial bracket estimate
    "tax_estimate": [
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/frequently-asked-questions-individuals/canadian-income-tax-rates-individuals-current-previous-years.html",
            "title": "Canadian federal income tax rates – current and previous years",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/tax-packages-years/general-income-tax-benefit-package/ontario.html",
            "title": "Ontario provincial tax package – rates and credits",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-10100-employment-income.html",
            "title": "Line 10100 – Employment income (T4 income for TAs/RAs)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-10400-other-employment-income.html",
            "title": "Line 10400 – Other employment income",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-13000-other-income/line-13010-scholarships-fellowships-bursaries-artists-project-grants-awards.html",
            "title": "Line 13010 – Scholarships, fellowships, bursaries (T4A box 105)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/tax-packages-years/general-income-tax-benefit-package/5000-g.html",
            "title": "Line 15000 – Federal income tax guide (total income)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-23600-net-income.html",
            "title": "Line 23600 – Net income calculation",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-30000-basic-personal-amount.html",
            "title": "Line 30000 – Basic personal amount (federal)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-31260-canada-employment-amount.html",
            "title": "Line 31260 – Canada employment amount",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-32300-your-tuition-education-textbook-amounts.html",
            "title": "Line 32300 – Tuition, education, and textbook amounts",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-21900-moving-expenses.html",
            "title": "Line 21900 – Moving expenses (students relocating for school)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-20800-rrsp-deduction.html",
            "title": "Line 20800 – RRSP deduction",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/rrsps-related-plans/contributing-a-rrsp-prpp.html",
            "title": "RRSP – contribution rules and limits",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-22900-other-employment-expenses/work-space-home-expenses.html",
            "title": "Work-space-in-the-home expenses (home office for TAs/RAs)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/cpp-contributions-your-return.html",
            "title": "CPP contributions – student and non-resident exemptions",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/completing-filing-information-returns/t4-information-employers/t4-slip/understanding-your-t4-slip.html",
            "title": "Understanding your T4 slip – boxes explained",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-13000-other-income/line-13010-taxable-scholarships-fellowships-bursaries-net-research-grants.html",
            "title": "T4A slip – box 105 scholarships and bursaries",
        },
    ],

    # --- Feature 2: Benefit Eligibility ------------------------------------
    # GST/HST Credit, OTB, CCB, tuition carry-forward (multi-turn)
    "benefit_eligibility": [
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/child-family-benefits/gsthstc-apply.html",
            "title": "GST/HST Credit – how to apply and eligibility",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/child-family-benefits/gst-hst-credit/how-much.html",
            "title": "GST/HST Credit – overview and payment amounts",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/child-family-benefits/provincial-territorial-programs/ontario-trillium-benefit-questions-answers.html",
            "title": "Ontario Trillium Benefit (OTB) – eligibility and amounts",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/tax-packages-years/general-income-tax-benefit-package/ontario/5006-tg.html",
            "title": "ON-BEN – Application for OTB and OSHPTG",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-child-benefit-overview.html",
            "title": "Canada Child Benefit (CCB) – overview",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-workers-benefit.html",
            "title": "Canada Workers Benefit (CWB) – low-income students",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/child-family-benefits/canada-carbon-rebate.html",
            "title": "Canada Carbon Rebate (Climate Action Incentive)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/forms/t2202.html",
            "title": "T2202 – Tuition and Enrolment Certificate",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/lines-33099-33199-eligible-medical-expenses-you-claim-on-your-tax-return.html",
            "title": "Lines 33099/33199 – Medical expenses tax credit",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/segments/tax-credits-deductions-persons-disabilities/disability-tax-credit.html",
            "title": "Disability Tax Credit (DTC) – eligibility and application",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-21400-child-care-expenses.html",
            "title": "Line 21400 – Child care expenses",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-31900-interest-paid-on-your-student-loans.html",
            "title": "Line 31900 – Interest paid on student loans",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account/what.html",
            "title": "Tax-Free Savings Account (TFSA) – overview",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/first-home-savings-account.html",
            "title": "First Home Savings Account (FHSA) – for future homeowners",
        },
    ],

    # --- Feature 3: Filing Reminder ----------------------------------------
    # Apr 30 deadline, first-time filers, document checklist
    "filing_reminder": [
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/important-dates-individuals.html",
            "title": "Tax filing deadline – April 30",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/news/newsroom/tax-tips/tax-tips-2025/new-canada-filing-tax-return-first-time.html",
            "title": "Filing your first income tax return in Canada",
        },
        {
            "url": "https://www.canada.ca/en/services/taxes/income-tax/personal-income-tax/how-file/tax-software/find-software.html",
            "title": "NETFILE – certified software for online tax filing",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/interest-penalties/late-filing-penalty.html",
            "title": "Late-filing penalty and interest on balance owing",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/e-services/digital-services-individuals/account-individuals.html",
            "title": "My CRA Account – register and manage your tax account",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/e-services/about-auto-fill-return.html",
            "title": "Auto-fill my return – import slips automatically",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/about-canada-revenue-agency-cra/direct-deposit.html",
            "title": "Direct deposit – set up for refunds and benefits",
        },
        {
            "url": "https://www.canada.ca/en/services/taxes/income-tax/personal-income-tax/after-you-file/noa-nor.html",
            "title": "Notice of Assessment – how to read yours",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/tax-packages-years/general-income-tax-benefit-package.html",
            "title": "T1 General – income tax and benefit return package",
        },
        {
            "url": "https://www.canada.ca/en/services/taxes/income-tax/personal-income-tax/after-you-file/change-return.html",
            "title": "How to change (amend) your tax return after filing",
        },
        {
            "url": "https://www.canada.ca/en/employment-social-development/services/sin.html",
            "title": "Social Insurance Number (SIN) – how to apply",
        },
    ],

    # --- Feature 4: Book UTSU Tax Clinic Appointment -----------------------
    # CVITP eligibility screening + document checklist + Calendly
    "book_appointment": [
        {
            "url": "https://www.utsu.ca/",
            "title": "UTSU – main page (tax clinic info and services)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/community-volunteer-income-tax-program.html",
            "title": "CVITP – Community Volunteer Income Tax Program overview",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/community-volunteer-income-tax-program/need-a-hand-complete-your-tax-return.html",
            "title": "CVITP – Who we help, documents needed, eligibility and scope",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/community-volunteer-income-tax-program/lend-a-hand-individuals.html",
            "title": "CVITP – Volunteer at a free tax clinic",
        },
        {
            "url": "https://internationalexperience.utoronto.ca/international-student-services/",
            "title": "UofT Centre for International Experience – Student services",
        },
    ],

    # --- International Students (cross-feature) ----------------------------
    # Residency, foreign income, non-resident withholding, tax treaties
    "international_students": [
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/international-students-studying-canada.html",
            "title": "International students in Canada – tax overview",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/information-been-moved/determining-your-residency-status.html",
            "title": "Determining your residency status (183-day rule, ties)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/newcomers-canada-immigrants.html",
            "title": "Newcomers to Canada – filing your first tax return",
        },
        {
            "url": "https://www.canada.ca/en/department-finance/programs/tax-policy/tax-treaties.html",
            "title": "Canada tax treaties – overview (China, Korea, India, US, etc.)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/individuals-leaving-entering-canada-non-residents/non-residents-canada.html",
            "title": "Non-residents of Canada – income tax obligations",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/international-non-residents/payments-non-residents/nr4-part-xiii-tax/part-xiii-withholding-tax/rates-part-xiii-tax.html",
            "title": "Part XIII tax – withholding on Canadian-source income (non-residents)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/forms/nr73.html",
            "title": "Form NR73 – Determination of residency status (leaving Canada)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/forms/nr74.html",
            "title": "Form NR74 – Determination of residency status (entering Canada)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/forms/nr4.html",
            "title": "NR4 slip – Statement of amounts paid to non-residents",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-40500-federal-foreign-tax-credit.html",
            "title": "Line 40500 – Federal foreign tax credit",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-10400-other-employment-income.html",
            "title": "Foreign employment income – how to report",
        },
        {
            "url": "https://www.ontario.ca/page/osap-ontario-student-assistance-program",
            "title": "OSAP – student assistance overview and repayment info",
        },
    ],

    # --- Slips & Forms reference -------------------------------------------
    # Common tax slips UofT students receive
    "slips_and_forms": [
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/tax-slips/understand-your-tax-slips/t4-slips/t4a-slip.html",
            "title": "T4A slip – guide for recipients (scholarships, bursaries, TA pay)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/forms/t4e.html",
            "title": "T4E slip – Employment Insurance and other benefits",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/forms/t2125.html",
            "title": "T2125 – Statement of business or professional activities (self-employed students)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/forms/t776.html",
            "title": "T776 – Statement of real estate rentals (students renting out rooms)",
        },
        {
            "url": "https://www.canada.ca/en/revenue-agency/services/forms-publications/forms/t2200.html",
            "title": "T2200 – Declaration of conditions of employment (home office)",
        },
    ],

}

# ---------------------------------------------------------------------------
# PDF downloads
# ---------------------------------------------------------------------------

PDF_URLS = [
    {
        "url": "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/p105/p105-24e.pdf",
        "filename": "p105_students_income_tax.pdf",
        "title": "P105 – Students and Income Tax",
        "features": ["tax_estimate", "benefit_eligibility", "international_students"],
    },
    {
        "url": "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4058/t4058-24e.pdf",
        "filename": "t4058_non_residents_income_tax.pdf",
        "title": "T4058 – Non-Residents and Income Tax",
        "features": ["international_students", "tax_estimate"],
    },
    {
        "url": "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4055/t4055-23e.pdf",
        "filename": "t4055_newcomers_to_canada.pdf",
        "title": "T4055 – Newcomers to Canada",
        "features": ["international_students", "filing_reminder"],
    },
    {
        "url": "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/rc4210/rc4210-24e.pdf",
        "filename": "rc4210_gsthst_credit.pdf",
        "title": "RC4210 – GST/HST Credit guide",
        "features": ["benefit_eligibility"],
    },
    {
        "url": "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4044/t4044-24e.pdf",
        "filename": "t4044_employment_expenses.pdf",
        "title": "T4044 – Employment Expenses",
        "features": ["tax_estimate"],
    },
    {
        "url": "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/rc4064/rc4064-24e.pdf",
        "filename": "rc4064_disability_information.pdf",
        "title": "RC4064 – Disability-Related Information",
        "features": ["benefit_eligibility"],
    },
    {
        "url": "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/p148/p148-22e.pdf",
        "filename": "p148_newcomers_guide_benefits.pdf",
        "title": "P148 – Newcomers – Getting Benefits and Credits",
        "features": ["benefit_eligibility", "international_students"],
    },
    {
        "url": "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4114/t4114-24e.pdf",
        "filename": "t4114_canada_child_benefit.pdf",
        "title": "T4114 – Canada Child Benefit",
        "features": ["benefit_eligibility"],
    },
]


def get_all_html_urls() -> list[dict]:
    """Return flat list of all HTML URL entries with their feature tag."""
    result = []
    for feature, entries in HTML_URLS.items():
        for entry in entries:
            result.append({**entry, "feature": feature})
    return result


def count_sources() -> dict:
    """Return a summary count of all sources."""
    html_count = sum(len(v) for v in HTML_URLS.values())
    return {
        "html_pages": html_count,
        "pdfs": len(PDF_URLS),
        "total": html_count + len(PDF_URLS),
        "by_feature": {k: len(v) for k, v in HTML_URLS.items()},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(count_sources(), indent=2))
