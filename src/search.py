from dataclasses import dataclass
from typing import List, Dict, Any
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sentence_transformers import CrossEncoder
from .config import CHROMA_DIR, COLLECTION_NAME, EMBED_MODEL, RERANK_MODEL, TOP_K, TOP_M
from .utils import QueryCache

@dataclass
class Hit:
    doc_id: str
    text: str
    score: float
    meta: Dict[str, Any]

class Searcher:
    def __init__(self, cache_db):
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.ef = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
        self.col = self.client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=self.ef)
        self.reranker = CrossEncoder(RERANK_MODEL)
        self.cache = QueryCache(cache_db)

    def search(self, query: str, top_k: int = TOP_K, top_m: int = TOP_M) -> List[Hit]:
        # cache check
        cached = self.cache.get(stage="search", query=query, top_k=top_k, top_m=top_m)
        if cached:
            return [Hit(**h) for h in cached]

        res = self.col.query(query_texts=[query], n_results=top_k)
        docs = res.get("documents", [[]])[0]
        ids = res.get("ids", [[]])[0]
        metas = res.get("metadatas", [[]])[0]

        # Re-rank
        pairs = [(query, d) for d in docs]
        scores = self.reranker.predict(pairs)
        ranked = sorted(zip(ids, docs, metas, scores), key=lambda x: float(x[3]), reverse=True)[:top_m]

        hits = [Hit(doc_id=i, text=t, meta=m, score=float(s)) for i, t, m, s in ranked]
        self.cache.set([h.__dict__ for h in hits], stage="search", query=query, top_k=top_k, top_m=top_m)
        return hits
