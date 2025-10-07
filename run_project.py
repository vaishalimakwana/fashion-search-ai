#!/usr/bin/env python3
"""
One-click runner for the BYOP Fashion Search RAG project.

Usage examples:
  python run_project.py                  # Auto-detect CSV and run all steps
  python run_project.py --csv data/myntra_fashion_dataset.csv
  python run_project.py --rebuild        # Clear cache + rebuild from scratch
  python run_project.py --dry            # Show steps only
"""
import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs"
CHROMA_DIR = ROOT / "chroma_store"

def debug(msg: str):
    print(f"[RUN] {msg}")

def find_csv(default_dir: Path) -> Optional[Path]:
    if not default_dir.exists():
        return None
    for p in default_dir.iterdir():
        if p.suffix.lower() == ".csv":
            return p
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, default="", help="Path to Myntra CSV (defaults to first CSV under data/)")
    ap.add_argument("--rebuild", action="store_true", help="Delete chroma_store and outputs/cache.sqlite before running")
    ap.add_argument("--dry", action="store_true", help="Print steps without executing")
    args = ap.parse_args()

    csv_path = Path(args.csv) if args.csv else find_csv(DATA_DIR)
    if not csv_path:
        print(f"ERROR: No CSV found. Place your dataset under: {DATA_DIR} or pass --csv <path-to-csv>")
        sys.exit(1)
    if not csv_path.exists():
        print(f"ERROR: CSV does not exist: {csv_path}")
        sys.exit(1)

    if args.rebuild:
        if CHROMA_DIR.exists():
            debug(f"Removing vector store: {CHROMA_DIR}")
            if not args.dry:
                shutil.rmtree(CHROMA_DIR, ignore_errors=True)
        cache_db = OUT_DIR / "cache.sqlite"
        if cache_db.exists():
            debug(f"Removing cache: {cache_db}")
            if not args.dry:
                cache_db.unlink(missing_ok=True)

    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(SRC.parent))

    debug(f"Preparing data from CSV → {csv_path}")
    if not args.dry:
        from src.data_prep import build_docs
        from src.config import DATA_DIR as CONF_DATA_DIR
        processed = CONF_DATA_DIR / "processed.jsonl"
        build_docs(csv_path, processed)

    debug("Building/Updating index (ChromaDB)")
    if not args.dry:
        from src.index import build_index
        build_index()

    debug("Running sample queries and saving 6 screenshots to outputs/")
    if not args.dry:
        from src.app_cli import run as run_cli
        run_cli()

    debug("✅ Done! Check outputs/ for the PNG screenshots.")

if __name__ == "__main__":
    main()
