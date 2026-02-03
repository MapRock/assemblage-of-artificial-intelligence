import pandas as pd
import os
import requests
import json
import time
import openai
from typing import List, Dict

from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# Config (env)
# ----------------------------
LLM_MODEL = os.getenv("CHATGPT_MODEL", "gpt-4.1-nano")
EMBED_MODEL = os.getenv("CHATGPT_EMBEDDING_MODEL", "text-embedding-3-small")
MAX_TOKENS = int(os.getenv("CHATGPT_MAX_RESPONSE_TOKENS", "300"))

# User-Agent string required by Wikidata to identify the calling application.
# This should be set via environment variable (WIKIDATA_USER_AGENT) so it can be
# customized per deployment and comply with Wikidata API usage guidelines.
# Example of a fictional User-Agent used to identify an application when calling Wikidata.
#   In real deployments, this should describe the actual application and include a real contact URL.
#   USER_AGENT = "AcmeKnowledgeExplorer/0.0.1 (contact: https://example.com/contact)"
USER_AGENT = os.getenv("WIKIDATA_USER_AGENT")

openai.api_key = os.getenv("OPENAI_API_KEY")
WIKIDATA_API = "https://www.wikidata.org/w/api.php"

WIKIDATA_THROTTLE_SEC = 1.0 # Be a good wikidata citizen.


# -----------------------------
# Configuration
# -----------------------------
INPUT_CSV = "C:\MapRock\AssemblageOfAI\src\explorer_subgraph\products.csv"
OUTPUT_CSV = "C:\MapRock\AssemblageOfAI\src\explorer_subgraph\output\products_with_iri.csv"
TABLE_NAME = "Products"

COLUMN_ROLES = {
    "pk": "product_pk",
    "surrogate_key": "product_code",
    "caption": "product_caption",
    "description": "product_description",
    "iri": "product_iri"
}



# -----------------------------
# Helpers
# -----------------------------
def now_ms():
    return time.perf_counter() * 1000.0


# -----------------------------
# Step 1: LLM disambiguates intent
# -----------------------------
def llm_disambiguate_intent(context: dict) -> dict:
    prompt = {
        "task": "Disambiguate the intended concept without inventing identifiers. What do you think the canonical label would be in Wikidata? Examples: ['corn, a crop grown for cattle fodder and ethanol' should have canonical label of 'maize'.]",
        "rules": [
            "Do NOT return QIDs or IRIs.",
            "Return a canonical label and search terms only.",
            "search_terms should include the canonical_label along with whatever you think is appropriate."
        ],
        "input": context,
        "return_format": {
            "canonical_label": "string",
            "search_terms": ["string"],
            "notes": "one short sentence"
        }
    }

    resp = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON."},
            {"role": "user", "content": json.dumps(prompt)}
        ],
        temperature=0.2,
        max_tokens=MAX_TOKENS
    )

    return json.loads(resp["choices"][0]["message"]["content"])


# -----------------------------
# Step 2: Wikidata candidate lookup
# -----------------------------




def wikidata_search(search_terms: List[str], limit: int = 5) -> List[Dict]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }

    seen = {}

    for term in search_terms:
        params = {
            "action": "wbsearchentities",
            "search": term,
            "language": "en",
            "format": "json",
            "limit": limit
        }

        r = requests.get(
            WIKIDATA_API,
            params=params,
            headers=headers,
            timeout=15
        )

        # If this fires, something is still wrong with headers
        r.raise_for_status()

        payload = r.json()

        for hit in payload.get("search", []):
            qid = hit.get("id")
            if qid and qid not in seen:
                seen[qid] = {
                    "qid": qid,
                    "label": hit.get("label"),
                    "description": hit.get("description", "")
                }

        # Be polite to Wikidata. Don't bombard with rapid requests.
        time.sleep(WIKIDATA_THROTTLE_SEC)

    return list(seen.values())



# -----------------------------
# Step 3: LLM selects best candidate
# -----------------------------
def llm_select_candidate(context: dict, candidates: List[dict]) -> dict:
    prompt = {
        "context": context,
        "candidates": candidates,
        "rules": [
            "Select the best matching Wikidata entity for THIS ROW.",
            "Choose the most specific applicable entity.",
            "Do NOT invent QIDs.",
            "If none match, return empty chosen_qid."
        ],
        "return_format": {
            "chosen_qid": "QID or empty string",
            "chosen_label": "label or empty string",
            "confidence": "float 0.0–1.0",
            "rationale": "one short sentence"
        }
    }

    t0 = now_ms()
    resp = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON."},
            {"role": "user", "content": json.dumps(prompt)}
        ],
        temperature=0.1,
        max_tokens=MAX_TOKENS
    )
    t1 = now_ms()

    result = json.loads(resp["choices"][0]["message"]["content"])
    result["latency_ms"] = t1 - t0
    return result


# -----------------------------
# Main pipeline
# -----------------------------
df = pd.read_csv(INPUT_CSV)
output_rows = []



for _, row in df.iterrows():
    row_context = {
        "table": TABLE_NAME,
        "caption": row[COLUMN_ROLES["caption"]],
        "description": row[COLUMN_ROLES["description"]]
    }
    print(f"Processing row: {row_context}")

    # Step 1
    intent = llm_disambiguate_intent(row_context)
    print(intent)

    # Step 2
    candidates = wikidata_search(intent.get("search_terms", []))

    # Step 3
    selection = llm_select_candidate(row_context, candidates)

    chosen_qid = selection.get("chosen_qid", "")
    chosen_candidate = next(
        (c for c in candidates if c.get("qid") == chosen_qid),
        {}
    )
    chosen_label = chosen_candidate.get("label", "")


    iri = f"https://www.wikidata.org/entity/{chosen_qid}" if chosen_qid else ""

    output_row = dict(row)
    output_row["wikidata_qid"] = chosen_qid
    output_row["product_iri"] = iri
    output_row["wikidata_label"] = chosen_label   # ← THIS IS THE KEY ADD
    output_row["iri_confidence"] = selection.get("confidence", 0.0)
    output_row["iri_rationale"] = selection.get("rationale", "")
    output_row["selection_latency_ms"] = selection.get("latency_ms", 0.0)

    output_rows.append(output_row)

output_df = pd.DataFrame(output_rows)
output_df.to_csv(OUTPUT_CSV, index=False)
