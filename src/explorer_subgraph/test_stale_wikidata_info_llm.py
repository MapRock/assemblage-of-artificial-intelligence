import json
import os
import time
import re
import requests
import openai
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# Config (env)
# ----------------------------
LLM_MODEL = os.getenv("CHATGPT_MODEL", "gpt-4.1-nano")
EMBED_MODEL = os.getenv("CHATGPT_EMBEDDING_MODEL", "text-embedding-3-small")
MAX_TOKENS = int(os.getenv("CHATGPT_MAX_RESPONSE_TOKENS", "300"))

openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT_DISAMBIG_FILE = "prompt_disambiguate_best_effort.txt"
PROMPT_CHOOSE_FILE = "prompt_choose_wikidata_candidate.txt"

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WDQS_URL = "https://query.wikidata.org/sparql"

HEADERS_WIKIDATA = {
    "User-Agent": "MapRockExplorerSubgraph/0.1 (https://github.com/MapRock/IntelligenceBusiness; contact: you@example.com)",
    "Accept": "application/json",
}
HEADERS_WDQS = {
    "User-Agent": "MapRockExplorerSubgraph/0.1 (https://github.com/MapRock/IntelligenceBusiness; contact: you@example.com)",
    "Accept": "application/sparql+json",
}

# A small, practical relationship bundle (adjust anytime)
REL_PROPS = [
    ("P366", "used for"),
    ("P527", "has part"),
    ("P361", "part of"),
    ("P5191", "derived from"),
    ("P1056", "produces"),
    ("P452", "industry"),
    ("P31",  "instance of"),
    ("P279", "subclass of"),
]

# ----------------------------
# Helpers
# ----------------------------
def now_ms() -> float:
    return time.perf_counter() * 1000.0

def script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))

def load_text_from_script_dir(filename: str) -> str:
    path = os.path.join(script_dir(), filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_") or "run"

def prepare_output_files(prefix: str) -> dict:
    out_dir = "C:\MapRock\AssemblageOfAI\src\explorer_subgraph\output"
    os.makedirs(out_dir, exist_ok=True)
    return {
        "dir": out_dir,
        "step1_llm": os.path.join(out_dir, f"{prefix}.step1_llm.json"),
        "step2_candidates": os.path.join(out_dir, f"{prefix}.step2_wikidata_candidates.json"),
        "step3_choose": os.path.join(out_dir, f"{prefix}.step3_llm_choose.json"),
        "step4_relationships": os.path.join(out_dir, f"{prefix}.step4_wikidata_relationships.json"),
        "step5_embeddings": os.path.join(out_dir, f"{prefix}.step5_embeddings.json"),
        "manifest": os.path.join(out_dir, f"{prefix}.manifest.json"),
    }

def fill_prompt_basic(template: str, label_text: str, context_text: str) -> str:
    return (
        template
        .replace("{LABEL_TEXT}", label_text or "")
        .replace("{CONTEXT_TEXT}", context_text or "")
    )

def call_llm_json(prompt: str, temperature: float = 0.0) -> dict:
    t0 = now_ms()
    resp = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON. No markdown. No commentary."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=MAX_TOKENS,
    )
    t1 = now_ms()
    text = resp["choices"][0]["message"]["content"].strip()
    data = json.loads(text)
    return {"latency_ms": (t1 - t0), "data": data}

def qid_from_iri(iri: str) -> str | None:
    if not iri:
        return None
    m = re.search(r"/entity/(Q\d+)$", iri.strip())
    return m.group(1) if m else None

