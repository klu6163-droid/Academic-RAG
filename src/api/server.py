"""
FastAPI server for the RAG literature Q&A API.

Start: python -m src.api.server
Or:    uvicorn src.api.server:app --reload --host 127.0.0.1 --port 8000
"""

import sys
from pathlib import Path

# Load .env file if present
_env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_file.exists():
    with open(_env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in __import__("os").environ:
                    __import__("os").environ[key] = value

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import (
    AskRequest,
    AskResponse,
    HealthResponse,
    RetrieveRequest,
    RetrieveResponse,
    StatsResponse,
)
from src.rag.service import get_service

app = FastAPI(title="Literature RAG API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", rag_ready=True)


@app.get("/api/stats", response_model=StatsResponse)
def stats():
    try:
        svc = get_service()
        return svc.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {type(e).__name__}: {str(e)[:300]}")


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        svc = get_service()
        return svc.answer_question(
            question=req.question,
            top_k=req.top_k,
            mode=req.mode,
            filters=req.filters,
            include_raw_evidence=True,
            answer_style=req.answer_style,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG error: {type(e).__name__}: {str(e)[:300]}")


@app.post("/api/retrieve", response_model=RetrieveResponse)
def retrieve_only(req: RetrieveRequest):
    try:
        svc = get_service()
        rows, warnings = svc.retrieve(
            question=req.question,
            top_k=req.top_k,
            mode=req.mode,
            filters=req.filters,
        )
        config = svc.config
        return RetrieveResponse(
            question=req.question,
            evidence=rows,
            retrieval={
                "top_k": req.top_k,
                "retrieved_count": len(rows),
                "mode": req.mode,
                "hybrid_retrieval": config.hybrid.enabled and svc.bm25.is_ready,
                "query_expansion_used": config.query_expansion.enabled and svc.llm_client.is_available,
            },
            warnings=warnings,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {type(e).__name__}: {str(e)[:300]}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.server:app", host="127.0.0.1", port=8001, reload=True)
