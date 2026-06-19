# ⚖️ SL-RegulaAI

**An agentic, context-aware compliance assistant for Sri Lankan tax and regulatory law.**

SL-RegulaAI is a Corrective RAG (CRAG) system built on a deterministic LangGraph state machine. It ingests Sri Lankan IRD gazettes and tax regulations, resolves multi-turn conversational context, and strictly grounds every response in verified legal text — refusing to answer rather than hallucinating.

---

## Why this exists

Mid-sized businesses and financial departments in Sri Lanka lose hours tracking shifting VAT thresholds, tax amendments, and labour compliance laws buried in dense gazette PDFs. Manual research is slow and exposes companies to audit risk. SL-RegulaAI turns that research into a conversation — with every answer traceable back to an exact gazette and page number.

---

## Architecture

Unlike a standard linear RAG pipeline, SL-RegulaAI routes every query through a deterministic graph rather than a single black-box LLM call. Each stage can independently retry, reject, or halt execution.

```
                                ┌───────────────────────┐
                                │     User follow-up      │
                                │  "Is their number          │
                                │    mandatory?"               │
                                └───────────┬───────────┘
                                            │
                               ┌────────────▼────────────┐
                               │  Context-Aware Rewriter    │
                               │     (Memory Bridge)          │
                               │  pulls history from Neon     │
                               │  Postgres via thread_id      │
                               └────────────┬────────────┘
                                            │
                        "Is a private company registration
                         number mandatory for VAT filing?"
                                            │
                               ┌────────────▼────────────┐
                               │         Retriever            │
                               │   pgvector similarity search  │
                               └────────────┬────────────┘
                                            │
                        ┌──────────────────►│
                        │          ┌────────▼────────┐
                        │          │ Dual-Clause Legal  │
                        │          │   Grader Node        │
                        │          └────────┬────────┘
                        │                   │
                 rewrite & retry     relevant?  not relevant →
                        │                   │     blocks generation
                        └───────────────────┤     (no hallucination)
                                            │
                               ┌────────────▼────────────┐
                               │          Generator           │
                               │    cited, grounded answer     │
                               └────────────┬────────────┘
                                            │
                               ┌────────────▼────────────┐
                               │  Recursion Circuit Breaker   │
                               │   5 failed loops → halt UI,   │
                               │   trigger human-in-the-loop   │
                               └────────────┬────────────┘
                                            │
                                ┌───────────▼───────────┐
                                │   Response + citations   │
                                │   + telemetry metadata    │
                                └───────────────────────┘
```

---

## Technology stack

| Layer | Technology |
|---|---|
| AI orchestration | LangGraph, LangChain, Groq API (Llama 3.1 8B / 70B) |
| Embeddings & search | HuggingFace `all-MiniLM-L6-v2`, pgvector |
| Database & memory | Neon Serverless PostgreSQL |
| Backend API | FastAPI, Pydantic |
| Frontend | Next.js, React, Tailwind CSS, React Markdown |
| Data processing | PyPDF, `RecursiveCharacterTextSplitter` |

---

## Core engineering features

### Context-aware query rewriting (the memory bridge)
Follow-up questions are intercepted before they ever reach the vector database. A dedicated graph node pulls conversational history from Postgres and rewrites vague references into fully resolved, standalone queries — turning *"Is their number mandatory?"* into *"Is a private company registration number mandatory for VAT filing?"*

### Deterministic CRAG state machine
Rather than a single opaque LLM call, every query passes through an explicit LangGraph workflow. A **Dual-Clause Legal Grader** node evaluates retrieved chunks against the query — if the legal text doesn't contain the answer, the graph blocks generation outright instead of letting the model guess.

### Automated batch ingestion pipeline
`ingest_data.py` scans a directory for government PDFs, chunks them (1000 characters, 200 overlap) with metadata auto-extracted from filenames, computes embeddings locally, and streams the payload to Postgres — fully decoupled from the API layer.

### Telemetry & observability
Every query response includes exact token consumption, millisecond latency, the internal graph execution path (which nodes fired), and raw citation metadata — exposed to the Next.js frontend for user-facing verification.

---

## Engineering challenges solved

**Multi-turn context drift.** Standard RAG breaks on pronoun resolution across conversational turns. The query-rewriting node stabilises entity references upstream, measurably improving retrieval precision on follow-up questions.

**Infinite LLM retry loops.** A failed grading check can trigger endless retries in agentic workflows. A strict `GraphRecursionError` circuit breaker halts execution after 5 failed loops, safely locking the UI and escalating to a human-in-the-loop fallback rather than spinning forever.

**Unpredictable vector metadata.** The vector store occasionally returned inconsistent `GazetteMetadata` shapes, causing silent 500 errors. Polymorphic extraction logic (`isinstance`, `hasattr` checks) now parses metadata defensively regardless of schema drift.

**Stateless-to-stateful routing.** The FastAPI server itself stays fully stateless for horizontal scalability — all conversation memory persists externally to Neon Postgres checkpointers, keyed by unique `thread_id`.

---

## Getting started

```bash
# 1. Clone and install
git clone https://github.com/<your-username>/sl-regulaai.git
cd sl-regulaai
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Add your GROQ_API_KEY and Neon DATABASE_URL

# 3. Ingest gazette PDFs
# Place IRD gazette PDFs in ./data/gazettes/, then:
python scripts/ingest_data.py

# 4. Run the API
python main.py
# Interactive docs → http://localhost:8000/docs
```

---

## Roadmap

- **Evaluation pipeline** — a 50-question "golden dataset" of edge-case compliance queries to systematically track context precision, answer relevance, and semantic similarity.
- **Streaming responses** — upgrading FastAPI endpoints to Server-Sent Events for token-by-token UI streaming.

---

## Where to get gazette PDFs

- [Department of Government Printing](http://www.documents.gov.lk)
- [Inland Revenue Department Sri Lanka](https://www.ird.gov.lk)

---

Built by Bhanuka — 2nd year AI undergraduate, SLIIT, first AI specialisation batch in Sri Lanka.
