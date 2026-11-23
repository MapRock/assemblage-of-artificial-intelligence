#!/usr/bin/env python3
"""PARTS 2 + 3: ASSOCIATIVE MEMORY FOR CREATIVE INTELLIGENCE

Open this file in VS Code and press F5 (or Run Python File).

INPUT:  The *finished* catalog.json from story_ideas_full_refresh_F5.py.
        No original ideas, direct ideas, or pairwise ideas are regenerated.

PART 2: Create a local, SQLite-backed PROPERTY GRAPH:
        Story --> HAS_REPRESENTATION --> Representation (with cached embedding)
        Story --> HAS_IDEA --> Idea
        Idea  --> INSPIRED_BY --> Story (for pairwise inspirations only)

        Embed BOTH separate representations of each story:
          - unresolved_situation (faithful, concrete, solution-free)
          - generalized_situation (short, cross-domain, solution-free)
        Leave the original story available unaltered in the graph.

PART 3: Immediately verify the graph, test exact self-retrieval, and search
        new solution-free situations through both representation indexes.
        Follow actual graph edges to retrieve ideas and their source stories.
        Produce human-readable Markdown and machine-readable JSON reports.

*** COST SAFETY ***
- No idea-generation or pairwise-comparison calls are made. For a NEW query
  without a supplied generalized version, ONE short LLM rewrite is made.
- Its response is cached by exact query and model/prompt settings; failed model
  responses are retained and NOT retried automatically.
- Existing embeddings are cached BY MODEL + DIMENSIONS + EXACT TEXT HASH.
- Pressing F5 again does NOT re-embed unchanged texts (including demo queries).
- The graph is rebuilt transactionally only if the source catalog changed.
- A failed API request has NO AUTOMATIC RETRIES (network failure may still bill).
- Existing finished catalog.json and previous creative-generation DB untouched.

This is an indexed SQLite property graph with graph traversal, NOT a native
Cypher/Neo4j server. It avoids installing/operating a server for the pilot.
You can move the explicitly typed nodes/edges to Neo4j later.

Dependencies: C:/Python310/python.exe -m pip install -U openai python-dotenv
OPENAI_API_KEY can be in your existing environment or a nearby .env file.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ======================= F5 SETTINGS ================================
# Usually keep blank: automatically select MOST RECENT *COMPLETE* refresh.
# Or paste the full path to a specific catalog.json (Windows paths accepted).
CATALOG_PATH = ""

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 512       # Supported by text-embedding-3-small
INDEX_ORIGINAL_STORY = False    # Later experiment; first test TWO separate views

TOP_MATCHES_PER_VIEW = 3        # Maximum *eligible* stories admitted per view
MIN_SIMILARITY_CONCRETE = 0.30  # Experimental cutoff: tune after examining rankings
MIN_SIMILARITY_GENERAL = 0.30   # Separate, independently adjustable cutoff
STRONG_MATCH_SCORE = 0.60       # Label only; does NOT change retrieval eligibility
RUN_DEMO_QUERIES = True         # Demo queries retain their supplied generalizations
ASK_FOR_QUERY_AT_END = False   # Set True to enter a new situation in the terminal
CUSTOM_QUERY = ""              # Your new UNRESOLVED situation here
CUSTOM_QUERY_GENERALIZED = "" # Leave blank to generate/cache a generalization

QUERY_REWRITE_MODEL = "gpt-6.2-astra" # Same known-working API model as Part 1
QUERY_REWRITE_EFFORT = "low"
QUERY_REWRITE_PROMPT_VERSION = "generalized-query-v1"
QUERY_REWRITE_MAX_TOKENS = 450
QUERY_REWRITE_MAX_INPUT_CHARS = 4000  # Independent guard for new model call
QUERY_REWRITE_MAX_ESTIMATED_USD = 0.08 # Guard per new rewrite (not account cap)
REWRITE_INPUT_PRICE_PER_MILLION = 8.0 # Operator estimate; update for billing
REWRITE_OUTPUT_PRICE_PER_MILLION = 40.0

# Embeddings cost $0.02 / 1M tokens as of Nov 2026. This is a soft guard
# against accidental enormous inputs, not an accurate billing guarantee.
MAX_TEXT_CHARS = 18000
MAX_NEW_EMBEDDING_TEXTS = 60    # Guard: refuse a bulk expansion without review
EMBEDDING_BATCH_SIZE = 24
EMBEDDING_PRICE_USD_PER_M = 0.02
# ====================================================================

BASE = Path(__file__).resolve().parent
OUTPUT_ROOT = BASE / "associative_memory"
DATABASE_PATH = OUTPUT_ROOT / "associative_memory.db"
REPORT_ROOT = OUTPUT_ROOT / "retrieval_reports"

# These are deliberately NEW predicaments, not the originals from your catalog.
# They're diagnostic examples, not a claim of validated retrieval quality.
DEMO_QUERIES = [
    (
        "Small hospital couriers and faster transport carts",
        "Small autonomous couriers carry samples through a hospital where large "
        "delivery carts share the same corridors. The couriers keep being damaged "
        "in encounters with the carts. Engineers keep improving the couriers' ability "
        "to predict cart movements, while the hospital keeps making the carts faster "
        "to increase throughput. The smaller machines need another way to stay safe.",
        "Two unequal kinds of moving equipment share a workspace. The smaller kind "
        "is harmed by encounters, and improvements to the more powerful kind keep "
        "undermining attempts by the vulnerable kind to predict and avoid it.",
    ),
    (
        "Research institute with rapidly arriving data",
        "A research institute keeps adding laboratories, each with its own data "
        "formats and definitions. Its central team cannot harmonize the new data "
        "as quickly as the laboratories arrive, but researchers need to use the "
        "newly received information before integration is complete.",
        "New sources of information arrive faster than a central integration "
        "process can absorb them. People need some form of access before the "
        "eventual unified representation is ready.",
    ),
    (
        "Arriving early for an annual festival",
        "A family travels to a popular annual festival several days before it starts "
        "to enjoy a calmer beginning. Many other families choose the same early "
        "arrival period. Roads and stopping places become crowded, leaving everyone "
        "tired by the time they arrive, even with extra days at the destination.",
        "A strategy meant to escape a concentrated period of demand becomes "
        "overcrowded because many other people adopt the same strategy. The "
        "original goal is an enjoyable occasion, not simply more time there.",
    ),
]

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS nodes (
    node_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL CHECK(kind IN ('Story','Idea','Representation')),
    label TEXT NOT NULL,
    properties_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_nodes_kind ON nodes(kind);
CREATE TABLE IF NOT EXISTS edges (
    source_id TEXT NOT NULL REFERENCES nodes(node_id),
    rel TEXT NOT NULL CHECK(rel IN ('HAS_IDEA','HAS_REPRESENTATION','INSPIRED_BY')),
    target_id TEXT NOT NULL REFERENCES nodes(node_id),
    PRIMARY KEY (source_id, rel, target_id)
);
CREATE INDEX IF NOT EXISTS ix_edges_source_rel ON edges(source_id,rel);
CREATE INDEX IF NOT EXISTS ix_edges_target_rel ON edges(target_id,rel);
CREATE TABLE IF NOT EXISTS embedding_cache (
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    text_hash TEXT NOT NULL,
    embedding_json TEXT NOT NULL,
    input_preview TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY(model,dimensions,text_hash)
);
CREATE TABLE IF NOT EXISTS node_embeddings (
    representation_id TEXT PRIMARY KEY REFERENCES nodes(node_id),
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    text_hash TEXT NOT NULL,
    FOREIGN KEY (model,dimensions,text_hash)
       REFERENCES embedding_cache(model,dimensions,text_hash)
);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS query_rewrite_cache (
    request_key TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    query_text TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('success','invalid')),
    generalized_text TEXT,
    raw_response TEXT NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    estimated_cost_usd REAL,
    created_at TEXT NOT NULL
);
"""


