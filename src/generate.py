import os
from typing import List
from .config import *
from .utils import normalize_text

# Optional OpenAI generation; fallback to deterministic extractive answer
def generate_answer(query: str, contexts: List[str]) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    prompt = f"""You are a helpful fashion search assistant. 
Use ONLY the given product snippets to answer the user's query precisely.
If relevant, name product titles/brands and explain why they match. Be concise.

Query: {query}

Context:
{chr(10).join('- ' + c for c in contexts)}
"""

    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"You are a concise, precise product search explainer."},
                    {"role":"user","content":prompt}
                ],
                temperature=0.2,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI call failed, falling back. Reason: {e}\n\n" + extractive_fallback(query, contexts)

    return extractive_fallback(query, contexts)

def extractive_fallback(query: str, contexts: List[str]) -> str:
    # simple deterministic fallback: return the most directly relevant sentences from contexts
    # (This is just so the pipeline always runs without external APIs.)
    joined = " ".join(contexts)
    # naive: split by '. '
    sents = [s.strip() for s in joined.split('. ') if s.strip()]
    # pick first ~5 sentences that include any word from the query
    qwords = set([w.lower() for w in query.split() if len(w) > 2])
    picked = []
    for s in sents:
        lw = set([w.lower() for w in s.split()])
        if lw & qwords:
            picked.append(s)
        if len(picked) >= 5:
            break
    if not picked:
        picked = sents[:5]
    return "Answer (extractive fallback):\n" + "\n".join(f"- {p}" for p in picked)
