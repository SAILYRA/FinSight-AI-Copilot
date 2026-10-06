"""
FinSight AI - ChromaDB Vector Indexer & Embedding Pipeline (Day 2)
Generates embeddings using BAAI/bge-small-en-v1.5 and persists them in ChromaDB.
"""

import os
from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from src.config import settings
from src.rag.loader import load_and_chunk_pdfs


def get_embedding_model(model_name: str = None) -> HuggingFaceEmbeddings:
    """Initializes and returns the HuggingFace embedding model."""
    target_model = model_name or settings.EMBEDDING_MODEL_NAME
    print(f"[*] Initializing HuggingFace Embeddings: {target_model}...")
    embeddings = HuggingFaceEmbeddings(
        model_name=target_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}  # Standard cosine similarity normalization
    )
    return embeddings


def build_and_persist_vectorstore(
    documents: List[Document] = None,
    persist_dir: str = None,
    model_name: str = None
) -> Chroma:
    """
    Builds a persistent ChromaDB vector store from chunked PDF documents.
    """
    p_dir = persist_dir or settings.CHROMA_PERSIST_DIR
    docs = documents if documents is not None else load_and_chunk_pdfs()
    embeddings = get_embedding_model(model_name)

    os.makedirs(p_dir, exist_ok=True)
    print(f"[*] Embedding {len(docs)} document chunks into ChromaDB at: {p_dir}...")
    
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=p_dir,
        collection_name="finsight_company_docs"
    )
    print(f"[SUCCESS] Vector store built and saved to {p_dir}")
    return vectorstore


def load_existing_vectorstore(
    persist_dir: str = None,
    model_name: str = None
) -> Chroma:
    """Loads an existing persisted ChromaDB vector store."""
    p_dir = persist_dir or settings.CHROMA_PERSIST_DIR
    if not os.path.exists(p_dir) or not os.listdir(p_dir):
        print(f"[*] No existing index found at {p_dir}. Building new index...")
        return build_and_persist_vectorstore(persist_dir=p_dir, model_name=model_name)

    embeddings = get_embedding_model(model_name)
    vectorstore = Chroma(
        persist_directory=p_dir,
        embedding_function=embeddings,
        collection_name="finsight_company_docs"
    )
    return vectorstore


if __name__ == "__main__":
    build_and_persist_vectorstore()