def digest(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_text(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(data, encoding="utf-8")
    temporary.replace(path)


def discover_catalog() -> Path:
    if CATALOG_PATH.strip():
        custom = Path(CATALOG_PATH).expanduser()
        if not custom.is_absolute():
            custom = BASE / custom
        if not custom.is_file():
            raise FileNotFoundError(f"CATALOG_PATH does not exist: {custom}")
        return custom

    root = BASE / "story_idea_experiments"
    finished = sorted(
        (p / "story_idea_reports" / "catalog.json" for p in root.glob("run_*")
         if (p / "COMPLETE.txt").is_file() and
         (p / "story_idea_reports" / "catalog.json").is_file()),
        key=lambda p: (p.stat().st_mtime_ns, str(p)), reverse=True)
    if finished:
        return finished[0]
    fallbacks = [BASE / "story_idea_reports" / "catalog.json", BASE / "catalog.json"]
    for candidate in fallbacks:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "No completed catalog.json found. Place this script beside the earlier "
        "full-refresh program, or set CATALOG_PATH to the catalog you uploaded.")


def require_text(obj: dict, key: str, context: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}: missing/empty {key}")
    if len(value) > MAX_TEXT_CHARS and key in (
            "unresolved_situation", "generalized_situation", "original_text"):
        raise ValueError(f"{context}: {key} exceeds MAX_TEXT_CHARS; stopped before API")
    return value.strip()


def validate_catalog(path: Path) -> tuple[list[dict], str]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or not isinstance(obj.get("stories"), list):
        raise ValueError("Expected JSON object with a 'stories' list")
    stories = obj["stories"]
    if not stories:
        raise ValueError("The catalog has no stories")
    known_ids = set()
    idea_ids = set()
    normalized = []
    for story in stories:
        if not isinstance(story, dict):
            raise ValueError("Story record is not an object")
        sid = require_text(story, "story_id", "story")
        if sid in known_ids:
            raise ValueError(f"Duplicate story ID: {sid}")
        known_ids.add(sid)
        normalized.append(story)
        for key in ("title", "original_text", "unresolved_situation", "generalized_situation"):
            require_text(story, key, sid)
        if not isinstance(story.get("ideas"), list):
            raise ValueError(f"{sid}: missing ideas array")
        for idea in story["ideas"]:
            if not isinstance(idea, dict):
                raise ValueError(f"{sid}: idea is not an object")
            iid = idea.get("idea_id")
            if not isinstance(iid, int) or isinstance(iid, bool) or iid in idea_ids:
                raise ValueError(f"{sid}: idea_id missing or repeated: {iid}")
            idea_ids.add(iid)
            if idea.get("target_story_id") != sid:
                raise ValueError(f"Idea {iid} target mismatch: expected {sid}")
            origin = idea.get("origin")
            if origin not in ("ORIGINAL", "DIRECT", "INSPIRED"):
                raise ValueError(f"Idea {iid}: invalid origin {origin}")
            for key in ("caption", "description", "principle", "source_detail"):
                require_text(idea, key, f"idea {iid}")
            if origin != "INSPIRED" and idea.get("inspired_by_story_id") is not None:
                raise ValueError(f"Idea {iid}: only INSPIRED may have source story")
            if origin == "INSPIRED" and not idea.get("inspired_by_story_id"):
                raise ValueError(f"Idea {iid}: INSPIRED without source story")
    for story in stories:
        for idea in story["ideas"]:
            other = idea.get("inspired_by_story_id")
            if other is not None and other not in known_ids:
                raise ValueError(f"Idea {idea['idea_id']}: source story {other} not in catalog")
    # Ignore API run records: only actual story, situation, and idea content defines graph.
    relevant = [
        {"story_id": s["story_id"], "title": s["title"],
         "original_text": s["original_text"],
         "unresolved_situation": s["unresolved_situation"],
         "generalized_situation": s["generalized_situation"],
         "ideas": s["ideas"]}
        for s in stories
    ]
    fingerprint = digest(json.dumps(relevant, ensure_ascii=False, sort_keys=True))
    return normalized, fingerprint


def rep_kinds() -> tuple[str, ...]:
    return (("unresolved_situation", "generalized_situation", "original_text")
            if INDEX_ORIGINAL_STORY else
            ("unresolved_situation", "generalized_situation"))


def graph_ids(story_id: str) -> str:
    return "story:" + story_id


def rep_id(story_id: str, field: str) -> str:
    return "repr:" + story_id + ":" + field


def idea_node_id(idea_id: int) -> str:
    return "idea:" + str(idea_id)


def open_database(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(path))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=2000")
    db.executescript(SCHEMA)
    return db


def cached_vector(db: sqlite3.Connection, text: str) -> list[float] | None:
    row = db.execute("""SELECT embedding_json FROM embedding_cache
        WHERE model=? AND dimensions=? AND text_hash=?""",
        (EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, digest(text))).fetchone()
    if row is None:
        return None
    v = json.loads(row["embedding_json"])
    if not isinstance(v, list) or len(v) != EMBEDDING_DIMENSIONS:
        raise RuntimeError("Cached embedding has wrong dimensions; refusing to use it")
    if not all(isinstance(f, (int,float)) and math.isfinite(f) for f in v):
        raise RuntimeError("Cached embedding contains an invalid number")
    return v


def normalize_vector(values: list[float]) -> list[float]:
    if len(values) != EMBEDDING_DIMENSIONS:
        raise ValueError(f"Expected {EMBEDDING_DIMENSIONS} dimensions, got {len(values)}")
    if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in values):
        raise ValueError("API embedding contained non-finite elements")
    norm = math.sqrt(math.fsum(float(x)*float(x) for x in values))
    if norm <= 1e-20:
        raise ValueError("API embedding was effectively zero")
    return [float(x) / norm for x in values]


