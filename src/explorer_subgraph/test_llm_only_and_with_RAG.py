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
MODEL = os.getenv("CHATGPT_MODEL", "gpt-4.1-nano")
EMBED_MODEL = os.getenv("CHATGPT_EMBEDDING_MODEL", "text-embedding-3-small")
MAX_TOKENS = int(os.getenv("CHATGPT_MAX_RESPONSE_TOKENS", "600"))

openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt file must live next to this script
PROMPT_FILE = "test_llm_only_and_with_RAG.txt"


# ----------------------------
# Helpers
# ----------------------------
def now_ms() -> float:
    return time.perf_counter() * 1000.0


def load_prompt(filename: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def fill_prompt(template: str, source_label: str, source_iri: str, context_text: str) -> str:
    source_iri = source_iri or ""
    context_text = context_text or ""

    return (
        template
        .replace("{SOURCE_LABEL}", source_label)
        .replace("{SOURCE_IRI_OR_EMPTY}", source_iri)
        .replace("{CONTEXT_TEXT}", context_text)
    )


def prepare_output_files(base_dir: str, prefix: str) -> dict:
    os.makedirs(base_dir, exist_ok=True)
    return {
        "prompt_path": os.path.join(base_dir, f"{prefix}.prompt.txt"),
        "step1_path": os.path.join(base_dir, f"{prefix}.step1.json"),
        "step2_path": os.path.join(base_dir, f"{prefix}.step2.json"),
        "manifest_path": os.path.join(base_dir, f"{prefix}.manifest.json"),
    }


def llm_related_only(prompt: str) -> dict:
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
    # Legacy Embedding API (your original style)
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
    # Inputs
    SOURCE_LABEL = "corn"
    SOURCE_IRI = ""  # optional; can be None/empty
    CONTEXT_TEXT = "Agricultural commodity; widely used in food products, animal feed, and industrial processing."

    # Read + fill prompt
    template = load_prompt(PROMPT_FILE)
    prompt = fill_prompt(template, SOURCE_LABEL, SOURCE_IRI, CONTEXT_TEXT)

    # Output paths (child of where python is run)
    output_dir = os.path.join(os.getcwd(), "output")
    prefix = f"explorer_{SOURCE_LABEL}"
    paths = prepare_output_files(output_dir, prefix)

    # Save filled prompt
    with open(paths["prompt_path"], "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"MODEL={MODEL}")
    print(f"EMBED_MODEL={EMBED_MODEL}")
    print(f"Source: {SOURCE_LABEL}")
    print(f"Context: {CONTEXT_TEXT}")

    # Step 1: LLM-only
    s1 = llm_related_only(prompt)
    print("\nStep 1 (LLM-only) latency ms:", round(s1["latency_ms"], 1))

    with open(paths["step1_path"], "w", encoding="utf-8") as f:
        json.dump(s1, f, indent=2)

    # Step 2: grounding + embeddings
    s2 = step2_ground_and_embed(s1, do_embeddings=True)
    print("Step 2 (ground + embed) latency ms:", round(s2["latency_ms"], 1))
    print("  (embedding portion) ms:", round(s2["embed_latency_ms"], 1))

    with open(paths["step2_path"], "w", encoding="utf-8") as f:
        json.dump(s2, f, indent=2)

    # Manifest summary (easy to diff across runs)
    manifest = {
        "model": MODEL,
        "embed_model": EMBED_MODEL,
        "max_tokens": MAX_TOKENS,
        "source_label": SOURCE_LABEL,
        "source_iri": SOURCE_IRI,
        "context_text": CONTEXT_TEXT,
        "step1_latency_ms": s1["latency_ms"],
        "step2_latency_ms": s2["latency_ms"],
        "embed_latency_ms": s2["embed_latency_ms"],
        "total_latency_ms": s1["latency_ms"] + s2["latency_ms"],
        "files": paths,
    }

    with open(paths["manifest_path"], "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Compact sample to stdout
    out = {
        "step1_latency_ms": s1["latency_ms"],
        "step2_latency_ms": s2["latency_ms"],
        "embed_latency_ms": s2["embed_latency_ms"],
        "source": s2["data"]["source"],
        "related_sample": s2["data"]["related"][:3],
    }
    print("\nSample output:")
    print(json.dumps(out, indent=2))
