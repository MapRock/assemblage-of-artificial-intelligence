#!/usr/bin/env python3
"""Creative Story Idea Library — complete development refresh.

OPEN THIS ONE FILE IN VS CODE AND PRESS F5 (or Run Python File).

Each COMPLETED F5 run starts a NEW experiment from the six story narratives:
  1) One DIRECT idea-generation call per original story.
  2) One call per story for BOTH a faithful solution-free narrative and a
     separate, shorter generalized solution-free situation.
  3) One bidirectional PAIR call for each unordered story pair, using ONLY
     the two ORIGINAL narratives — never the model-generated ideas.

Results go in a NEW timestamped folder under story_idea_experiments/.
No prior SQLite DB, previous run, or original JSON is overwritten.

SAFETY: An INTERRUPTED run resumes from the last successful saved call on F5.
A parse error is recorded and will NOT be re-billed on subsequent F5 presses
unless you explicitly change RETRY_FAILED_CALLS to True.

Only library needed: pip install -U openai python-dotenv
OPENAI_API_KEY may come from environment or a nearby .env file.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ====================== SIMPLE SETTINGS ==============================
MODEL = "gpt-6.2-astra"
IDEA_REASONING_EFFORT = "medium"       # Keeps the successful experiment's setting
SITUATION_REASONING_EFFORT = "low"     # Short faithful rewrites
BUDGET_USD = 2.00                     # Approximate, per full experiment
MAX_CALLS_PER_LAUNCH = 0              # 0 = all remaining; e.g. 3 for a pilot
RETRY_FAILED_CALLS = False            # Normally do not risk paying twice
DRY_RUN = False                       # True = show what would run; no calls

IDEA_MAX_OUTPUT_TOKENS = 3500
SITUATION_MAX_OUTPUT_TOKENS = 1200
INPUT_PRICE_PER_MILLION = 8.0         # Change if your API rates differ
OUTPUT_PRICE_PER_MILLION = 40.0       # Includes reasoning output tokens
# ====================================================================

BASE = Path(__file__).resolve().parent
EXPERIMENT_ROOT = BASE / "story_idea_experiments"
ACTIVE_RUN_FILE = EXPERIMENT_ROOT / "_incomplete_run.json"
IDEA_PROMPT_VERSION = "creative-library-v1.0"  # Prompts preserved from successful pilot
SITUATION_PROMPT_VERSION = "unresolved-generalized-v1.0"

# THESE ARE THE SIX ORIGINAL STORIES FROM YOUR SUCCESSFUL EXPERIMENT.
# You can edit the list. A changed story starts a new experiment.
STORIES = [{'id': 'warehouse-manager',
  'title': 'Warehouse Manager',
  'text': 'A warehouse manager keeps seeing little mobile drones get squashed by much larger '
          'robots. The manager tries improving the little drones so they are smarter and '
          'better at predicting when a collision is about to happen. But the big robots keep '
          'becoming faster and smarter as the warehouse tries to operate more efficiently, '
          'and the smaller drones continue to get crushed. The manager needs inspiration for '
          'a way to keep the little drones from being squashed, without continually trying to '
          'outpredict the increasingly capable big robots.\n'},
 {'id': 'star-magnolia',
  'title': 'Star magnolia',
  'text': 'one of the valuable characteristics of star magnolia in my yard is that the thick '
          'mesh of short stubby branches provides excellent protection for juncos, '
          'chickadees, and finches. cats, hawks, dogs, cannot easily pentrate the thicket. '
          "it's a great retreat from our nearby bird feeder."},
 {'id': 'ginger-beverage',
  'title': 'Ginger beverage',
  'text': 'One afternoon I wondered whether white ginger from the garden could be used to '
          'make ginger ale the way common ginger root is used. I dug up a small piece of the '
          'rhizome and grated it into a pot of water with sugar and lime. As the mixture '
          'simmered, the kitchen filled with a strong floral aroma that was different from '
          'the familiar smell of culinary ginger. After letting the mixture cool, I strained '
          'it and added sparkling water to make a fizzy drink. The result looked promising, '
          'but the flavor was much stronger and wilder than expected.'},
 {'id': 'thanksgiving-travel',
  'title': 'Thanksgiving Travel',
  'text': 'For years, we tried to get an early start on Thanksgiving by traveling several '
          'days before the holiday. The idea was to arrive at our destination early, settle '
          'in, and enjoy a relaxing Thanksgiving without the pressure of traveling on the '
          'holiday itself.\n'
          'But the experience rarely worked out that way. The roads were crowded with other '
          'travelers who had exactly the same idea. Traffic jams, crowded rest stops, and '
          'unpredictable delays made the journey exhausting. By the time we arrived, we were '
          'already stressed.\n'
          'Eventually, we questioned the assumption that leaving earlier necessarily made the '
          "holiday more relaxing. Our actual objective wasn't to maximize the number of days "
          'at our destination. It was to enjoy Thanksgiving without the stress of heavy '
          'travel.\n'
          'So one year, we decided to travel on Thanksgiving Day itself. The roads were much '
          'quieter, and the drive was considerably more pleasant. We arrived in a better '
          'mood, even though we had sacrificed some time at our destination. The experience '
          'changed how we planned subsequent Thanksgiving trips.'},
 {'id': 'trophic-cascade',
  'title': 'Trophic Cascade',
  'text': "In 1963, ecologist Robert Paine began studying a rocky stretch of Washington's "
          'Pacific coast. The shoreline was home to mussels, barnacles, limpets, sea stars, '
          'and numerous other creatures competing for space on the rocks. Paine noticed that '
          'ochre sea stars regularly preyed on mussels and wondered what would happen to the '
          'other organisms if the sea stars disappeared. He began removing sea stars from a '
          'small section of shoreline while leaving nearby areas undisturbed. Over the '
          'following months, mussels spread rapidly across the cleared rocks. Without the sea '
          'stars feeding on them, the mussels increasingly occupied space that other species '
          'needed. Barnacles and other organisms were crowded out, and the number of species '
          'occupying the experimental area fell from fifteen to eight. The nearby undisturbed '
          'shoreline remained more varied. Paine discovered that the sea stars, despite '
          'eating other animals, had been preventing one competitor from dominating the '
          'community.'},
 {'id': 'data-vault',
  'title': 'Data vault',
  'text': 'A customer of mine was in acquisition mode and looking to expand their business. '
          'The rate of acquisitions outpaced the ability to onboard the data into the data '
          'warehouse. I proposed a data vault strategy. Getting the data into the raw vault '
          "meant it was at least accessible, even though it wasn't fully integrated.Still, a "
          'tougher SQL statement at the user end was better than having no access to the data '
          'at all.Eventually, the new data would be properly onboarded into the integrated '
          'data vault.'}]

DIRECT_SYSTEM = """You are a creative research partner building a persistent library of inspirations.
The goal is CREATIVE POSSIBILITIES, not polished engineering solutions.
Carefully preserve the given story's particular facts. Never invent source events.
Be imaginative, including unconventional possibilities which might require serious
subsequent engineering. Do not rule an inspiration out simply because it is difficult,
expensive, or incomplete. Avoid generic filler and trivial rephrasings.
Reply with one valid JSON object only, no markdown fences."""

PAIR_SYSTEM = """You are exploring analogies between two INDEPENDENTLY RECORDED experiences.
Both stories are equally eligible to be a source of inspiration for the other.
Look for surprising transferable relationships, actions, causal mechanisms,
constraints, incidental operations, accidents, and reversals. The connection need
not be obvious, perfectly analogous, or directly implementable. Suggest creative
DIRECTIONS worth exploring, not final engineering designs. Do not force connections.
Distinguish facts in the source story from your speculative transfer. Do not invent
source events. Consider each direction separately; neither is subordinate to the other.
Reply with one valid JSON object only, no markdown fences."""

DIRECT_TEMPLATE = """Story ID: {id}\nTitle: {title}\n\nORIGINAL STORY (do not alter):\n{story}\n\nGenerate a catalog of creative ideas for this story.\n\nFirst, if the original story ACTUALLY describes one or more approaches,
interventions, or attempted solutions to a difficulty, record those as
'original_ideas' in the order they occur. Include reported outcome or failure,
where known. Do not fabricate an approach for a purely observational story.
An observed natural feature is not automatically a deliberate intervention.
\nSecond, propose 3 to 5 DIFFERENT additional ideas ('direct_ideas'), expanding
past the explicit approach in the story. For purely observational stories,
propose imaginative applications or investigative directions inspired by what
was observed, without fabricating a problem for the original narrator.
\nFor each idea provide:
- caption: a concise title (not the entire idea)
- description: a substantive 60-120 word discussion of the inspiration,
  possible transformations or implications, and what could be investigated;
  speculative ideas should remain speculative