def make_client() -> Any:
    try:
        from dotenv import load_dotenv
        load_dotenv(BASE / ".env")
        load_dotenv()  # Match the original F5 program's key discovery.
    except ImportError:
        pass
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY missing. Put it in your existing environment "
                           "or .env next to this script; no API requests made.")
    try:
        from openai import OpenAI
    except ImportError as e:
        raise RuntimeError(
            "Install with C:/Python310/python.exe -m pip install -U openai python-dotenv") from e
    return OpenAI(max_retries=0, timeout=90.0)


# Only used for NEW queries without a generalized version. This function never
# creates ideas, changes the source catalog, or modifies the graph's story nodes.
QUERY_REWRITE_SYSTEM = """Rewrite a NEW predicament as a generalized, solution-free
retrieval representation. Preserve its actual structural relationships, participants'
roles, constraints, and goals. Abstract away incidental domain nouns only where
this preserves meaning. Never invent events, hidden causes, solutions, outcomes,
or morals. Avoid generic empty abstractions. Return ONLY a JSON object with one
string field named generalized_situation, no markdown fences."""


def extract_generalized(raw: str, original: str) -> str:
    """Strictly validate the reply; don't silently use concrete text as substitute."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I).strip()
    doc=json.loads(cleaned)
    if not isinstance(doc,dict) or set(doc)!={"generalized_situation"}:
        raise ValueError("Query rewrite must contain only generalized_situation")
    result=doc["generalized_situation"]
    if not isinstance(result,str):
        raise ValueError("Query generalized_situation must be text")
    result=result.strip()
    if not 15 <= len(result.split()) <= 120:
        raise ValueError("Generalized query must be 15–120 words")
    if len(result)>MAX_TEXT_CHARS or result==original.strip():
        raise ValueError("Query generalization is invalid or identical to input")
    return result


def generalized_query(db: sqlite3.Connection, situation: str,
                      client_factory=None) -> str:
    """One call per *new* input, durable cache, no automatic retries after bad output.

    A network exception may still incur charges; the OpenAI client has retries=0.
    """
    situation=situation.strip()
    if not situation:
        raise ValueError("Cannot generalize empty query")
    if len(situation)>QUERY_REWRITE_MAX_INPUT_CHARS:
        raise ValueError(f"Query is longer than {QUERY_REWRITE_MAX_INPUT_CHARS} characters; "
                         "shorten it before any model call")
    key=digest(json.dumps({"model":QUERY_REWRITE_MODEL,
                           "effort":QUERY_REWRITE_EFFORT,
                           "version":QUERY_REWRITE_PROMPT_VERSION,
                           "situation":situation},sort_keys=True,ensure_ascii=False))
    found=db.execute("SELECT * FROM query_rewrite_cache WHERE request_key=?",(key,)).fetchone()
    if found is not None:
        if found["status"]!="success":
            raise RuntimeError("This query rewrite previously returned an invalid response. "
                               "Raw reply is retained in query_rewrite_cache; "
                               "no automatic paid retry.")
        print("  Query generalization: cached; 0 new model calls")
        return found["generalized_text"]

    user=("Generalize the following NEW, UNRESOLVED situation in 25–65 words. "
          "Keep its meaningful asymmetries and constraints; describe the "
          "predicament as it stands, NOT its solution.\n\n" + situation)
    estimated=((len((QUERY_REWRITE_SYSTEM+user).encode('utf8'))+1000) *
               REWRITE_INPUT_PRICE_PER_MILLION + QUERY_REWRITE_MAX_TOKENS *
               REWRITE_OUTPUT_PRICE_PER_MILLION)/1_000_000
    if estimated>QUERY_REWRITE_MAX_ESTIMATED_USD:
        raise RuntimeError(f"Query rewrite reserve ${estimated:.4f} exceeds per-call "
                           f"guard ${QUERY_REWRITE_MAX_ESTIMATED_USD:.4f}")
    print(f"  Query generalization: ONE new low-effort model call "
          f"(conservative reserve ${estimated:.4f})",flush=True)
    client=(client_factory or make_client)()
    kwargs={"model":QUERY_REWRITE_MODEL,
            "input":[{"role":"system","content":QUERY_REWRITE_SYSTEM},
                     {"role":"user","content":user}],
            "max_output_tokens":QUERY_REWRITE_MAX_TOKENS,
            "store":False}
    if QUERY_REWRITE_EFFORT!="none":
        kwargs["reasoning"]={"effort":QUERY_REWRITE_EFFORT}
    response=client.responses.create(**kwargs)
    raw=getattr(response,"output_text","") or ""
    usage=getattr(response,"usage",None)
    tokens_in=getattr(usage,"input_tokens",None) if usage else None
    tokens_out=getattr(usage,"output_tokens",None) if usage else None
    cost=((tokens_in or 0)*REWRITE_INPUT_PRICE_PER_MILLION+
          (tokens_out or 0)*REWRITE_OUTPUT_PRICE_PER_MILLION)/1_000_000 if usage else None
    try:
        if getattr(response,"status","completed")!="completed":
            raise ValueError("Query rewrite response was not complete")
        result=extract_generalized(raw,situation)
        status="success"
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        status="invalid"
        result=None
        invalid_reason=str(exc)
    with db:
        db.execute("""INSERT INTO query_rewrite_cache
          (request_key,model,prompt_version,query_text,status,generalized_text,
           raw_response,input_tokens,output_tokens,estimated_cost_usd,created_at)
          VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
          (key,QUERY_REWRITE_MODEL,QUERY_REWRITE_PROMPT_VERSION,situation,
           status,result,raw,tokens_in,tokens_out,cost,stamp()))
    if status!="success":
        raise RuntimeError("Model returned invalid query generalization: "+invalid_reason+
                           "; cached raw response, will NOT automatically retry")
    print(f"  Query generalization saved: {result}")
    return result


