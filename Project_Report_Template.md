# Project Report — Fashion Search RAG (BYOP)

## Objectives

- Build a 3-layer search system (Embedding → Search → Generation) for fashion products.
- Compare chunking and model choices to improve retrieval quality.

## System Design (Overview)

- Data prep parses CSV into normalized text docs with metadata.
- Embedding & Vector Store: Sentence-Transformers with Chroma (local persistence).
- Search: First-pass kNN + Cross-Encoder re-rank.
- Generation: OpenAI (optional) or deterministic fallback.
- Caching: SQLite-based query cache.

## Embedding Layer

- Model: `all-MiniLM-L6-v2` (fast, 384-dim).
- Chunking: Product-level aggregation of fields (title, brand, category, description, etc.).
- Experiments to try:
  - Field-wise mini-chunks (title-only, desc-only) vs. aggregated.
  - Alternative models (e.g., all-mpnet-base-v2).

## Search Layer

- Initial top_k=20 from Chroma.
- Cross-Encoder `ms-marco-MiniLM-L-6-v2` re-ranks to top_m=3.
- SQLite cache stores search outputs for repeated queries.

## Generation Layer

- Prompt injects top contexts.
- Uses OpenAI if key present; falls back to extractive summarizer for offline runs.

## Queries (examples)

1. women summer cotton midi dress under 2000 rupees
2. men running shoes with breathable mesh black color
3. kids winter hoodie warm fleece for boys

## Challenges & Lessons

- Schema variance across datasets.
- Balancing speed vs. quality in embeddings/reranking.
- Deterministic fallbacks ensure demos work without external keys.

## How to Reproduce

See `README.md` for commands. Place Myntra CSV at `data/myntra_fashion_dataset.csv`, run data prep, index, then `app_cli.py` to generate the six screenshots.
