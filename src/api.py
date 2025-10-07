from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from pathlib import Path

from .search import Searcher
from .generate import generate_answer
from .config import OUT_DIR

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"

app = FastAPI(title="Fashion Search RAG API")

# CORS for any future external pages (safe to keep for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve /web/* as static files
if WEB_DIR.exists():
    app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

# Home → show the UI if present, else redirect to docs
@app.get("/", response_class=HTMLResponse)
def home():
    if (WEB_DIR / "index.html").exists():
        return (WEB_DIR / "index.html").read_text(encoding="utf-8")
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"status": "ok"}

searcher = Searcher(cache_db=OUT_DIR / "cache.sqlite")

class QueryIn(BaseModel):
    query: str
    top_k: int | None = None
    top_m: int | None = None

class HitOut(BaseModel):
    doc_id: str
    text: str
    score: float
    meta: dict

class QueryOut(BaseModel):
    query: str
    hits: List[HitOut]
    answer: str

@app.post("/search", response_model=List[HitOut])
def search(q: QueryIn):
    hits = searcher.search(q.query, top_k=q.top_k or 20, top_m=q.top_m or 3)
    return [HitOut(doc_id=h.doc_id, text=h.text, score=h.score, meta=h.meta) for h in hits]

@app.post("/query", response_model=QueryOut)
def query(q: QueryIn):
    hits = searcher.search(q.query, top_k=q.top_k or 20, top_m=q.top_m or 3)
    contexts = [h.text for h in hits]
    answer = generate_answer(q.query, contexts)
    return QueryOut(
        query=q.query,
        hits=[HitOut(doc_id=h.doc_id, text=h.text, score=h.score, meta=h.meta) for h in hits],
        answer=answer
    )