- principle: one sentence expressing the underlying creative principle
- source_detail: what in the original story supports the original approach
  or inspired the newly proposed idea
- outcome_note: actual observed result if the story says, else empty string
\nReturn exactly {{"original_ideas":[{{"caption":"...","description":"...",
"principle":"...","source_detail":"...","outcome_note":"..."}}],
"direct_ideas":[{{"caption":"...","description":"...","principle":"...",
"source_detail":"...","outcome_note":""}}]}}.\n"""

PAIR_TEMPLATE = """Compare two stories to discover unexpected inspirations IN BOTH DIRECTIONS.
\nSTORY A: {a_id} — {a_title}\n{a_text}\n\nSTORY B: {b_id} — {b_title}\n{b_text}\n\nFor A_inspires_B: use details from A to inspire 1-3 substantially different
creative ideas for B. Store the ideas under B, with A as their source.
For B_inspires_A: use details from B to inspire 1-3 substantially different
creative ideas for A. Store the ideas under A, with B as their source.
\nConsider incidental details, not just the main problem or explicit solution.
Prefer surprising, defensible analogical prompts over familiar solutions.
It is fine for either list to be empty if you genuinely find no inspiration.
Avoid merely restating the direct, obvious solutions of the target story.
\nFor each idea:
- caption: a short headline
- description: a substantive 60-120 word exploratory description, explaining
  the possible conceptual transfer and a few possible directions, without
  claiming an engineered solution is already available
