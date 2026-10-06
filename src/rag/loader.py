"""
FinSight AI - PDF Document Loader & Chunking Module (Day 2)
Loads PDFs using PyMuPDF and chunks them while preserving file and page metadata.
"""

import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import settings


def load_and_chunk_pdfs(
    pdf_dir: str = None,
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[Document]:
    """
    Loads all PDFs in pdf_dir, extracts text per page, preserves page numbers
    and filename in metadata, and splits into token/character chunks.
    """
    target_dir = pdf_dir or settings.PDF_DIR
    c_size = chunk_size or settings.CHUNK_SIZE
    c_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    if not os.path.exists(target_dir):
        raise FileNotFoundError(f"PDF directory not found at: {target_dir}")

    pdf_files = [f for f in os.listdir(target_dir) if f.lower().endswith(".pdf")]
    if not pdf_files:
        raise ValueError(f"No PDF files found inside {target_dir}")

    all_raw_docs: List[Document] = []
    print(f"[*] Loading {len(pdf_files)} PDF(s) from {target_dir}...")

    for filename in sorted(pdf_files):
        file_path = os.path.join(target_dir, filename)
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()

        for doc in docs:
            # Normalize and enrich metadata for accurate citations
            page_num = doc.metadata.get("page", 0) + 1  # Convert 0-indexed to 1-indexed
            doc.metadata["page_number"] = page_num
            doc.metadata["source_file"] = filename
            doc.metadata["file_path"] = file_path

        all_raw_docs.extend(docs)
        print(f"   ✓ Loaded: {filename} ({len(docs)} pages)")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=c_size,
        chunk_overlap=c_overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    chunked_docs = text_splitter.split_documents(all_raw_docs)
    print(f"[+] Total chunks created: {len(chunked_docs)} (Chunk size: {c_size}, Overlap: {c_overlap})")
    
    return chunked_docs


if __name__ == "__main__":
    chunks = load_and_chunk_pdfs()
    if chunks:
        print("\n--- Sample Chunk Metadata & Preview ---")
        print(f"Source: {chunks[0].metadata.get('source_file')}")
        print(f"Page: {chunks[0].metadata.get('page_number')}")
        print(f"Snippet:\n{chunks[0].page_content[:200]}...")
