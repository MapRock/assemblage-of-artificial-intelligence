import json
import os
import time
import requests
import openai
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# Config (env)
# ----------------------------
MODEL = os.getenv("CHATGPT_MODEL", "gpt-3.5-turbo-instruct")
EMBED_MODEL = os.getenv("CHATGPT_EMBEDDING_MODEL", "text-embedding-ada-002")
MAX_TOKENS = int(os.getenv("CHATGPT_MAX_RESPONSE_TOKENS", "600"))

openai.api_key = os.getenv("OPENAI_API_KEY")

# ----------------------------
# Helpers
# ----------------------------
def now_ms() -> float:
    return time.perf_counter() * 1000.0

def llm_related_only(source_label: str, context: str, n_min=6, n_max=8) -> dict:
    prompt = f"""
Return ONLY valid JSON. No markdown.

TASK:
Given a source object, propose {n_min} to {n_max} related objects that the source may play a role in.
Not synonyms/antonyms/homonyms.

Each description must be one concrete sentence suitable for semantic embeddings.

In the returning JSON, transform the "source Label" to the label of the Wikidata IRI closest to the specified context.

FORMAT:
{{
  "source": {{"label": "..."}},
  "related": [
    {{"label": "...", "description": "..."}}
  ]
}}

INPUT:
Source label: {source_label}
Context: {context}
""".strip()

    t0 = now_ms()

    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a system component that returns ONLY valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=MAX_TOKENS,
    )

    t1 = now_ms()

    text = resp["choices"][0]["message"]["content"].strip()
    data = json.loads(text)
    return {"latency_ms": (t1 - t0), "data": data}


def wikidata_qid(label: str):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": label,
        "limit": 1,
    }

    headers = {
        "User-Agent": "MapRockExplorerSubgraph/0.1 (https://github.com/MapRock/IntelligenceBusiness; contact: you@example.com)",
        "Accept": "application/json",
    }

    r = requests.get(url, params=params, headers=headers, timeout=15)

    if r.status_code == 403:
        # Fallback: try a more browser-like UA (some environments get blocked otherwise)
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        r = requests.get(url, params=params, headers=headers, timeout=15)

    r.raise_for_status()
    hits = r.json().get("search", [])
    return hits[0].get("id") if hits else None


def embed_texts(texts):
    # Legacy Embedding API
    resp = openai.Embedding.create(
        model=EMBED_MODEL,
        input=texts
    )
    return [d["embedding"] for d in resp["data"]]


def step2_ground_and_embed(step1_payload: dict, do_embeddings: bool = True) -> dict:
    data = step1_payload["data"]

    t0 = now_ms()

    # Ground the source
    src_label = data["source"]["label"]
    src_qid = wikidata_qid(src_label)

    # Ground related nodes
    related = data.get("related", [])
    for item in related:
        qid = wikidata_qid(item["label"])
        item["wikidata_qid"] = qid
        item["iri"] = f"https://www.wikidata.org/entity/{qid}" if qid else None

    # Add source IRI
    data["source"]["wikidata_qid"] = src_qid
    data["source"]["iri"] = f"https://www.wikidata.org/entity/{src_qid}" if src_qid else None

    embed_latency = 0.0
    if do_embeddings:
        texts = [item["description"] for item in related if item.get("description")]
        if texts:
            e0 = now_ms()
            _ = embed_texts(texts)
            e1 = now_ms()
            embed_latency = (e1 - e0)

    t1 = now_ms()
    return {"latency_ms": (t1 - t0), "embed_latency_ms": embed_latency, "data": data}


# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    source = "corn"
    context = "Agricultural commodity; widely used in food products, animal feed, and industrial processing."

    print(f"MODEL={MODEL}")
    print(f"EMBED_MODEL={EMBED_MODEL}")
    print(f"Source: {source}")
    print(f"Context: {context}")

    # Step 1
    s1 = llm_related_only(source, context)

    print("\nStep 1 (LLM-only) latency ms:", round(s1["latency_ms"], 1))

    # Step 2: grounding + embeddings
    s2 = step2_ground_and_embed(s1, do_embeddings=True)
    print("Step 2 (ground + embed) latency ms:", round(s2["latency_ms"], 1))
    print("  (embedding portion) ms:", round(s2["embed_latency_ms"], 1))

    # Show a compact sample
    out = {
        "step1_latency_ms": s1["latency_ms"],
        "step2_latency_ms": s2["latency_ms"],
        "source": s2["data"]["source"],
        "related_sample": s2["data"]["related"][:3],
    }
    print("\nSample output:")
    print(json.dumps(out, indent=2))