def embed_missing(db: sqlite3.Connection, texts: list[str], client_factory=None) -> int:
    """Embed only unique uncached strings. Keep each completed batch safely cached.

    A network failure has no silent retries, so costs are not hidden.
    """
    unique = list(dict.fromkeys(s.strip() for s in texts))
    if any(not s for s in unique):
        raise ValueError("Cannot embed an empty text")
    if any(len(s) > MAX_TEXT_CHARS for s in unique):
        raise ValueError("A text exceeds MAX_TEXT_CHARS; stopped before API")
    missing = [s for s in unique if cached_vector(db, s) is None]
    print(f"Embedding cache: {len(unique)-len(missing)} reused, {len(missing)} new")
    if not missing:
        return 0
    if len(missing) > MAX_NEW_EMBEDDING_TEXTS:
        raise RuntimeError(f"Refusing to send {len(missing)} new embeddings at once. "
                           f"Review MAX_NEW_EMBEDDING_TEXTS={MAX_NEW_EMBEDDING_TEXTS}.")
    # Conservative token upper bound just for operator visibility; not a charge estimate.
    conservative_tokens = sum(len(s.encode("utf-8")) for s in missing)
    print(f"  Maximum rough input upper bound: {conservative_tokens:,} tokens "
          f"(~${conservative_tokens*EMBEDDING_PRICE_USD_PER_M/1_000_000:.5f} "
          "at configured rate; actual should be lower)")
    client = (client_factory or make_client)()
    billed_estimate = 0.0
    for offset in range(0, len(missing), EMBEDDING_BATCH_SIZE):
        group = missing[offset:offset+EMBEDDING_BATCH_SIZE]
        print(f"  API: embedding {len(group)} texts "
              f"({offset + 1}-{offset+len(group)} of {len(missing)})", flush=True)
        # Paid embedding request; a missing query generalization may also need
        # one small, separately cached Responses API request.
        response = client.embeddings.create(
            model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIMENSIONS,
            input=group, encoding_format="float")
        data = sorted(response.data, key=lambda item: item.index)
        if len(data) != len(group) or [item.index for item in data] != list(range(len(group))):
            raise RuntimeError("Embeddings API returned missing or reordered indexes; "
                               "no cache entries written from this batch")
        vectors = [normalize_vector(item.embedding) for item in data]
        # Save only after the entire response has been validated.
        with db:
            for text,vector in zip(group, vectors):
                db.execute("""INSERT OR IGNORE INTO embedding_cache
                   (model,dimensions,text_hash,embedding_json,input_preview,created_at)
                   VALUES (?,?,?,?,?,?)""", (
                    EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, digest(text),
                    json.dumps(vector, separators=(",", ":")), text[:100], stamp()))
        usage = getattr(response, "usage", None)
        tokens = getattr(usage, "total_tokens", None) if usage is not None else None
        if tokens is None and usage is not None:
            tokens = getattr(usage, "prompt_tokens", None)
        if tokens is not None:
            charge = int(tokens) * EMBEDDING_PRICE_USD_PER_M / 1_000_000
            billed_estimate += charge
            print(f"  Cached batch; {tokens} input tokens, estimated ${charge:.6f}")
        else:
            print("  Cached batch; server did not report token usage")
    if billed_estimate:
        print(f"New embeddings estimated cost: ${billed_estimate:.6f}")
    return len(missing)


def get_metadata(db: sqlite3.Connection, key: str) -> str | None:
    row = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row["value"] if row else None