- principle: abstract transferable relationship in one sentence
- source_detail: a CONCRETE detail actually found in the SOURCE story
- analogy: how that detail may be reinterpreted for the TARGET story
\nReturn exactly {{"A_inspires_B":[{{"caption":"...","description":"...",
"principle":"...","source_detail":"...","analogy":"..."}}],
"B_inspires_A":[{{"caption":"...","description":"...","principle":"...",
"source_detail":"...","analogy":"..."}}]}}.\n"""


SITUATION_SYSTEM = """You rewrite independently recorded experiences for a searchable
associative-memory library. The goal is to represent the SITUATION without
revealing its known solution, outcome, discovery, moral, or punchline.
Faithful editing, not problem-solving. Never invent facts, motivations,
unsuccessful attempts, observations, or experimental results. An observational
story is not automatically an unsolved problem. Do not suggest solutions.
Return one JSON object only, without markdown fences."""

SITUATION_TEMPLATE = """For this original story, produce TWO DIFFERENT retrieval texts.

1. unresolved_situation (about 40-100 words): Rewrite the circumstances,
   participants, genuine difficulty or open question as they stood BEFORE
   an approach or result became known. Preserve domain-specific context and
   important asymmetries. Exclude the later intervention, remedy, protective
   mechanism, observed result, and stated lesson. Do not manufacture a problem
   for a purely observational story: retain the setting and uncertainty instead.

2. generalized_situation (about 25-60 words): Generalize the situation in #1,
   not the original story's solution. Describe the functional relationships,
   competing goals, constraints, asymmetries, or uncertainties in terms that
   might be recognizable in other domains. Preserve the actual predicament;
   do NOT invent an abstract moral, causal mechanism, solution, outcome, or
   assumptions not supported by the source. Avoid generic filler such as
   'a challenge needs a solution'.

The two fields serve DIFFERENT retrieval pathways. Keep them distinct.

STORY ID: {id}
TITLE: {title}
ORIGINAL STORY:
{story}

Return exactly this JSON object with TWO string values:
{{"unresolved_situation":"...","generalized_situation":"..."}}"""

SCHEMA = """
CREATE TABLE IF NOT EXISTS stories (
  story_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  original_text TEXT NOT NULL,
  original_sha TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
  run_id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_hash TEXT NOT NULL,
  task_kind TEXT NOT NULL CHECK(task_kind IN ('DIRECT','SITUATION','PAIR')),
  story_a_id TEXT NOT NULL REFERENCES stories(story_id),
  story_b_id TEXT REFERENCES stories(story_id),
  model TEXT NOT NULL,
  reasoning_effort TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('success','parse_error')),
  raw_response TEXT NOT NULL,
  prompt_text TEXT NOT NULL,
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  reasoning_tokens INTEGER NOT NULL,
  estimated_cost_usd REAL NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_runs_request ON runs(request_hash, status);
