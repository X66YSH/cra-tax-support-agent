# CRA Tax Support Assistant for UofT Students

A conversational support agent that helps University of Toronto students navigate Canadian tax filing, credits, and benefits using RAG-powered knowledge retrieval and multi-turn agentic workflows.

## Team

- Zongheng Li
- Krishitha Muddasani
- Yijun Gu
- Zhuoyi Qu
- Zilin Cai

## Overview

International students at UofT pay among Canada's highest tuition yet often miss credits worth thousands — tuition carry-forward, GST/HST credit, Ontario Trillium Benefit. This agent provides 24/7 pre-screening and document prep to help students prepare for tax season.

## Features

- **Knowledge Base**: 100+ sources from CRA (canada.ca) and UofT resources (HTML + PDF)
- **Tax Estimate** — Income + province → federal & provincial bracket estimate
- **Benefit Eligibility Check** — GST/HST Credit, OTB, CCB, tuition carry-forward (multi-turn)
- **Filing Reminder** — Mock reminder for Apr 30 deadline or UTSU booking
- **Book UTSU Tax Clinic Appointment** — CVITP eligibility screening + document prep + Calendly link (multi-turn)
- **Guardrails** — Disclaimer on every response, rejects out-of-scope queries, prompt injection handling

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | qwen3-30b-a3b-fp8 |
| Framework | LangChain, LangGraph |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers |
| State | SQLite |
| Frontend | Streamlit |
| Scraping | BeautifulSoup |
| Deployment | Railway (bonus) |

## Architecture

```
User → Intent Classification → RAG Pipeline (ChromaDB) → Action Handler → LLM Response
                                                              ↓
                                                        Session State (SQLite)
```

## Setup

```bash
# Clone the repository
git clone https://github.com/X66YSH/cra-tax-support-agent.git
cd cra-tax-support-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Project Structure

```
cra-tax-support-agent/
├── docs/                  # Proposal and documentation
├── data/                  # Scraped and processed knowledge base
│   ├── raw/               # Raw HTML/PDF files
│   └── processed/         # Chunked and cleaned documents
├── src/
│   ├── ingestion/         # Scraping and chunking pipeline
│   ├── rag/               # Embedding, indexing, retrieval
│   ├── agent/             # Intent classification, routing, tools
│   ├── guardrails/        # Safety filters and disclaimers
│   └── ui/                # Streamlit frontend
├── tests/                 # Evaluation test cases
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
└── README.md
```

## Branch Strategy

Each team member works on their own branch and submits pull requests to `main`:

| Branch | Owner |
|--------|-------|
| `main` | Protected — merge via PR only |
| `zongheng` | Zongheng Li |
| `krishitha` | Krishitha Muddasani |
| `yijun` | Yijun Gu |
| `zhuoyi` | Zhuoyi Qu |
| `zilin` | Zilin Cai |

## License

This project is for academic purposes — University of Toronto, Winter 2026.