def build_graph(db: sqlite3.Connection, stories: list[dict], fingerprint: str) -> bool:
    settings = json.dumps({"model": EMBEDDING_MODEL,
                           "dimensions": EMBEDDING_DIMENSIONS,
                           "repr_kinds": rep_kinds()}, sort_keys=True)
    if get_metadata(db, "dataset_hash") == fingerprint and get_metadata(db, "settings") == settings:
        print("Graph unchanged: reusing existing nodes, edges, and embeddings.")
        return False
    print("Building property graph in one SQLite transaction ...")
    with db:
        # Keep embedding_cache intact; it preserves previous paid embeddings.
        db.execute("DELETE FROM node_embeddings")
        db.execute("DELETE FROM edges")
        db.execute("DELETE FROM nodes")
        for s in stories:
            sid = s["story_id"]
            snode = graph_ids(sid)
            db.execute("INSERT INTO nodes VALUES (?,?,?,?)", (
                snode, "Story", s["title"],
                json.dumps({"story_id":sid,"title":s["title"],
                            "original_text":s["original_text"]}, ensure_ascii=False)))
            for field in rep_kinds():
                rid = rep_id(sid,field)
                value = s[field].strip()
                if cached_vector(db,value) is None:
                    raise RuntimeError(f"Missing paid embedding for {rid}; graph not replaced")
                db.execute("INSERT INTO nodes VALUES (?,?,?,?)", (
                    rid,"Representation",field,
                    json.dumps({"story_id":sid,"field":field,"text":value},
                               ensure_ascii=False)))
                db.execute("INSERT INTO edges VALUES (?,?,?)", (snode,"HAS_REPRESENTATION",rid))
                db.execute("INSERT INTO node_embeddings VALUES (?,?,?,?)", (
                    rid, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, digest(value)))
        for s in stories:
            for idea in s["ideas"]:
                inode = idea_node_id(idea["idea_id"])
                db.execute("INSERT INTO nodes VALUES (?,?,?,?)", (
                    inode,"Idea",idea["caption"],json.dumps(idea,ensure_ascii=False)))
                db.execute("INSERT INTO edges VALUES (?,?,?)", (
                    graph_ids(s["story_id"]), "HAS_IDEA", inode))
                if idea["origin"] == "INSPIRED":
                    db.execute("INSERT INTO edges VALUES (?,?,?)", (
                        inode,"INSPIRED_BY",graph_ids(idea["inspired_by_story_id"])))
        db.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("dataset_hash",fingerprint))
        db.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("settings",settings))
        db.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("last_graph_build_utc",stamp()))
    return True


def graph_properties(db: sqlite3.Connection, node_id: str) -> dict:
    row = db.execute("SELECT properties_json FROM nodes WHERE node_id=?", (node_id,)).fetchone()
    if row is None:
        raise ValueError(f"Unknown graph node: {node_id}")
    return json.loads(row["properties_json"])


def follow(db: sqlite3.Connection, node_id: str, relation: str) -> list[str]:
    """Graph edge traversal (not a scan through the incoming catalog)."""
    return [r["target_id"] for r in db.execute(
        "SELECT target_id FROM edges WHERE source_id=? AND rel=? ORDER BY target_id",
        (node_id,relation))]


def graph_ideas(db: sqlite3.Connection, story_id: str) -> list[dict]:
    """Follow Story -> Idea -> (optional) inspiration-source Story."""
    results = []
    for inode in follow(db, graph_ids(story_id), "HAS_IDEA"):
        idea = graph_properties(db, inode)
        inspirations = follow(db, inode, "INSPIRED_BY")
        if idea["origin"] == "INSPIRED":
            if len(inspirations) != 1:
                raise RuntimeError(f"Broken provenance path for {inode}")
            source = graph_properties(db,inspirations[0])
            idea["inspiration_source_title"] = source["title"]
        else:
            if inspirations:
                raise RuntimeError(f"Unexpected provenance link for {inode}")
            idea["inspiration_source_title"] = None
        results.append(idea)
    order = {"ORIGINAL":0,"DIRECT":1,"INSPIRED":2}
    return sorted(results,key=lambda i:(order[i["origin"]],i.get("idea_id",0)))


def indexed_representations(db: sqlite3.Connection) -> dict[str,list[dict]]:
    entries = {key: [] for key in rep_kinds()}
    rows = db.execute("""SELECT n.node_id, n.properties_json, c.embedding_json
        FROM nodes n
        JOIN node_embeddings e ON e.representation_id=n.node_id
        JOIN embedding_cache c ON c.model=e.model AND c.dimensions=e.dimensions
             AND c.text_hash=e.text_hash
        WHERE n.kind='Representation' ORDER BY n.node_id""").fetchall()
    for row in rows:
        props = json.loads(row["properties_json"])
        entry = {"story_id":props["story_id"], "field":props["field"],
                 "text":props["text"], "vector":json.loads(row["embedding_json"])}
        entries[props["field"]].append(entry)
    return entries


def similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Cannot compare embeddings of different dimensions")
    return math.fsum(x*y for x,y in zip(a,b)) # Both vectors normalized on storage


def validate_graph(db: sqlite3.Connection, stories: list[dict]) -> dict[str,int]:
    """Structural correctness (a genuine invariant, unlike subjective relevance)."""
    counts = {r["kind"]:r["n"] for r in db.execute(
        "SELECT kind, COUNT(*) n FROM nodes GROUP BY kind")}
    expected_ideas = sum(len(s["ideas"]) for s in stories)
    expected_inspirations = sum(i["origin"]=="INSPIRED" for s in stories for i in s["ideas"])
    expected = {"Story":len(stories),"Idea":expected_ideas,
                "Representation":len(stories)*len(rep_kinds())}
    if counts != expected:
        raise RuntimeError(f"Graph nodes: expected {expected}, got {counts}")
    edge_counts = {r["rel"]:r["n"] for r in db.execute(
        "SELECT rel, COUNT(*) n FROM edges GROUP BY rel")}
    expected_edges = {"HAS_REPRESENTATION":expected["Representation"],
                      "HAS_IDEA":expected_ideas,
                      "INSPIRED_BY":expected_inspirations}
    if edge_counts != expected_edges:
        raise RuntimeError(f"Graph edges: expected {expected_edges}, got {edge_counts}")
    if db.execute("PRAGMA foreign_key_check").fetchone():
        raise RuntimeError("Graph has broken foreign keys")
    for s in stories:
        sid=s["story_id"]
        props=graph_properties(db, graph_ids(sid))
        if props["original_text"]!=s["original_text"]:
            raise RuntimeError(f"Original story text changed in graph: {sid}")
        links=follow(db,graph_ids(sid),"HAS_REPRESENTATION")
        if set(links)!={rep_id(sid,key) for key in rep_kinds()}:
            raise RuntimeError(f"Broken representation links for {sid}")
        found=graph_ideas(db,sid)
        if {i["idea_id"] for i in found}!={i["idea_id"] for i in s["ideas"]}:
            raise RuntimeError(f"Broken idea links for {sid}")
        for idea in found:
            if idea["origin"]=="INSPIRED":
                source=follow(db,idea_node_id(idea["idea_id"]),"INSPIRED_BY")
                if source != [graph_ids(idea["inspired_by_story_id"])]:
                    raise RuntimeError(f"Wrong provenance for idea {idea['idea_id']}")
    index = indexed_representations(db)
    for field,rows in index.items():
        if len(rows)!=len(stories):
            raise RuntimeError(f"Embedding index {field}: missing entries")
        for entry in rows:
            if len(entry["vector"])!=EMBEDDING_DIMENSIONS:
                raise RuntimeError("Embedding index has malformed vectors")
            if cached_vector(db,entry["text"]) != entry["vector"]:
                raise RuntimeError("Stored representation embedding doesn't match cache")
            # Self-retrieval test: exact same text returns itself at score ~1.
            top=max((similarity(entry["vector"],other["vector"]),other["story_id"])
                    for other in rows)
            if top[1]!=entry["story_id"] or abs(top[0]-1.0)>1e-5:
                raise RuntimeError(f"Self-retrieval failed for {entry['story_id']} ({field})")
    print("PASS: all story, idea, representation, and inspiration links validated")
    print(f"PASS: self-retrieval for {len(stories)} stories in EACH of {len(rep_kinds())} views")
    print(f"  Nodes: {expected} | Edges: {expected_edges}")
    return {**expected, **expected_edges}


