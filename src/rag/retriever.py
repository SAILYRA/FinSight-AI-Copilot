from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

try:
    from langchain_classic.retrievers import EnsembleRetriever
except ImportError:
    try:
        from langchain.retrievers import EnsembleRetriever
    except ImportError:
        from langchain_community.retrievers import EnsembleRetriever

from src.config import settings
from src.rag.loader import load_and_chunk_pdfs
from src.rag.indexer import load_existing_vectorstore


class HybridDocumentRetriever:
    """
    Production Hybrid Retriever combining Dense (ChromaDB) and Sparse (BM25) search.
    """
    def __init__(
        self,
        top_k: int = None,
        dense_weight: float = None,
        sparse_weight: float = None
    ):
        self.top_k = top_k or settings.TOP_K
        self.dense_weight = dense_weight if dense_weight is not None else settings.DENSE_WEIGHT
        self.sparse_weight = sparse_weight if sparse_weight is not None else settings.SPARSE_WEIGHT
        self.ensemble_retriever = self._build_ensemble()

    def _build_ensemble(self) -> EnsembleRetriever:
        # 1. Load document chunks for BM25
        docs = load_and_chunk_pdfs()
        
        # 2. Build BM25 Sparse Retriever
        print("[*] Initializing BM25 Sparse Keyword Retriever...")
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = self.top_k

        # 3. Build Chroma Dense Vector Retriever
        print("[*] Initializing Chroma Dense Vector Retriever...")
        vectorstore = load_existing_vectorstore()
        chroma_retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.top_k}
        )

        # 4. Combine into Ensemble Retriever (Dense + Sparse)
        print(f"[*] Creating EnsembleRetriever (Dense: {self.dense_weight}, Sparse: {self.sparse_weight})...")
        ensemble = EnsembleRetriever(
            retrievers=[chroma_retriever, bm25_retriever],
            weights=[self.dense_weight, self.sparse_weight]
        )
        return ensemble

    def retrieve(self, query: str) -> List[Document]:
        """Retrieves top matching documents using hybrid search."""
        return self.ensemble_retriever.invoke(query)

    def retrieve_with_citations(self, query: str) -> Dict[str, Any]:
        """
        Retrieves top documents and formats structured citations and text snippets.
        """
        docs = self.retrieve(query)
        citations = []
        formatted_passages = []

        for i, doc in enumerate(docs, start=1):
            source = doc.metadata.get("source_file", "Unknown")
            page = doc.metadata.get("page_number", "N/A")
            content = doc.page_content.strip()

            citation_tag = f"[Source: {source} | Page: {page}]"
            citations.append({
                "source_file": source,
                "page_number": page,
                "chunk_index": i,
                "citation_tag": citation_tag
            })
            formatted_passages.append(f"--- Document Chunk {i} {citation_tag} ---\n{content}")

        context_text = "\n\n".join(formatted_passages)
        return {
            "query": query,
            "context": context_text,
            "citations": citations,
            "raw_documents": docs
        }


# Singleton helper instance
_hybrid_retriever_instance = None

def get_hybrid_retriever() -> HybridDocumentRetriever:
    global _hybrid_retriever_instance
    if _hybrid_retriever_instance is None:
        _hybrid_retriever_instance = HybridDocumentRetriever()
    return _hybrid_retriever_instance


def search_company_docs(query: str) -> str:
    """
    Public RAG tool function for the agent.
    Takes a natural language query and returns retrieved context with citations.
    """
    retriever = get_hybrid_retriever()
    result = retriever.retrieve_with_citations(query)
    return result["context"]


if __name__ == "__main__":
    test_query = "What was Acme Corp's total revenue and YoY growth in FY 2025?"
    print(f"\n🔎 Testing Hybrid Retrieval Query: '{test_query}'\n")
    retriever = HybridDocumentRetriever()
    result = retriever.retrieve_with_citations(test_query)
    
    print("\n--- Retrieved Context with Citations ---")
    print(result["context"])
    print("\n--- Extracted Citations Summary ---")
    for c in result["citations"]:
        print(f" • {c['citation_tag']}")
