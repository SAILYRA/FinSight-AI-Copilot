"""
FinSight AI - Production FastAPI Backend (Day 6-7)
Exposes REST endpoints for multi-turn chat, RAG inspection, SQL schema, and health checks.
"""

import os
import time
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.agent.graph import invoke_agent
from src.sql.database import get_database

app = FastAPI(
    title="FinSight AI API",
    description="Enterprise Financial Intelligence & Operations Agent API combining Hybrid Document RAG and Safe Text-to-SQL.",
    version=settings.VERSION
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request & Response Models ---

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or instruction", min_length=1)
    thread_id: Optional[str] = Field(default=None, description="Conversational thread ID for session persistence")


class ChatResponse(BaseModel):
    thread_id: str
    input_message: str
    response: str
    tools_called: List[str]
    citations: List[str]
    sql_queries: List[str]
    latency_seconds: float


class HealthResponse(BaseModel):
    status: str
    version: str
    model: str
    database_connected: bool
    persisted_vectorstore: bool
    uptime_seconds: float


START_TIME = time.time()


# --- Endpoints ---

@app.get("/", tags=["General"])
def root():
    return {
        "message": "FinSight AI Agent API is running.",
        "docs_url": "/docs",
        "health_url": "/health",
        "version": settings.VERSION
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    db_ok = os.path.exists(settings.DATABASE_PATH)
    vector_ok = os.path.exists(settings.CHROMA_PERSIST_DIR)
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        model=settings.GROQ_MODEL,
        database_connected=db_ok,
        persisted_vectorstore=vector_ok,
        uptime_seconds=round(time.time() - START_TIME, 2)
    )


@app.post("/chat", response_model=ChatResponse, tags=["Agent"])
def chat_endpoint(request: ChatRequest):
    """
    Sends a message to the FinSight AI LangGraph Agent and returns synthesized response,
    document citations, and executed SQL queries.
    """
    session_id = request.thread_id or f"session_{uuid.uuid4().hex[:8]}"
    start_t = time.perf_counter()

    try:
        agent_output = invoke_agent(request.message, thread_id=session_id)
        elapsed = round(time.perf_counter() - start_t, 2)

        return ChatResponse(
            thread_id=session_id,
            input_message=request.message,
            response=agent_output["response"],
            tools_called=agent_output["tools_called"],
            citations=agent_output["citations"],
            sql_queries=agent_output["sql_queries"],
            latency_seconds=elapsed
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent Execution Error: {str(e)}"
        )


@app.get("/schema", tags=["Inspection"])
def get_database_schema():
    """Returns database table definitions and sample data."""
    try:
        db = get_database()
        return {"schema_context": db.get_schema_context()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", tags=["Inspection"])
def list_ingested_documents():
    """Lists all available enterprise PDF documents."""
    if not os.path.exists(settings.PDF_DIR):
        return {"documents": []}
    files = [f for f in os.listdir(settings.PDF_DIR) if f.endswith(".pdf")]
    return {
        "pdf_directory": settings.PDF_DIR,
        "total_documents": len(files),
        "documents": files
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