def rank_view(db: sqlite3.Connection, index: dict, field: str,
              query_text: str) -> list[dict]:
    vec = cached_vector(db,query_text)
    if vec is None:
        raise RuntimeError("Query embedding not cached; abort rather than invent a score")
    scores=[]
    for item in index[field]:
        story_props=graph_properties(db,graph_ids(item["story_id"]))
        scores.append({"story_id":item["story_id"], "title":story_props["title"],
                       "score":round(similarity(vec,item["vector"]),6)})
    return sorted(scores,key=lambda x:(-x["score"],x["story_id"]))


def thresholds() -> dict[str,float]:
    values={"unresolved_situation":MIN_SIMILARITY_CONCRETE,
            "generalized_situation":MIN_SIMILARITY_GENERAL}
    if INDEX_ORIGINAL_STORY:
        values["original_text"]=MIN_SIMILARITY_CONCRETE
    for name,value in values.items():
        if not -1 <= value <= 1:
            raise ValueError(f"Similarity cutoff for {name} must lie in [-1,1]")
    if TOP_MATCHES_PER_VIEW<1:
        raise ValueError("TOP_MATCHES_PER_VIEW must be >=1")
    return values


def query_memory(db: sqlite3.Connection, index: dict, title: str,
                 situation: str, generalized: str) -> dict:
    """Bounded, threshold-gated story retrieval; follow real graph edges.

    A story gets in ONLY if its per-view score meets that view's cutoff AND
    it is among that view's first K eligible stories. We do not pad to K.
    Ranking is kept independently for each view; no synthetic aggregate score.
    """
    if not generalized.strip():
        raise ValueError("Missing generalized query: prepare before query_memory")
    input_by_view={"unresolved_situation":situation.strip(),
                   "generalized_situation":generalized.strip(),
                   "original_text":situation.strip()}
    cutoffs=thresholds()
    ranked={field:rank_view(db,index,field,input_by_view[field])
            for field in rep_kinds()}
    selected_by_view={field:[r["story_id"] for r in rows
                             if r["score"]>=cutoffs[field]][:TOP_MATCHES_PER_VIEW]
                      for field,rows in ranked.items()}
    # Interleave RANKS (not cosine values) across independent views. Both
    # views' rank-1 candidates are examined before either view's rank-2.
    chosen=[]
    for pos in range(TOP_MATCHES_PER_VIEW):
        for field in rep_kinds():
            values=selected_by_view[field]
            if pos<len(values) and values[pos] not in chosen:
                chosen.append(values[pos])
    recalled=[]
    for sid in chosen:
        scores={field:next(r["score"] for r in ranks if r["story_id"]==sid)
                for field,ranks in ranked.items()}
        passed=[field for field in rep_kinds() if sid in selected_by_view[field]]
        original=graph_properties(db,graph_ids(sid))["original_text"]
        ideas=graph_ideas(db,sid)
        recorded=[i for i in ideas if i["origin"]=="ORIGINAL"]
        direct=[i for i in ideas if i["origin"]=="DIRECT"]
        inspired=[i for i in ideas if i["origin"]=="INSPIRED"]
        strong=any(scores[field]>=STRONG_MATCH_SCORE for field in passed)
        # A strong situation match gives a particularly natural context in
        # which to inspect cached analogical inspirations. Still no claim of
        # relevance or proven success for the generated ideas.
        additional=(inspired+direct) if strong else (direct+inspired)
        recalled.append({"story_id":sid,
                         "title":graph_properties(db,graph_ids(sid))["title"],
                         "scores_by_view":scores,
                         "qualified_by_views":passed,
                         "strong_match_heuristic":strong,
                         "original_story":original,
                         "recorded_approaches":recorded,
                         "additional_ideas":additional,
                         "ideas":recorded+additional})
    return {"query_title":title,"situation":situation,
            "generalized_query":generalized,
            "cutoffs":cutoffs,"top_matches_per_view":TOP_MATCHES_PER_VIEW,
            "strong_match_score":STRONG_MATCH_SCORE,
            "rankings":ranked,"selected_by_view":selected_by_view,
            "recalled_stories":recalled}


