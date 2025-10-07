import json, chromadb
from pathlib import Path
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from .config import DATA_DIR, COLLECTION_NAME, EMBED_MODEL, CHROMA_DIR

def build_index():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    col = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)

    docs_path = DATA_DIR / "processed.jsonl"
    if not docs_path.exists():
        raise FileNotFoundError(f"{docs_path} not found. Run data_prep.py first.")

    ids, texts, metadatas = [], [], []
    with docs_path.open("r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            ids.append(obj["id"])
            texts.append(obj["text"])
            metadatas.append(obj["meta"])

            # batch insert to save memory
            if len(ids) >= 1024:
                col.add(ids=ids, documents=texts, metadatas=metadatas)
                ids, texts, metadatas = [], [], []

    if ids:
        col.add(ids=ids, documents=texts, metadatas=metadatas)

    print("Index built / updated.")

if __name__ == "__main__":
    build_index()
