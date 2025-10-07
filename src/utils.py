import re, os, json, hashlib, sqlite3
from pathlib import Path
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
from .config import OUT_DIR

# ---- Simple file-safe text ----
def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s)
    return s.strip()

# ---- SQLite cache for queries ----
class QueryCache:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_table()

    def _ensure_table(self):
        con = sqlite3.connect(self.db_path)
        try:
            con.execute(
                "CREATE TABLE IF NOT EXISTS cache (k TEXT PRIMARY KEY, v TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )
            con.commit()
        finally:
            con.close()

    def _key(self, **kwargs) -> str:
        blob = json.dumps(kwargs, sort_keys=True).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    def get(self, **kwargs):
        k = self._key(**kwargs)
        con = sqlite3.connect(self.db_path)
        try:
            cur = con.execute("SELECT v FROM cache WHERE k=? LIMIT 1", (k,))
            row = cur.fetchone()
            if row:
                return json.loads(row[0])
            return None
        finally:
            con.close()

    def set(self, value, **kwargs):
        k = self._key(**kwargs)
        con = sqlite3.connect(self.db_path)
        try:
            con.execute(
                "INSERT OR REPLACE INTO cache (k, v) VALUES (?, ?)",
                (k, json.dumps(value)),
            )
            con.commit()
        finally:
            con.close()

# ---- Render text to image for "screenshots" ----
def render_text_image(text: str, out_path: Path, width: int = 1400, padding: int = 40):
    lines = []
    # simple wrap
    line = ""
    for word in text.split():
        if len(line) + len(word) + 1 > 110:
            lines.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        lines.append(line)

    img = Image.new("RGB", (width, 200 + 24 * len(lines)), "white")
    draw = ImageDraw.Draw(img)
    y = padding
    for ln in lines:
        draw.text((padding, y), ln, fill="black")
        y += 24
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