def report_markdown(result: dict) -> str:
    lines=[f"# Associative recall — {result['query_title']}","",
           "## New unresolved situation","",result["situation"],"",
           "## Generalized situation (provided or generated once and cached)","",
           result["generalized_query"],"",
           "Similarity is cosine similarity, **not** a probability that an analogy "
           "will work. Each embedding view has its own independent ranking and "
           "cutoff. We never pad the selection to a fixed number of stories.","",
           f"Cutoffs: concrete **{result['cutoffs']['unresolved_situation']:.2f}**; "
           f"generalized **{result['cutoffs']['generalized_situation']:.2f}**. "
           f"Maximum per view: **{result['top_matches_per_view']}**.",""]
    for field,ranking in result["rankings"].items():
        lines.extend([f"## Similarity ranking: {field}","",
                      "| Rank | Story | Similarity | Passed cutoff? | Selected? |",
                      "|---:|---|---:|:---:|:---:|"])
        for n,row in enumerate(ranking,1):
            eligible=row["score"]>=result["cutoffs"][field]
            selected=row["story_id"] in result["selected_by_view"][field]
            lines.append(f"| {n} | {row['title']} | {row['score']:.4f} | "
                         f"{'Yes' if eligible else 'No'} | {'Yes' if selected else 'No'} |")
        lines.append("")
    lines.extend(["## Recalled original experiences and ideas", "",
                  "**First:** inspect the original story and any approaches actually "
                  "recorded in it, including failures and known outcomes. A cross-domain "
                  "approach is a source of analogy, not a ready-made solution. "
                  "**Then:** inspect its cached speculative inspirations. A high-scoring "
                  "story match may make those inspirations easier to adapt, but their "
                  "relevance has NOT been individually evaluated.",""])
    if not result["recalled_stories"]:
        lines += ["**No stored story met the configured similarity cutoff.**", "",
                  "No ideas recalled. Check the full rankings above before deciding "
                  "whether to widen the search.",""]
    for n,story in enumerate(result["recalled_stories"],1):
        scores=", ".join(f"{field}: {score:.4f}"
                         for field,score in story["scores_by_view"].items())
        note=("Close match (experimental 0.60 label): cached inspirations may "
              "transfer more directly." if story["strong_match_heuristic"] else
              "Partial match: inspect the source experience for analogical mechanisms.")
        lines.extend([f"### {n}. {story['title']}","",
                      f"**Scores:** {scores}","",
                      f"**Qualified through:** {', '.join(story['qualified_by_views'])}","",
                      f"**Interpretation:** {note}","",
                      "#### Original recorded experience","",story["original_story"],""])
        if story["recorded_approaches"]:
            lines.append("#### Recorded approaches / interventions — FIRST PRIORITY")
            lines.append("")
            for idea in story["recorded_approaches"]:
                lines.extend([f"**{idea['caption']}** (idea {idea['idea_id']})","",
                              idea["description"],"",
                              f"**Underlying principle:** {idea['principle']}",""])
                if idea.get("outcome_note"):
                    lines.extend([f"**Actual reported outcome:** {idea['outcome_note']}",""])
        else:
            lines.extend(["*This source is an observation or predicament without "
                          "an explicitly recorded intervention; examine its original "
                          "relationships and details instead.*",""])
        lines.extend(["#### Further cached ideas (speculative, not verified)","",
                      f"{len(story['additional_ideas'])} additional ideas retained; "
                      "none has been independently ranked against this new query.",""])
        for idea in story["additional_ideas"]:
            lines.extend([f"**[{idea['origin']}] {idea['caption']}** (idea {idea['idea_id']})",""])
            if idea.get("inspiration_source_title"):
                lines.extend([f"*Originally inspired by: {idea['inspiration_source_title']}*",""])
            lines.extend([idea["description"],"",f"**Principle:** {idea['principle']}",""])
            if idea.get("source_detail"):
                lines.extend([f"**Source detail:** {idea['source_detail']}",""])
            if idea.get("analogy"):
                lines.extend([f"**Analogical bridge:** {idea['analogy']}",""])
    return "\n".join(lines)+"\n"


def safe_filename(s: str) -> str:
    return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")[:90] or "query"


def export_graph(db: sqlite3.Connection) -> None:
    """Portable node/edge JSON for inspection or later graph-engine migration."""
    node_rows=db.execute("SELECT * FROM nodes ORDER BY kind,node_id").fetchall()
    edge_rows=db.execute("SELECT * FROM edges ORDER BY rel,source_id,target_id").fetchall()
    doc={"graph_type":"SQLite-backed property graph", "embedding_model":EMBEDDING_MODEL,
         "embedding_dimensions":EMBEDDING_DIMENSIONS,
         "nodes":[{"id":r["node_id"],"kind":r["kind"],"label":r["label"],
                   "properties":json.loads(r["properties_json"])} for r in node_rows],
         "edges":[{"source":r["source_id"],"relation":r["rel"],
                   "target":r["target_id"]} for r in edge_rows]}
    # Vectors live in SQLite and are not duplicated in this human-inspectable export.
    write_text(OUTPUT_ROOT/"graph.json",json.dumps(doc,indent=2,ensure_ascii=False))


def make_readme(source: Path, counts: dict, queries: list[dict]) -> str:
    lines=["# An Associative Memory for Creative Intelligence — Parts 2 + 3", "",
           f"Input (existing, not modified): `{source}`", "",
           "This is a **SQLite-backed property graph**. It records Story, Idea, and "
           "Representation nodes and explicit relationships. It is not Neo4j/Cypher.","",
           f"- Embedding model: `{EMBEDDING_MODEL}` ({EMBEDDING_DIMENSIONS} dimensions)",
           f"- Separate search indexes: `{', '.join(rep_kinds())}`",
           f"- Stories: {counts['Story']}",f"- Existing ideas: {counts['Idea']}",
           f"- Representation nodes: {counts['Representation']}",
           f"- `HAS_IDEA` edges: {counts['HAS_IDEA']}",
           f"- `INSPIRED_BY` edges: {counts['INSPIRED_BY']}",
           f"- `HAS_REPRESENTATION` edges: {counts['HAS_REPRESENTATION']}","",
           "## Verified invariants", "",
           "All graph nodes and links verified; source provenance checked; foreign "
           "keys checked; each story was retrieved as its own nearest neighbor "
           "in each embedding view. This verifies construction, **not** how "
           "creative/relevant the broader semantic retrieval results are.","",
           "## Files", "",
           "- `associative_memory.db`: graph, embeddings, embedding cache",
           "- `graph.json`: portable inspectable nodes and edges, without embedding vectors",
           "- `retrieval_reports/*.md`: full recalled ideas and their provenance",
           "- `retrieval_reports/*.json`: similarity scores and recalled idea records", "",
           "## Diagnostic queries", ""]
    for result in queries:
        name=safe_filename(result["query_title"])
        lines.append(f"- [{result['query_title']}](retrieval_reports/{name}.md)")
    lines.extend(["", "Scores are cosine similarities, not probabilities. "
                  "The script selects stories using per-view minimum cosine cutoffs "
                  "and a per-view top-K ceiling, then displays original recorded "
                  "approaches before cached speculative ideas. It does not evaluate "
                  "individual ideas for relevance or feasibility. For a new query "
                  "without its own generalization, one low-effort query rewrite "
                  "call is made and cached. No creative ideation calls are made.", ""])
    return "\n".join(lines)


