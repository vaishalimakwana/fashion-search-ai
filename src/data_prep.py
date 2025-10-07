import argparse, pandas as pd, json
from pathlib import Path
from .utils import normalize_text
from .config import DATA_DIR

def build_docs(csv_path: Path, out_path: Path):
    df = pd.read_csv(csv_path)
    # Heuristic: keep common product text fields if present
    candidates = [c for c in df.columns if c.lower() in {"id","productid","product_id","title","productname","product_name","brand","description","product_description","category","subcategory","gender","color","material","price"}]
    df = df[candidates] if candidates else df

    docs = []
    for i, row in df.fillna("").iterrows():
        pid = str(row.get("id", row.get("productid", row.get("product_id", i))))
        title = normalize_text(str(row.get("title", row.get("productname", row.get("product_name","")))))
        brand = normalize_text(str(row.get("brand","")))
        desc = normalize_text(str(row.get("description", row.get("product_description",""))))
        category = normalize_text(str(row.get("category","")))
        subcat = normalize_text(str(row.get("subcategory","")))
        gender = normalize_text(str(row.get("gender","")))
        color = normalize_text(str(row.get("color","")))
        material = normalize_text(str(row.get("material","")))
        price = normalize_text(str(row.get("price","")))

        content = " ".join([
            f"Title: {title}" if title else "",
            f"Brand: {brand}" if brand else "",
            f"Category: {category}" if category else "",
            f"Subcategory: {subcat}" if subcat else "",
            f"Gender: {gender}" if gender else "",
            f"Color: {color}" if color else "",
            f"Material: {material}" if material else "",
            f"Description: {desc}" if desc else "",
            f"Price: {price}" if price else "",
        ]).strip()

        if not content:
            continue

        docs.append({
            "id": f"prod_{pid}_{i}",
            "text": content,
            "meta": {
                "pid": pid,
                "title": title,
                "brand": brand,
                "category": category,
                "subcategory": subcat,
                "gender": gender,
                "color": color,
                "material": material,
                "price": price
            }
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"Wrote {len(docs)} docs → {out_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, required=True, help="Path to Myntra CSV")
    ap.add_argument("--out", type=str, default=str(DATA_DIR / "processed.jsonl"))
    args = ap.parse_args()
    build_docs(Path(args.csv), Path(args.out))
