from pathlib import Path
from rich import print
from .config import OUT_DIR
from .search import Searcher
from .generate import generate_answer
from .utils import render_text_image

# Three self-designed queries tailored for Myntra-like apparel:
QUERIES = [
    "women summer cotton midi dress under 2000 rupees",
    "men running shoes with breathable mesh black color",
    "kids winter hoodie warm fleece for boys"
]

def run():
    searcher = Searcher(cache_db=OUT_DIR / "cache.sqlite")

    for i, q in enumerate(QUERIES, start=1):
        print(f"[bold green]\n=== Query {i}: {q} ===[/bold green]")
        hits = searcher.search(q)

        # --- Save Search Layer screenshot ---
        search_text = f"Query: {q}\n\nTOP-3 SEARCH RESULTS\n"
        for rank, h in enumerate(hits, start=1):
            title = h.meta.get("title","")
            brand = h.meta.get("brand","")
            search_text += f"\n[{rank}] score={h.score:.3f}\nTitle: {title}\nBrand: {brand}\nSnippet: {h.text[:300]}...\n"
        render_text_image(search_text, OUT_DIR / f"query_{i}_search.png")

        # --- Generation Layer ---
        contexts = [h.text for h in hits]
        answer = generate_answer(q, contexts)

        ans_text = f"Query: {q}\n\nFINAL ANSWER\n\n{answer}\n"
        render_text_image(ans_text, OUT_DIR / f"query_{i}_answer.png")

        # Print to console too
        print(search_text)
        print(ans_text)

    print(f"Saved screenshots to: {OUT_DIR.resolve()}")

if __name__ == "__main__":
    run()
