# FinSight AI — Project Roadmap & Implementation Plan

A production-grade, portfolio-ready conversational AI agent combining Hybrid Document RAG and Safe Text-to-SQL with LangGraph, Groq, FastAPI, and Streamlit.

---

## 📅 Roadmap Overview

### Day 1: Prepare Dataset & Environment (~2 hours)
- **Repository & Setup**: Clean GitHub repo with Python virtual environment (`venv`).
- **Data Folder (`/data`)**:
  - **Unstructured Data**: 3–4 sample PDFs (e.g., annual company report, HR policy document, product manual).
  - **Structured Data**: SQLite database (`sales_data.db`) created from sample sales/orders CSVs with 4–5 relational tables (`customers`, `orders`, `products`, `regions`).

---

### Day 2: Document RAG Pipeline with Citations (Core RAG)
- **Document Ingestion**:
  - Load PDFs with LangChain's `PyMuPDFLoader`.
  - Chunk documents using `RecursiveCharacterTextSplitter` (800 tokens chunk size, 150 token overlap).
  - Preserve critical metadata (`page_number`, `source_file`) for citations.
- **Embeddings & Vector Store**:
  - Embedding model: `HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")`.
  - Vector database: `ChromaDB`.
- **Hybrid Search (Dense + Keyword)**:
  - Combine Chroma vector retriever with `BM25Retriever` using `EnsembleRetriever`.
  - *Portfolio / Interview Impact*: Demonstrates production hybrid retrieval separating you from basic vector-only RAG implementations.

---

### Day 3: Safe Text-to-SQL Tool (Structured Data)
- **Read-Only SQLite Connection**:
  - Python tool decorated with LangChain's `@tool` connecting to `sales_data.db` strictly in read-only mode (`URI` with `?mode=ro` / SQLite readonly PRAGMA) preventing data modifications (DROP, DELETE, UPDATE, INSERT).
- **Prompt Engineering & Schema Context**:
  - Feed database schema (`CREATE TABLE` definitions + 3 representative sample rows per table).
- **Execution & Output**:
  - Instruct LLM to output valid SQLite queries.
  - Execute safely and return both the raw SQL query and the resulting tabular dataset.

---

### Day 4: Agentic Routing with LangGraph
- **Graph Architecture**:
  - Build an agent using LangGraph (`create_react_agent` or 3-node `StateGraph`).
  - LLM backend: Groq (`llama-3.3-70b-versatile`).
- **Tool Binding**:
  - `search_company_docs` (Hybrid RAG pipeline).
  - `query_sales_database` (Safe Text-to-SQL).
- **State & Memory**:
  - Integrate `MemorySaver` checkpointer for multi-turn conversational persistence.

---

### Day 5: Quantitative Evaluation with RAGAS (The Recruiter Hook)
- **Benchmark Test Set**: 15 curated question-and-answer pairs covering single-hop, multi-hop, and hybrid queries.
- **Metrics Tracked**:
  - **Faithfulness**: Ensure no hallucination (Target: > 85%).
  - **Context Precision**: Verify accuracy of retrieved chunks.
  - **Average Latency**: Benchmark end-to-end response times (Target: ~1.4s with Groq).

---

### Day 6–7: API, Streamlit UI & Live Deployment (Ship to Portfolio)
- **FastAPI Backend**:
  - Expose `/chat` endpoint handling queries, thread session IDs, and tool inspection data.
- **Streamlit Frontend**:
  - Interactive chat interface.
  - Expandable UI sections:
    - *"Sources Cited (Page #)"*
    - *"Generated SQL Query"*
- **Containerization & Hosting**:
  - Add production `Dockerfile`.
  - Deploy to Streamlit Community Cloud or Hugging Face Spaces.
  - Highlight live URL and GitHub repository link at the top of resume and portfolio.