def wikidata_search_candidates(search: str, limit: int = 8) -> dict:
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": search,
        "limit": limit,
    }
    t0 = now_ms()
    r = requests.get(WIKIDATA_API, params=params, headers=HEADERS_WIKIDATA, timeout=15)
    if r.status_code == 403:
        headers = dict(HEADERS_WIKIDATA)
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        r = requests.get(WIKIDATA_API, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    t1 = now_ms()

    hits = r.json().get("search", [])
    candidates = []
    for h in hits:
        qid = h.get("id")
        candidates.append({
            "qid": qid,
            "iri": f"https://www.wikidata.org/entity/{qid}" if qid else "",
            "label": h.get("label", ""),
            "description": h.get("description", ""),
        })

    return {"latency_ms": (t1 - t0), "query": search, "candidates": candidates}

def wdqs_relationships(qid: str, limit_total: int = 80) -> dict:
    prop_values = " ".join([f"wdt:{pid}" for pid, _ in REL_PROPS])
    sparql = f"""
    SELECT ?prop ?propLabel ?value ?valueLabel WHERE {{
      VALUES ?prop {{ {prop_values} }}
      VALUES ?item {{ wd:{qid} }}
      ?item ?prop ?value .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT {limit_total}
    """.strip()

    t0 = now_ms()
    r = requests.get(WDQS_URL, params={"format": "json", "query": sparql}, headers=HEADERS_WDQS, timeout=30)
    r.raise_for_status()
    t1 = now_ms()

    rows = r.json()["results"]["bindings"]
    edges = []
    for b in rows:
        prop_uri = b["prop"]["value"]
        pid = prop_uri.rsplit("/", 1)[-1]
        prop_label = b.get("propLabel", {}).get("value", pid)
        value_iri = b["value"]["value"]
        value_label = b.get("valueLabel", {}).get("value", value_iri.rsplit("/", 1)[-1])
        edges.append({
            "property_pid": pid,
            "property_label": prop_label,
            "value_label": value_label,
            "value_iri": value_iri,
        })

    return {"latency_ms": (t1 - t0), "qid": qid, "edges": edges}

def embed_texts(texts: list[str]) -> dict:
    t0 = now_ms()
    resp = openai.Embedding.create(model=EMBED_MODEL, input=texts)
    t1 = now_ms()
    vectors = [d["embedding"] for d in resp["data"]]
    return {"latency_ms": (t1 - t0), "count": len(vectors), "vectors": vectors}

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    # Provide label and/or context

   
    #LABEL_TEXT = "System 0"  # e.g., "corn"
    #CONTEXT_TEXT = "AI concept related to background thinking"  # e.g., "a cereal grain used for food and fodder"
   
    
    LABEL_TEXT = "S/2025 U 1"  # e.g., "corn"
    CONTEXT_TEXT = "moon of uranus"  # e.g., "a cereal grain used for food and fodder"


    LABEL_TEXT = "corn"  # e.g., "corn"
    CONTEXT_TEXT = "a cereal grain used for food and fodder"  # e.g., "a cereal grain used for food and fodder"

   

    prefix = f"candidate_loop_{safe_slug(LABEL_TEXT or 'no_label')}_{safe_slug(CONTEXT_TEXT)[:35]}"
    paths = prepare_output_files(prefix)

    # Step 1: LLM best-effort disambiguation
    tmpl1 = load_text_from_script_dir(PROMPT_DISAMBIG_FILE)
    p1 = fill_prompt_basic(tmpl1, LABEL_TEXT, CONTEXT_TEXT)
    s1 = call_llm_json(p1, temperature=0.0)
    with open(paths["step1_llm"], "w", encoding="utf-8") as f:
        json.dump(s1, f, indent=2)

    wikidata_iri_step1 = s1["data"]["wikidata_iri"]
    confidence_step1 = s1["data"]["confidence"]
    rationale_step1 = s1["data"]["notes"]

   
    canonical_label = (s1["data"].get("canonical_label") or "").strip()
    llm_iri = (s1["data"].get("wikidata_iri") or "").strip()
    qid = qid_from_iri(llm_iri)

    search_terms = s1["data"].get("search_terms") or []
    if not isinstance(search_terms, list):
        search_terms = []

    # Step 2: Wikidata candidates (array)
    # Choose the best query string available
    candidate_query = (canonical_label or LABEL_TEXT or (search_terms[0] if search_terms else "") or CONTEXT_TEXT).strip()
    s2 = wikidata_search_candidates(candidate_query, limit=8)
    with open(paths["step2_candidates"], "w", encoding="utf-8") as f:
        json.dump(s2, f, indent=2)


    # Step 3: If we don't have QID yet, ask LLM to pick from candidates
    chosen = {"latency_ms": 0.0, "data": {"chosen_qid": qid or "", "chosen_label": canonical_label, "confidence": 0.0, "rationale": ""}}
    confidence3 = None
    rationale3 = None


    # Format candidates JSON compactly for the prompt
    candidates_json = json.dumps(s2["candidates"], ensure_ascii=False, indent=2)

    tmpl3 = load_text_from_script_dir(PROMPT_CHOOSE_FILE)
    p3 = (
        tmpl3
        .replace("{LABEL_TEXT}", LABEL_TEXT or "")
        .replace("{CONTEXT_TEXT}", CONTEXT_TEXT or "")
        .replace("{CANDIDATES_JSON}", candidates_json)
    )
    chosen = call_llm_json(p3, temperature=0.1)

    with open(paths["step3_choose"], "w", encoding="utf-8") as f:
        json.dump(chosen, f, indent=2)

    qid = (chosen["data"].get("chosen_qid") or "").strip()
    canonical_label = (chosen["data"].get("chosen_label") or canonical_label).strip()
    confidence3 = chosen["data"]["confidence"]
    rationale3 = chosen["data"]["rationale"]

    # Step 4: Relationships (Wikidata standing in for “ES graph lookup”)
    s4 = wdqs_relationships(qid, limit_total=80) if qid else {"latency_ms": 0.0, "qid": None, "edges": []}
    with open(paths["step4_relationships"], "w", encoding="utf-8") as f:
        json.dump(s4, f, indent=2)

    # Step 5: Embeddings for relationship texts
    edge_texts = []
    for e in s4.get("edges", []):
        edge_texts.append(f"{canonical_label or LABEL_TEXT} — {e['property_label']} — {e['value_label']}")

    s5 = embed_texts(edge_texts) if edge_texts else {"latency_ms": 0.0, "count": 0, "vectors": []}

    # Save only a small preview
    s5_out = {
        "latency_ms": s5["latency_ms"],
        "count": s5["count"],
        "texts_sample": edge_texts[:10],
        "vector_dim": (len(s5["vectors"][0]) if s5["vectors"] else 0),
        "vectors_sample": s5["vectors"][:2],
    }
    with open(paths["step5_embeddings"], "w", encoding="utf-8") as f:
        json.dump(s5_out, f, indent=2)

    # Manifest
    timings = {
        "step1_llm_best_effort": s1["latency_ms"],
        "step2_wikidata_candidates": s2["latency_ms"],
        "step3_llm_choose_candidate": chosen["latency_ms"],
        "step4_wikidata_relationships": s4["latency_ms"],
        "step5_embeddings": s5["latency_ms"],
    }
    manifest = {
        "llm_model": LLM_MODEL,
        "embed_model": EMBED_MODEL,
        "max_tokens": MAX_TOKENS,
        "inputs": {"label": LABEL_TEXT, "context": CONTEXT_TEXT},
        "intermediate": {
            "canonical_label": canonical_label,
            "llm_iri": llm_iri,
            "resolved_qid": qid,
            "candidate_query": candidate_query,
        },
        "timings_ms": timings,
        "total_ms": sum(timings.values()),
        "artifact_paths": paths,
    }
    with open(paths["manifest"], "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Console summary
    print(f"Original Label and context: '{LABEL_TEXT}', '{CONTEXT_TEXT}'")
    print(f"LLM Wikidata IRI from Step #1: {wikidata_iri_step1}")
    print(f"Confidence and rationale for Step #1: {confidence_step1}, {rationale_step1}")
    print(f"Confidence and rationale for Step #3: {confidence3}, {rationale3}")

    print(f"Canonical label: {canonical_label!r}")
    print(f"Resolved QID:    {qid}")
    print("Timings (ms):")
    for k, v in timings.items():
        print(f"  {k}: {v:.1f}")
    print(f"  total: {manifest['total_ms']:.1f}")
    print(f"Output dir: {paths['dir']}")