CREATE TABLE IF NOT EXISTS ideas (
  idea_id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_story_id TEXT NOT NULL REFERENCES stories(story_id),
  origin TEXT NOT NULL CHECK(origin IN ('ORIGINAL','DIRECT','INSPIRED')),
  inspired_by_story_id TEXT REFERENCES stories(story_id),
  run_id INTEGER NOT NULL REFERENCES runs(run_id),
  sequence_in_run INTEGER NOT NULL,
  caption TEXT NOT NULL,
  description TEXT NOT NULL,
  principle TEXT NOT NULL,
  source_detail TEXT NOT NULL,
  analogy TEXT NOT NULL,
  outcome_note TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(run_id, target_story_id, origin, sequence_in_run)
);
CREATE INDEX IF NOT EXISTS idx_ideas_target ON ideas(target_story_id, origin);
CREATE TABLE IF NOT EXISTS story_situations (
  story_id TEXT PRIMARY KEY REFERENCES stories(story_id),
  run_id INTEGER NOT NULL UNIQUE REFERENCES runs(run_id),
  unresolved_situation TEXT NOT NULL,
  generalized_situation TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def validate_story_list() -> None:
    if not STORIES:
        raise ValueError("STORIES cannot be empty")
    ids = [s["id"] for s in STORIES]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate story IDs")
    for s in STORIES:
        for key in ("id", "title", "text"):
            if not isinstance(s.get(key), str) or not s[key].strip():
                raise ValueError(f"Missing {key} in story: {s!r}")


def config_fingerprint() -> str:
    config = {
        "stories": STORIES,
        "model": MODEL,
        "ideas_effort": IDEA_REASONING_EFFORT,
        "situation_effort": SITUATION_REASONING_EFFORT,
        "idea_max_output": IDEA_MAX_OUTPUT_TOKENS,
        "situation_max_output": SITUATION_MAX_OUTPUT_TOKENS,
        "idea_prompts": [DIRECT_SYSTEM, DIRECT_TEMPLATE, PAIR_SYSTEM, PAIR_TEMPLATE],
        "situation_prompts": [SITUATION_SYSTEM, SITUATION_TEMPLATE],
    }
    return sha(json.dumps(config, ensure_ascii=False, sort_keys=True))


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def open_experiment_directory() -> tuple[Path, bool]:
    """Resume only interrupted experiments whose inputs haven't changed.

    After a complete run, next F5 creates a fresh DB and pays for new calls.
    """
    EXPERIMENT_ROOT.mkdir(parents=True, exist_ok=True)
    current = config_fingerprint()
    if ACTIVE_RUN_FILE.exists():
        try:
            active = json.loads(ACTIVE_RUN_FILE.read_text(encoding="utf-8"))
            path = EXPERIMENT_ROOT / active["folder"]
            if (active["fingerprint"] == current and path.is_dir()
                    and (path / "story_ideas.db").exists()
                    and not (path / "COMPLETE.txt").exists()):
                return path, True
            print("Prior unfinished experiment retained; settings/stories changed or it is complete.")
        except (ValueError, KeyError, OSError) as exc:
            raise RuntimeError("Active-run metadata could not be read safely. "
                               "Inspect _incomplete_run.json before restarting.") from exc
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    folder = f"run_{stamp}"
    path = EXPERIMENT_ROOT / folder
    path.mkdir(parents=False, exist_ok=False)
    atomic_write_text(ACTIVE_RUN_FILE, json.dumps(
        {"folder": folder, "fingerprint": current, "created_at": now()}, indent=2))
    return path, False


def connect(path: Path) -> sqlite3.Connection:
    # No existing database is ever cleared. Each refresh gets a new directory.
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(SCHEMA)
    return db


def add_stories(db: sqlite3.Connection) -> None:
    with db:
        for s in STORIES:
            digest = sha(s["text"])
            old = db.execute("SELECT original_sha,title FROM stories WHERE story_id=?", (s["id"],)).fetchone()
            if old:
                if old["original_sha"] != digest or old["title"] != s["title"]:
                    raise ValueError(f"Story changed during an incomplete run: {s['id']}")
            else:
                db.execute("INSERT INTO stories VALUES(?,?,?,?,?)",
                           (s["id"], s["title"], s["text"], digest, now()))


def parse_json(s: str) -> dict[str, Any]:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    try:
        data = json.loads(s)
    except json.JSONDecodeError:
        left, right = s.find("{"), s.rfind("}")
        if left < 0 or right < left:
            raise ValueError("No complete JSON object in model output")
        data = json.loads(s[left:right + 1])
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    return data


def validated_ideas(raw: str, kind: str) -> dict[str, list[dict[str,str]]]:
    data = parse_json(raw)
    keys = ("original_ideas", "direct_ideas") if kind == "DIRECT" else ("A_inspires_B", "B_inspires_A")
    parsed: dict[str, list[dict[str,str]]] = {}
    for key in keys:
        arr = data.get(key)
        if not isinstance(arr, list):
            raise ValueError(f"Missing JSON array: {key}")
        checked = []
        for item in arr:
            if not isinstance(item, dict):
                raise ValueError(f"Non-object entry in {key}")
            fields = ("caption", "description", "principle", "source_detail", "analogy", "outcome_note")
            idea = {f: str(item.get(f, "") or "").strip() for f in fields}
            if not all(idea[f] for f in ("caption", "description", "principle", "source_detail")):
                raise ValueError(f"Idea in {key} missing required fields")
            if kind == "PAIR" and not idea["analogy"]:
                raise ValueError(f"Pair idea in {key} missing analogical bridge")
            checked.append(idea)
        parsed[key] = checked
    return parsed


def validated_situations(raw: str) -> tuple[str,str]:
    data = parse_json(raw)
    values = []
    for key in ("unresolved_situation", "generalized_situation"):
        text = data.get(key)
        if not isinstance(text, str) or len(text.strip()) < 25:
            raise ValueError(f"Missing or implausibly short field: {key}")
        values.append(text.strip())
    if values[0].lower() == values[1].lower():
        raise ValueError("Generalized and concrete situation must differ")
    return values[0], values[1]


def prompt_for(kind: str, a: dict[str,str], b: dict[str,str] | None) -> tuple[str,str,str,str]:
    if kind == "DIRECT":
        return DIRECT_SYSTEM, DIRECT_TEMPLATE.format(id=a["id"], title=a["title"], story=a["text"]), IDEA_REASONING_EFFORT, IDEA_PROMPT_VERSION
    if kind == "SITUATION":
        return SITUATION_SYSTEM, SITUATION_TEMPLATE.format(id=a["id"], title=a["title"], story=a["text"]), SITUATION_REASONING_EFFORT, SITUATION_PROMPT_VERSION
    assert kind == "PAIR" and b is not None
    return PAIR_SYSTEM, PAIR_TEMPLATE.format(a_id=a["id"], a_title=a["title"], a_text=a["text"],
                                            b_id=b["id"], b_title=b["title"], b_text=b["text"]), IDEA_REASONING_EFFORT, IDEA_PROMPT_VERSION


def request_hash(kind: str, a: dict[str,str], b: dict[str,str] | None) -> str:
    system, user, effort, prompt_version = prompt_for(kind,a,b)
    return sha(json.dumps([kind, a["id"],b["id"] if b else None, MODEL, effort,
                           prompt_version, system, user], ensure_ascii=False))


def tasks() -> list[tuple[str,dict[str,str],dict[str,str] | None]]:
    # Original ideas are created before any cross-story comparisons.
    return ([("DIRECT", s, None) for s in STORIES]
            + [("SITUATION", s, None) for s in STORIES]
            + [("PAIR", a, b) for a,b in itertools.combinations(STORIES,2)])


def spent(db: sqlite3.Connection) -> float:
    return float(db.execute("SELECT COALESCE(SUM(estimated_cost_usd),0) FROM runs").fetchone()[0])


def call_status(db: sqlite3.Connection, digest: str) -> tuple[str,int] | None:
    row = db.execute("SELECT status,run_id FROM runs WHERE request_hash=? ORDER BY run_id DESC LIMIT 1",(digest,)).fetchone()
    return (row["status"], row["run_id"]) if row else None


def upper_bound_cost(system: str, user: str, max_out: int) -> float:
    # A deliberately cautious pre-call estimate: assume up to one token per UTF8
    # byte of prompt, plus protocol overhead, and the entire output token cap.
    approx_input_tokens = len((system + user).encode("utf-8")) + 1000
    return ((approx_input_tokens * INPUT_PRICE_PER_MILLION)
            + (max_out * OUTPUT_PRICE_PER_MILLION)) / 1_000_000


def model_response(client: Any, system: str, user: str, effort: str, max_out: int) -> tuple[str,int,int,int,bool]:
    # Preserves the same Responses API call pattern that worked in the first experiment.
    kwargs: dict[str, Any] = {
        "model": MODEL,
        "input": [{"role":"system","content":system},{"role":"user","content":user}],
        "max_output_tokens": max_out,
        "store": False,
    }
    if effort != "none":
        kwargs["reasoning"] = {"effort": effort}
    response = client.responses.create(**kwargs)
    raw = response.output_text or ""
    state = getattr(response, "status", "completed")
    completed = state not in ("incomplete", "failed", "cancelled")
    usage = getattr(response, "usage", None)
    if usage is None:
        # Be conservative if billing usage is missing instead of claiming $0.
        in_tokens = len((system + user).encode("utf-8")) + 1000
        out_tokens = max_out
        reasoning_tokens = 0
    else:
        in_tokens = int(getattr(usage,"input_tokens",0) or 0)
        out_tokens = int(getattr(usage,"output_tokens",0) or 0)
        details = getattr(usage,"output_tokens_details",None)
        reasoning_tokens = int(getattr(details,"reasoning_tokens",0) or 0)
    return raw,in_tokens,out_tokens,reasoning_tokens,completed


def save_result(db: sqlite3.Connection, *, kind: str, a: dict[str,str],
                b: dict[str,str] | None, digest: str, effort: str,
                prompt_version: str, prompt_text: str, raw: str,
                in_tokens: int, out_tokens: int, reasoning_tokens: int,
                cost: float, parsed: Any, status: str) -> int:
    # One SQLite transaction holds both the API response and the derived records.
    with db:
        cur = db.execute("""INSERT INTO runs
          (request_hash,task_kind,story_a_id,story_b_id,model,reasoning_effort,
           prompt_version,status,raw_response,prompt_text,input_tokens,output_tokens,
           reasoning_tokens,estimated_cost_usd,created_at)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (digest,kind,a["id"],b["id"] if b else None,MODEL,effort,
           prompt_version,status,raw,prompt_text,in_tokens,out_tokens,
           reasoning_tokens,cost,now()))
        run_id=int(cur.lastrowid)
        if status != "success":
            return run_id
        if kind == "SITUATION":
            unresolved,generalized = parsed
            db.execute("""INSERT INTO story_situations
              (story_id,run_id,unresolved_situation,generalized_situation,created_at)
              VALUES(?,?,?,?,?)""",
              (a["id"],run_id,unresolved,generalized,now()))
            return run_id
        if kind == "DIRECT":
            groups = [(a["id"],None,"ORIGINAL",parsed["original_ideas"]),
                      (a["id"],None,"DIRECT",parsed["direct_ideas"])]
        else:
            assert b is not None
            groups = [(b["id"],a["id"],"INSPIRED",parsed["A_inspires_B"]),
                      (a["id"],b["id"],"INSPIRED",parsed["B_inspires_A"])]
        for target,source,origin,ideas in groups:
            for n,idea in enumerate(ideas,1):
                db.execute("""INSERT INTO ideas
                 (target_story_id,origin,inspired_by_story_id,run_id,sequence_in_run,
                  caption,description,principle,source_detail,analogy,outcome_note,created_at)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (target,origin,source,run_id,n,idea["caption"],idea["description"],
                   idea["principle"],idea["source_detail"],idea["analogy"],
                   idea["outcome_note"],now()))
        return run_id


def export(db: sqlite3.Connection, directory: Path) -> None:
    outdir = directory / "story_idea_reports"
    outdir.mkdir(parents=True,exist_ok=True)
    story_rows = [dict(row) for row in db.execute("""SELECT s.story_id,s.title,s.original_text,
      COALESCE(t.unresolved_situation,'') AS unresolved_situation,
      COALESCE(t.generalized_situation,'') AS generalized_situation
      FROM stories s LEFT JOIN story_situations t ON t.story_id=s.story_id ORDER BY s.rowid""")]
    idea_rows = [dict(row) for row in db.execute("SELECT * FROM ideas ORDER BY idea_id")]
    runs = [dict(row) for row in db.execute("SELECT * FROM runs ORDER BY run_id")]
    titles = {s["story_id"]:s["title"] for s in story_rows}
    catalog = []
    for s in story_rows:
        ideas = [x for x in idea_rows if x["target_story_id"] == s["story_id"]]
        ideas.sort(key=lambda i: ({"ORIGINAL":0,"DIRECT":1,"INSPIRED":2}[i["origin"]],i["idea_id"]))
        catalog.append({**s,"ideas":ideas})
        body=[f"# {s['title']}","","## Original story","",s["original_text"],"",
              "## Solution-free situation","",s["unresolved_situation"] or "Not generated yet.","",
              "## Generalized solution-free situation","",s["generalized_situation"] or "Not generated yet.","",
              "## Ideas and inspirations",""]
        if not ideas:
            body.append("No ideas recorded yet.")
        for number,idea in enumerate(ideas,1):
            body.extend([f"### {number}. {idea['caption']} [{idea['origin']}]",""])
            if idea["inspired_by_story_id"]:
                body.extend([f"**Inspired by:** {titles.get(idea['inspired_by_story_id'], idea['inspired_by_story_id'])}",""])
            body.extend([idea["description"],""])
            for label,key in (("Principle","principle"),("Source detail","source_detail"),
                              ("Analogical bridge","analogy"),("Observed outcome","outcome_note")):
                if idea[key]:
                    body.append(f"**{label}:** {idea[key]}\n")
            body.append(f"*Idea ID {idea['idea_id']}; run {idea['run_id']}*\n")
        safe = re.sub(r"[^a-z0-9-]+","-",s["story_id"].lower()).strip("-")
        atomic_write_text(outdir / f"{safe}.md", "\n".join(body)+"\n")
    atomic_write_text(outdir / "catalog.json", json.dumps({"stories":catalog,"runs":runs},ensure_ascii=False,indent=2))
    counts={kind:sum(r["task_kind"]==kind and r["status"]=="success" for r in runs)
            for kind in ("DIRECT","SITUATION","PAIR")}
    origin_counts={origin:sum(i["origin"]==origin for i in idea_rows)
                   for origin in ("ORIGINAL","DIRECT","INSPIRED")}
    lines=["# Creative story idea library", "", f"Stories: {len(story_rows)}",
           f"Completed DIRECT calls: {counts['DIRECT']}",
           f"Completed SITUATION calls: {counts['SITUATION']}",
           f"Completed PAIR calls (both directions): {counts['PAIR']}",
           f"Idea counts: {origin_counts['ORIGINAL']} original, {origin_counts['DIRECT']} direct, "
           f"{origin_counts['INSPIRED']} inspired",
           f"Estimated recorded API cost: ${spent(db):.4f}", "",
           "| Story | Original | Direct | Inspired | Solution-free | Generalized |",
           "|---|---:|---:|---:|:---:|:---:|"]
    for s in catalog:
        c={o:sum(i["origin"]==o for i in s["ideas"]) for o in ("ORIGINAL","DIRECT","INSPIRED")}
        lines.append(f"| {s['title']} | {c['ORIGINAL']} | {c['DIRECT']} | {c['INSPIRED']} | "
                     f"{'Yes' if s['unresolved_situation'] else '—'} | "
                     f"{'Yes' if s['generalized_situation'] else '—'} |")
    atomic_write_text(outdir / "README.md", "\n".join(lines)+"\n")
    print(f"Saved {outdir / 'catalog.json'} and six readable story reports.")


def run() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(BASE / ".env")
        load_dotenv()
    except ImportError:
        pass
    validate_story_list()
    all_tasks=tasks()
    expected_direct=len(STORIES)
    expected_pair=len(STORIES)*(len(STORIES)-1)//2
    expected_total=len(all_tasks)
    print("="*72)
    print("CREATIVE STORY LIBRARY — FULL DEVELOPMENT REFRESH")
    print(f"{len(STORIES)} stories | {expected_direct} direct calls | {len(STORIES)} situation calls "
          f"| {expected_pair} bidirectional pair calls = {expected_total} calls")
    print(f"Model: {MODEL}, reasoning: {IDEA_REASONING_EFFORT}, rewrite: {SITUATION_REASONING_EFFORT}")
    print(f"Soft spending budget: ${BUDGET_USD:.2f}")
    print("Existing story_ideas.db and catalog.json in your working folder are untouched.")
    print("="*72)

    if DRY_RUN:
        print("DRY_RUN=True: No API calls, no experiment folder written.")
        for kind,a,b in all_tasks:
            print(f" {kind:9} {a['title']}" + (f" ↔ {b['title']}" if b else ""))
        return

    if not os.getenv("OPENAI_API_KEY"):
        print("Missing OPENAI_API_KEY. Set it in your existing environment or .env file.")
        print("No experiment was started and no API calls were made.")
        return

    # Import and instantiate *before* creating the paid-run directory.
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install with: C:/Python310/python.exe -m pip install -U openai python-dotenv") from exc
    # Avoid hidden SDK retries because even a network timeout may follow a billable call.
    client = OpenAI(max_retries=0, timeout=120.0)
    directory,resuming = open_experiment_directory()
    print(f"{'Resuming unfinished' if resuming else 'Starting fresh'} experiment: {directory}")
    db=connect(directory / "story_ideas.db")
    try:
        add_stories(db)
        calls_this_launch=0
        stopped_reason=""
        for kind,a,b in all_tasks:
            digest = request_hash(kind,a,b)
            already = call_status(db,digest)
            if already and already[0] == "success":
                continue
            if already and already[0] == "parse_error" and not RETRY_FAILED_CALLS:
                stopped_reason=(f"The previous {kind} call for {a['title']} returned invalid/incomplete "
                                f"JSON (run {already[1]}). The raw response is safely stored. "
                                "No automatic paid retry. Set RETRY_FAILED_CALLS=True if you want one.")
                break
            if MAX_CALLS_PER_LAUNCH and calls_this_launch >= MAX_CALLS_PER_LAUNCH:
                stopped_reason="Reached MAX_CALLS_PER_LAUNCH; F5 again to resume."
                break
            system,prompt,effort,prompt_version = prompt_for(kind,a,b)
            output_cap = SITUATION_MAX_OUTPUT_TOKENS if kind=="SITUATION" else IDEA_MAX_OUTPUT_TOKENS
            budget_hold = upper_bound_cost(system,prompt,output_cap)
            if spent(db) + budget_hold > BUDGET_USD:
                stopped_reason=(f"Soft budget guard: ${spent(db):.4f} already recorded; "
                                f"reserve ${budget_hold:.4f} for next call exceeds ${BUDGET_USD:.2f}. "
                                "Raise BUDGET_USD and F5 to resume.")
                break
            task_label= f"{kind} {a['title']}" + (f" ↔ {b['title']}" if b else "")
            print(f"Calling: {task_label} (worst-case allowance ${budget_hold:.3f})",flush=True)
            try:
                raw,inp,out,reason,completed = model_response(client,system,prompt,effort,output_cap)
            except Exception as exc:
                stopped_reason = (f"API call failed for {task_label}: {exc}. "
                                  "Stopped; no automatic retry. "
                                  "If the server finished despite a network error, billing is uncertain.")
                print(stopped_reason,file=sys.stderr)
                break
            cost=(inp*INPUT_PRICE_PER_MILLION + out*OUTPUT_PRICE_PER_MILLION)/1_000_000
            try:
                if not completed:
                    raise ValueError("API reported incomplete/failed response")
                parsed = validated_situations(raw) if kind=="SITUATION" else validated_ideas(raw,kind)
                status="success"
            except (ValueError,KeyError,TypeError) as exc:
                status="parse_error"
                parsed=None
                print(f"Model reply failed validation: {exc}",file=sys.stderr)
            run_id=save_result(db,kind=kind,a=a,b=b,digest=digest,effort=effort,
                               prompt_version=prompt_version,prompt_text=system+"\n\n"+prompt,
                               raw=raw,in_tokens=inp,out_tokens=out,reasoning_tokens=reason,
                               cost=cost,parsed=parsed,status=status)
            calls_this_launch+=1
            note=(f"{sum(len(v) for v in parsed.values())} ideas"
                  if kind!="SITUATION" and parsed else ("two situation fields" if status=="success" else ""))
            print(f"  Run {run_id}: {status}, {note}, input {inp}, output {out} "
                  f"(reasoning {reason}), ${cost:.4f}; total ${spent(db):.4f}")
            # Export after every completed billed call; valuable even if interrupted later.
            export(db,directory)
            if status!="success":
                stopped_reason=("Stopped after validation error. Raw response saved; "
                                "no automatic paid retry on next F5.")
                break

        # A complete run means exactly one successful call for every task.
        # Test every planned task before marking this refresh complete:
        completed_all=all((state:=call_status(db,request_hash(kind,a,b))) is not None
                          and state[0]=="success" for kind,a,b in all_tasks)
        export(db,directory)
        if completed_all:
            atomic_write_text(directory / "COMPLETE.txt", f"Completed at {now()}\n")
            try:
                active=json.loads(ACTIVE_RUN_FILE.read_text(encoding="utf-8"))
                if active.get("folder") == directory.name:
                    ACTIVE_RUN_FILE.unlink()
            except OSError:
                pass
            print(f"\nFULL REFRESH COMPLETE — {expected_total} calls, "
                  f"{db.execute('SELECT COUNT(*) FROM ideas').fetchone()[0]} ideas, "
                  f"estimated ${spent(db):.4f}")
            print("Pressing F5 AGAIN will create a new experiment and make new paid calls.")
        else:
            print("\nEXPERIMENT SAVED BUT NOT COMPLETE.")
            print(stopped_reason or "Some planned calls have not completed.")
            print("Press F5 to resume this experiment; successful calls are not repeated.")
        print(f"\nBrowse: {directory / 'story_idea_reports' / 'README.md'}")
        print(f"JSON:   {directory / 'story_idea_reports' / 'catalog.json'}")
        print(f"SQLite: {directory / 'story_ideas.db'}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
