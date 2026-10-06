"""
FinSight AI - LangChain RAG Tool (Day 4)
Exposes search_company_docs as a LangChain @tool for the LangGraph agent.
"""

from langchain_core.tools import tool
from src.rag.retriever import get_hybrid_retriever


@tool
def search_company_docs_tool(query: str) -> str:
    """
    Searches unstructured company documents (Annual Reports, HR Policy Handbooks,
    Technical Product Manuals, Cybersecurity & Compliance Standards) using Hybrid Retrieval
    (Dense Chroma Vector Search + Sparse BM25 Keyword Search).

    Use this tool when answering questions about:
    - Executive summaries, business outlook, ESG goals, and FY financial overview from reports
    - HR policies: PTO, vacation leave, sick days, hybrid work schedules, expense reimbursements
    - Technical specs: System architecture, SLA guarantees, API rate limits, error codes
    - Compliance: SOC2 Type II, ISO 27001, encryption standards, incident response timelines

    Returns retrieved document excerpts with source filename and page citations.
    """
    retriever = get_hybrid_retriever()
    result = retriever.retrieve_with_citations(query)
    return result["context"]