def run() -> None:
    print("="*72)
    print("ASSOCIATIVE MEMORY — PART 2 GRAPH + EMBEDDINGS / PART 3 RECALL")
    print("No idea-generation calls. Unseen custom queries may incur ONE cached rewrite call.")
    print("Existing creative catalog and idea DB stay untouched.")
    print("="*72)
    source = discover_catalog()
    print(f"Input catalog: {source}")
    stories, fingerprint=validate_catalog(source)
    print(f"Validated {len(stories)} stories and "
          f"{sum(len(s['ideas']) for s in stories)} existing ideas")
    OUTPUT_ROOT.mkdir(parents=True,exist_ok=True)
    db=open_database(DATABASE_PATH)
    try:
        # Stage 1: prepare (and cache) a real generalized version for EVERY
        # new query missing one. The DEMO examples supply theirs explicitly so
        # historic rankings remain reproducible and incur no rewrite expense.
        query_inputs=[]
        if RUN_DEMO_QUERIES:
            query_inputs.extend(DEMO_QUERIES)
        if CUSTOM_QUERY.strip():
            query_inputs.append(("My new predicament", CUSTOM_QUERY.strip(),
                                 CUSTOM_QUERY_GENERALIZED.strip()))
        normalized_queries=[]
        for name,situation,generalized in query_inputs:
            if not generalized.strip():
                print(f"Preparing generalized query: {name}")
                generalized=generalized_query(db,situation)
            normalized_queries.append((name,situation,generalized))
        query_inputs=normalized_queries
        graph_texts=[s[field].strip() for s in stories for field in rep_kinds()]
        query_texts=[text for _,s,g in query_inputs for text in (s,g)]
        embed_missing(db, graph_texts + query_texts)

        # Stage 2: NEVER wipe an existing good graph unless every new embedding exists.
        was_built=build_graph(db,stories,fingerprint)
        counts=validate_graph(db,stories)
        index=indexed_representations(db)
        export_graph(db)

        # Stage 3: retrieval over BOTH views and graph traversal for the original
        # and pair-inspired idea records.
        results=[]
        for name,situation,generalized in query_inputs:
            result=query_memory(db,index,name,situation,generalized)
            results.append(result)
            filename=safe_filename(name)
            write_text(REPORT_ROOT/(filename+".md"),report_markdown(result))
            write_text(REPORT_ROOT/(filename+".json"),json.dumps(result,indent=2,ensure_ascii=False))
            print(f"\nQUERY: {name}")
            for field,rankings in result["rankings"].items():
                print(f"  {field} top matches:")
                for row in rankings:
                    flag=("RECALL" if row['story_id'] in result['selected_by_view'][field]
                          else "below cutoff" if row['score']<result['cutoffs'][field]
                          else "outside top-K")
                    print(f"    {row['score']:.4f}  {row['title']}: {flag}")
            print(f"  Selected {len(result['recalled_stories'])} qualifying story catalogs; "
                  f"{sum(len(x['ideas']) for x in result['recalled_stories'])} ideas are "
                  "available behind them (not individually scored)")
            for st in result['recalled_stories']:
                print(f"    {st['title']}: {len(st['recorded_approaches'])} recorded "
                      f"approaches FIRST, {len(st['additional_ideas'])} cached ideas")
            print(f"  Full idea details: {REPORT_ROOT / (filename+'.md')}")
        write_text(OUTPUT_ROOT/"README.md",make_readme(source,counts,results))
        print("\n"+"="*72)
        print("SUCCESS: graph built/verified and retrieval test completed")
        print(f"Graph database: {DATABASE_PATH}")
        print(f"Browse summary: {OUTPUT_ROOT / 'README.md'}")
        print("Pressing F5 again reuses cached embeddings, query rewrites, and graph if unchanged.")
        print("="*72)

        if ASK_FOR_QUERY_AT_END:
            print("\nEnter a NEW SOLUTION-FREE predicament (blank to finish).")
            while True:
                try:
                    s=input("\nNew situation > ").strip()
                except (EOFError,KeyboardInterrupt):
                    print("\nFinished.")
                    break
                if not s: break
                if len(s)>MAX_TEXT_CHARS:
                    print("Too long; shorten the input.")
                    continue
                try:
                    g=generalized_query(db,s)
                    embed_missing(db,[s,g])
                    result=query_memory(db,index,"Interactive query "+digest(s)[:8],s,g)
                    filename=safe_filename(result["query_title"])
                    write_text(REPORT_ROOT/(filename+".md"),report_markdown(result))
                    for field,ranking in result["rankings"].items():
                        print(f"{field}: "+", ".join(
                            f"{r['title']} {r['score']:.3f}"
                            for r in ranking
                            if r['story_id'] in result['selected_by_view'][field]))
                    print(f"Full report: {REPORT_ROOT/(filename+'.md')}")
                except Exception as exc:
                    print(f"Search stopped without automatic retries: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    try:
        run()
    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        print(f"\nSTOPPED SAFELY: {exc}",file=sys.stderr)
        sys.exit(1)
