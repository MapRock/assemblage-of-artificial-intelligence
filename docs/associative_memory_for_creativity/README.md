
# An Associative Memory for Creative Intelligence

This directory contains a two-program experiment in **preserving experiences and the creative associations they inspire**, then recalling that accumulated work when a new predicament arises.

The premise is that an experience from one domain may suggest an approach to a problem in another. A relevant story might already contain an applicable solution, an informative failure, or an observed mechanism. Earlier comparisons between stories may also have produced ideas worth revisiting. Instead of asking a language model to rediscover those connections every time, this experiment stores them with their sources and makes them searchable.

The accompanying research article is titled *An Associative Memory for Creative Intelligence*.

## What the experiment does

There are three operations, implemented in two Python programs:

1. **Generate associations.** Start with six original stories. Ask an LLM for ideas arising directly from each story, and then compare every pair of stories **in both directions** for additional inspirations. Preserve original observations and attempted approaches separately from newly generated possibilities.
2. **Build associative memory.** Store stories, ideas, and provenance relationships in a local SQLite-backed property graph. Give each story two searchable, solution-free descriptions: a concrete situation and a more generalized situation.
3. **Recall experiences and ideas.** For a new predicament, search both embedding representations, reject stories that fail the configured similarity cutoff, and follow the graph to the qualifying stories and their ideas. Present each **original experience and its recorded approaches or outcomes first**, followed by the cached creative inspirations.

The graph uses explicit `Story`, `Idea`, and `Representation` nodes, with `HAS_IDEA`, `HAS_REPRESENTATION`, and `INSPIRED_BY` relationships. It is implemented in SQLite, **not** a Neo4j/Cypher server.

## The six starting stories

| Story | Source experience |
|---|---|
| **Warehouse Manager** | Small mobile drones keep getting crushed by larger, increasingly capable warehouse robots despite improvements in collision prediction. |
| **Star Magnolia** | A dense arrangement of short branches shelters small birds from larger predators. |
| **Ginger Beverage** | A kitchen experiment involving grated ginger, straining, and an unexpectedly strong finished drink. |
| **Thanksgiving Travel** | Leaving days early to avoid traffic creates an exhausting journey; traveling on Thanksgiving Day works better, provided arrival is still timely. |
| **Trophic Cascade** | Robert Paine's sea-star removal experiment reveals how one species can prevent another from dominating an ecosystem. |
| **Data Vault** | A company acquires businesses faster than their data can be fully integrated; a raw vault makes incoming data accessible in the meantime. |

The stories deliberately mix personal experience, a scientific experiment, a consulting experience, and a hypothetical engineering predicament. The goal is not merely to find stories with similar vocabulary, but to explore relationships and potential transfers between different domains.

## Programs

| File | Role |
|---|---|
| [`generate_story_ideas.py`](generate_story_ideas.py) | **Part 1.** Generate the original/direct/inspired idea catalog and the two situation descriptions for each story. |
| [`create_associative_memory.py`](create_associative_memory.py) | **Parts 2 and 3.** Load a completed catalog, create and verify the graph, embed the representations, and run retrieval tests or custom queries. |

### Requirements

- Python 3.10 or later.
- An OpenAI API key and access to the model configured in the scripts.
- Python packages: `openai` and `python-dotenv`. SQLite is provided by Python's standard library.

From this directory:

```bash
python -m pip install -U openai python-dotenv
```

Set `OPENAI_API_KEY` in your environment or create a local `.env` file alongside the scripts:

```dotenv
OPENAI_API_KEY=your_api_key_here
```

**Do not commit `.env`, API keys, or private story content.** Both programs send selected text to the configured API models.

### Step 1 — Generate an idea catalog

```bash
python generate_story_ideas.py
```

The default six-story run schedules **27 model calls**:

- 6 direct idea-generation calls (one per story);
- 6 situation-description calls (one per story);
- 15 pairwise calls (one per unordered pair, exploring both directions in the same call).

The program uses `gpt-6.2-astra` by default. The model and spending controls are editable near the top of the file. Set `DRY_RUN = True` to inspect the planned calls without making API requests. `BUDGET_USD = 2.00` is a **soft estimated-cost guard**, not a guaranteed billing cap; actual charges depend on model pricing and usage.

Each run is saved in its own timestamped folder:

```text
story_idea_experiments/
  run_<timestamp>/
    story_ideas.db
    COMPLETE.txt                     # only after a complete run
    story_idea_reports/
      catalog.json                   # input for the second program
      README.md
      warehouse-manager.md
      star-magnolia.md
      ...
```

An interrupted run can resume its completed calls if the story and prompt settings have not changed. **Once a run is complete, running this program again starts a new experiment and may incur another set of charges.** LLM-generated idea counts and wording can vary between complete runs.

### Step 2 — Build the memory and test recall

```bash
python create_associative_memory.py
```

By default, this program finds the **most recent completed** `catalog.json` from Step 1. It does **not** regenerate the story ideas. You can instead point it to a specific completed catalog by editing:

```python
CATALOG_PATH = "story_idea_experiments/run_<timestamp>/story_idea_reports/catalog.json"
```

The program uses `text-embedding-3-small` with 512 dimensions by default. It validates story/idea/provenance links, checks exact self-retrieval for each indexed story, and runs three diagnostic queries:

1. **Hospital couriers and faster transport carts:** analogous to Warehouse Manager, with potentially relevant protective mechanisms from Star Magnolia and Trophic Cascade.
2. **Research institute with rapidly arriving data:** analogous to Data Vault and its approach to access before full integration.
3. **Arriving early for an annual festival:** analogous to the Thanksgiving Travel experience and its tradeoff between an earlier arrival and a better journey.

