# ⚖️ SL-RegulaAI

### An Agentic RAG-based compliance assistant for Sri Lankan tax and regulatory documents.

SL-RegulaAI is a context-aware AI assistant that helps users query Sri Lankan regulatory documents such as IRD gazettes and tax-related publications.

The system uses a retrieval-grounded AI workflow to find relevant legal information, maintain conversation context, verify retrieved sources, and generate responses with citations instead of relying on unsupported model outputs.

---

## Why this exists

Tax and regulatory information changes frequently. Important updates are often buried inside long government PDF documents, making manual searching slow and inefficient.

SL-RegulaAI explores how AI can simplify this process by turning regulatory research into a conversational experience:

**User asks a compliance question → system retrieves relevant documents → AI generates a source-grounded response.**

The goal is not to replace professional legal advice, but to demonstrate how AI systems can improve access to complex regulatory information.

---

# 🏗️ Architecture

Unlike a simple "retrieve → generate" RAG pipeline, SL-RegulaAI uses a LangGraph workflow to add additional control steps around retrieval and generation.

```
User Query
    |
    ▼
FastAPI Backend
    |
    ▼
Context-Aware Query Rewriter
    |
    ▼
pgvector Retrieval
    |
    ▼
Document Relevance Grader
    |
    ▼
LLM Generation
    |
    ▼
Source Verification
    |
    ▼
Response + Citations
```

The workflow handles:

- conversation context resolution
- retrieval quality checking
- grounded response generation
- failure handling for unsupported queries

---

# 🔄 How the workflow works

## 1. Context-aware query rewriting

Multi-turn conversations create a common RAG problem:

Example:

User:
> "Is their number mandatory?"

A normal RAG system may not understand what "their" refers to.

SL-RegulaAI uses conversation history to rewrite vague follow-up questions into standalone queries before retrieval.

Example:

```
"Is their number mandatory?"

↓

"Is the private company registration number mandatory for VAT filing?"
```

This improves retrieval consistency across conversations.

---

## 2. Retrieval with pgvector

Regulatory documents are:

- extracted from PDFs
- split into meaningful chunks
- converted into embeddings
- stored with metadata

The system retrieves relevant sections using vector similarity search.

Stored information includes:

- document source
- metadata
- page references

---

## 3. Retrieval quality checking

Before generating an answer, retrieved documents are evaluated.

If the retrieved context does not sufficiently match the question, the workflow can attempt another retrieval path instead of immediately generating a response.

---

## 4. Grounded response generation

The LLM generates answers using retrieved regulatory context.

Responses include source references to improve transparency and verification.

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| AI Workflow | LangGraph, LangChain |
| LLM | Groq API (Llama 3.1) |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Vector Database | PostgreSQL + pgvector |
| Database Hosting | Neon Serverless PostgreSQL |
| Backend | FastAPI, Pydantic |
| Frontend | Next.js, React, Tailwind CSS |
| Document Processing | PyPDF, RecursiveCharacterTextSplitter |

---

# 🚀 Core Features

## ✅ Multi-turn conversation support

Maintains conversation state using persistent storage and resolves follow-up questions before retrieval.

---

## ✅ Citation-based responses

Generated answers are linked back to retrieved document sources for easier verification.

---

## ✅ Automated document ingestion

PDF documents can be processed through an ingestion pipeline:

```
PDF
 ↓
Text Extraction
 ↓
Chunking
 ↓
Embedding Generation
 ↓
Vector Storage
```

---

## ✅ Workflow-based AI architecture

Instead of a single LLM call, the system uses a structured graph workflow where each step has a specific responsibility.

---

# 🧩 Engineering Challenges

## Context drift in multi-turn RAG

Problem:
Follow-up questions often depend on previous messages.

Solution:
Implemented a query rewriting step that converts conversational references into complete searchable queries.

---

## Retrieval reliability

Problem:
A language model may generate answers from incomplete context.

Solution:
Added retrieval evaluation steps before final response generation.

---

## Handling failed workflows

Problem:
AI workflows with retries can continue indefinitely.

Solution:
Implemented workflow limits and failure handling to prevent endless execution attempts.

---

## Managing conversation state

Problem:
APIs are easier to scale when they remain stateless.

Solution:
Conversation state is stored externally using PostgreSQL-based persistence.

---

# 📸 Screenshots

_WILL UPDATE SOON._

---

# ⚙️ Getting Started

## Clone repository

```bash
git clone https://github.com/<your-username>/SL-RegulaAI.git

cd SL-RegulaAI
```

---

## Install dependencies

```bash
python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

---

## Environment Setup

Create `.env`

```
GROQ_API_KEY=
DATABASE_URL=
```

---

## Document ingestion

Place regulatory PDFs inside:

```
data/gazettes/
```

Run:

```bash
python scripts/ingest_data.py
```

---

## Start backend

```bash
python main.py
```

API documentation:

```
http://localhost:8000/docs
```

---

# 🛣️ Future Improvements

- Build a structured evaluation dataset for RAG testing
- Add automated retrieval and answer quality metrics
- Improve document classification and routing
- Add streaming responses
- Expand regulatory document coverage

---

# 📚 Sources for documents

Sri Lankan government documents:

- Department of Government Printing  
https://www.documents.gov.lk

- Inland Revenue Department Sri Lanka  
https://www.ird.gov.lk

---

Built by **Bhanuka**  
AI Undergraduate — SLIIT 🇱🇰  
First AI Specialisation Batch in SLIIT
