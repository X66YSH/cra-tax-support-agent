# CRA Tax Support Agent for UofT Students

A conversational AI agent that helps University of Toronto students navigate Canadian tax filing, credits, and benefits using RAG-powered knowledge retrieval and multi-turn agentic workflows.

## Team

- Zongheng Li
- Krishitha Muddasani
- Yijun Gu
- Zhuoyi Qu
- Zilin Cai

## Overview

International students at UofT pay among Canada's highest tuition yet often miss credits worth thousands — tuition carry-forward, GST/HST credit, Ontario Trillium Benefit. This agent provides 24/7 pre-screening and document prep to help students prepare for tax season.

## Features

- **Knowledge Base**: 69 sources (61 HTML + 8 PDF) from CRA and UofT → 1,493 chunks in ChromaDB
- **Tax Estimate** — Income + province → federal & provincial bracket estimate
- **Benefit Eligibility Check** — GST/HST Credit, OTB, CCB, tuition carry-forward (multi-turn)
- **Filing Reminder** — Deadline alerts and filing checklist
- **Book UTSU Tax Clinic** — CVITP eligibility screening + document prep + booking link (multi-turn)
- **Guardrails** — Disclaimer on every response, rejects out-of-scope queries, prompt injection handling

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | qwen3-30b-a3b-fp8 (course endpoint) |
| Framework | LangChain, LangGraph |
| Vector DB | ChromaDB (cosine similarity, HNSW) |
| Embeddings | all-MiniLM-L6-v2 (sentence-transformers) |
| State | SQLite |
| Backend | FastAPI + Uvicorn |
| Frontend | React 19 + Vite + TailwindCSS |
| Scraping | BeautifulSoup + PyPDF2 |

## Architecture

```
User → React Frontend → FastAPI Backend → Intent Classifier (LLM)
                                              ↓
                              ┌────────────────┼────────────────┐
                              ↓                ↓                ↓
                        Action Handler    RAG Pipeline     Guardrails
                        (LangGraph)      (ChromaDB)       (Safety Filter)
                              ↓                ↓                ↓
                        Parameter         Semantic           Block/Redirect
                        Collection        Search + QE
                              ↓                ↓
                              └────────┬───────┘
                                       ↓
                                 LLM Response
                                       ↓
                              Session State (SQLite)
```

## Setup

```bash
# Clone the repository
git clone https://github.com/X66YSH/cra-tax-support-agent.git
cd cra-tax-support-agent

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API key

# Build the RAG knowledge base (first time only)
python -m src.rag.run_rag --index

# Install frontend dependencies
cd frontend && npm install && cd ..
```

## Running

```bash
# Option 1: Development (two terminals)
# Terminal 1 — Backend
source .venv/bin/activate
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend dev server
cd frontend && npm run dev

# Open http://localhost:5173

# Option 2: Production (single server)
cd frontend && npm run build && cd ..
source .venv/bin/activate
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000

# Open http://localhost:8000

# Option 3: Share via ngrok
ngrok http 8000
# Share the https://xxx.ngrok-free.dev link
```

## Evaluation

33/35 test cases passed (**94.3% accuracy**). See `tests/eval_summary.md` for details.

| Category | Tests | Passed | Accuracy |
|---|---|---|---|
| Intent Classification | 10 | 10 | 100% |
| Action Execution | 8 | 8 | 100% |
| Guardrails | 6 | 6 | 100% |
| Robustness / Edge Cases | 6 | 4 | 66.7% |
| Hallucination Checks | 5 | 5 | 100% |

## Project Structure

```
cra-tax-support-agent/
├── backend/               # FastAPI backend
│   ├── app.py             # API endpoints + static file serving
│   ├── orchestrator.py    # Intent → action → RAG → LLM pipeline
│   └── database.py        # SQLite session/message persistence
├── frontend/              # React + Vite + TailwindCSS
│   ├── src/
│   │   ├── App.jsx        # Main app with session management
│   │   ├── api.js         # API client
│   │   └── components/    # Sidebar, ChatWindow, MessageBubble, etc.
│   └── public/logo.svg    # App logo
├── src/
│   ├── ingestion/         # Scraping (HTML + PDF) and chunking
│   ├── rag/               # Embedding, ChromaDB indexing, retrieval
│   ├── agent/             # Intent classification, action routing
│   └── guardrails/        # Safety filters and disclaimers
├── tests/                 # 35 evaluation test cases
│   ├── test_actions.py
│   ├── eval_results.txt
│   └── eval_summary.md
├── docs/                  # Proposal and documentation
├── requirements.txt
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