Results are written under:

```text
associative_memory/
  associative_memory.db             # property graph and cached embeddings
  graph.json                        # nodes and edges; embedding vectors omitted
  README.md                         # automatically generated run summary
  retrieval_reports/
    small-hospital-couriers-and-faster-transport-carts.md
    small-hospital-couriers-and-faster-transport-carts.json
    research-institute-with-rapidly-arriving-data.md
    research-institute-with-rapidly-arriving-data.json
    arriving-early-for-an-annual-festival.md
    arriving-early-for-an-annual-festival.json
```

The Markdown reports include **the complete story and idea descriptions**, similarity rankings, source details, analogical explanations, and provenance. The JSON reports are available for programmatic inspection.

### Try your own predicament

At the top of `create_associative_memory.py`, set:

```python
RUN_DEMO_QUERIES = False
CUSTOM_QUERY = (
    "Small autonomous couriers carry supplies through hospital corridors "
    "shared with larger, faster transport carts, and collisions keep occurring."
)
CUSTOM_QUERY_GENERALIZED = ""  # leave blank for automatic generalization
```

Then run the file again. Alternatively, set `ASK_FOR_QUERY_AT_END = True` to enter new predicaments interactively.

Describe **the unresolved situation**, not the solution you want the program to find. For a custom query, the program can produce a short generalized version with one additional model call and cache it. The three built-in demonstrations use their *prewritten* generalized queries so they remain comparable with the original experiment.

Unchanged embeddings and successful query generalizations are cached in SQLite. Re-running the recall program does not repeat those calls merely because you pressed F5 again.

## How retrieval is selected and ordered

The initial prototype always returned the top three stories from each embedding view—even when the third match was extremely weak—and then retrieved **every idea** associated with those stories. One hospital-courier query consequently returned **70 of 83 ideas** across five stories. This was recall by quota, not meaningful selectivity.

The revised program uses these editable defaults:

```python
TOP_MATCHES_PER_VIEW = 3
MIN_SIMILARITY_CONCRETE = 0.30
MIN_SIMILARITY_GENERAL = 0.30
STRONG_MATCH_SCORE = 0.60
```

- **Qualification:** A story must pass the minimum cosine-similarity cutoff for at least one of the two representations. The program never pads results with weak matches just to reach three.
- **Story ordering:** Each representation is ranked independently. The program interleaves ranks across the concrete and generalized views, removes duplicate stories, and does not combine their raw cosine values into an invented score.
- **Within a story:** The original narrative and any **recorded** approaches, failures, and outcomes appear first. Generated ideas are presented afterward and remain identified as speculative.
- **Strong matches:** If a qualifying similarity reaches `0.60`, the program shows cached cross-story inspirations before additional direct ideas. This changes **category ordering**; it does *not* independently score or rank every idea against the new query.

For example, in the original 83-idea experiment, the hospital-courier query produced the following generalized-situation similarities:

| Story | Generalized cosine similarity |
|---|---:|
| Warehouse Manager | 0.7678 |
| Trophic Cascade | 0.5102 |
| Star Magnolia | 0.3962 |

All three pass the illustrative `0.30` cutoff. The weaker concrete-view matches for Data Vault (`0.2854`) and Thanksgiving Travel (`0.1501`) do not. These are **recorded scores from that experiment**, not guaranteed outputs of a newly generated catalog.

An important feature is that a recalled Warehouse Manager story brings along ideas originally inspired by *other* experiences—for example, separating a payload's journey from its carrier (Ginger Beverage), examining the trip to a charging station (Thanksgiving Travel), or questioning whether pauses in large-robot traffic might be protective (Trophic Cascade). The source stories themselves do not all need to match the new query to make their **previously generated inspirations** available.

## Reproducing the published experiment

The accompanying article describes a specific completed run with **6 original-story approaches, 20 direct ideas, and 57 pair-inspired ideas: 83 ideas total**, generated in 27 calls.

**The exact 83-idea `catalog.json` is not included in the repository snapshot used to prepare this README.** A fresh run of `generate_story_ideas.py` may produce different ideas, counts, and similarity scores. To reproduce the article's particular catalog and rankings, preserve that completed run's `catalog.json` and explicitly set `CATALOG_PATH` to it. Do not rely on the default “most recent completed run” when reproducing historical results.

## Current scope and limitations

This is a **small research prototype**, not a production semantic search or a validated creative-optimization system.

- The graph and embedding caches work, but cosine similarity does not establish that an analogy is sound or that an intervention will succeed.
- Selecting a story still makes all of its associated ideas available. **Individual ideas are not yet ranked by relevance, novelty, feasibility, or diversity** for the new query.
- A full pairwise exploration grows quadratically with the number of stories; it is practical for six stories, not for millions. Choosing which pairs to explore is a separate research problem.
- Some stories contain observed mechanisms, some contain attempted or successful approaches, and some contain hypothetical predicaments. These must not be conflated.
- The next experiments should compare retrieved inspirations with direct LLM ideation on genuinely new problems, study recall as the library grows, and evaluate deeper relational analogies before considering real-world interventions.

The larger ambition is an **accumulating memory of experience and creative reasoning**: preserve the details nobody knew would become important, retain associations discovered ahead of time, and make them available when future problems evoke something familiar.

## Related work and license

This experiment is part of the [Assemblage of Artificial Intelligence](https://github.com/MapRock/assemblage-of-artificial-intelligence) project and the broader Enterprise Intelligence / Time Molecules / knowledge-graph research described at [eugeneasahara.com](https://eugeneasahara.com/).

Licensed under the repository's [MIT License](../../LICENSE).
