# BYOP Fashion Search RAG (Myntra Dataset)

**Goal:** Build a 3-layer RAG-style search system (Embedding → Search → Generation) over the Myntra product dataset.

- Dataset example: Kaggle Myntra fashion product dataset (CSV). Download locally and place under `data/`.
- Embeddings: Sentence-Transformers (default: `all-MiniLM-L6-v2`).
- Vector DB: ChromaDB (local, file-based).
- Re-ranker: Cross-Encoder (default: `cross-encoder/ms-marco-MiniLM-L-6-v2`).
- Generation: OpenAI (optional) or a deterministic fallback summarizer so the CLI always runs offline.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# 1) Put your Myntra CSV into data/, e.g. data/myntra_fashion_dataset.csv
# 2) Prepare data → build index
python src/data_prep.py --csv data/myntra.csv
python src/index.py

# 3) Run the sample queries end-to-end (will produce 6 PNGs under outputs/)
python src/app_cli.py
```

## Building the Vector Store
To generate the vector database (not included due to size):
```bash
python src/data_prep.py --csv data/myntra_fashion_dataset.csv
python src/index.py
```

## Screenshots produced - 6 screenshots in file named - "outputs"
- 3 images for Search Layer (top 3 hits per query): `outputs/query_{i}_search.png`
- 3 images for Generation Layer (final answers): `outputs/query_{i}_answer.png`

You can adjust the sample queries in `src/app_cli.py`.

## Notes
- To use OpenAI for the generation layer, set `OPENAI_API_KEY` in your environment.
- If not set, the CLI will use a deterministic extractive fallback summarizer.
