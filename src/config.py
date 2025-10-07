from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs"
CHROMA_DIR = ROOT / "chroma_store"

# Models
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Collection
COLLECTION_NAME = "myntra_fashion"

# Search defaults
TOP_K = 20     # initial retrieval
TOP_M = 3      # after re-ranking (top M)
