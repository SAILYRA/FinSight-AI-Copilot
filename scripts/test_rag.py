"""
FinSight AI - Interactive RAG Verification Script (Day 2 Hands-on)
Runs queries across different enterprise documents and displays retrieved chunks with exact citations.
"""

import sys
import os

# Set utf-8 encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rag.retriever import HybridDocumentRetriever


def run_rag_tests():
    print("=" * 70)
    print("🚀 FIN-SIGHT AI — HYBRID RAG RETRIEVAL VERIFICATION (DAY 2)")
    print("=" * 70)

    retriever = HybridDocumentRetriever(top_k=3, dense_weight=0.6, sparse_weight=0.4)

    test_queries = [
        {
            "category": "📊 Financial Performance (Annual Report)",
            "query": "What was Acme Corp's total revenue and operating income in FY 2025?"
        },
        {
            "category": "🏢 HR & Employee Policy (Handbook)",
            "query": "What is the policy on carrying over unused annual leave days into the next year?"
        },
        {
            "category": "⚙️ Technical Specifications & SLA (Product Manual)",
            "query": "What is the SLA uptime guarantee and target response time for Mission-Critical tier?"
        },
        {
            "category": "🔒 Security & Compliance (SOC2 / ISO Standards)",
            "query": "What is the data retention and erasure timeline after contract termination?"
        }
    ]

    for idx, item in enumerate(test_queries, start=1):
        print("\n" + "#" * 70)
        print(f"TEST {idx}: {item['category']}")
        print(f"QUERY: \"{item['query']}\"")
        print("#" * 70)

        result = retriever.retrieve_with_citations(item["query"])

        print("\n--- 📑 RETRIEVED CITATIONS ---")
        for c in result["citations"]:
            print(f" • [Chunk {c['chunk_index']}] File: {c['source_file']} | Page: {c['page_number']}")

        print("\n--- 📖 FORMATTED PASSAGES PREVIEW ---")
        for passage in result["context"].split("\n\n"):
            first_few_lines = "\n".join(passage.split("\n")[:4])
            print(f"{first_few_lines}\n...")

    print("\n" + "=" * 70)
    print("[SUCCESS] All Hybrid RAG queries executed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    run_rag_tests()
