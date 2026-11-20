## Library of Experiences: Searching for Creativity Through Analogy

This directory contains supporting research and experimental materials for *Library of Experiences: Searching for Creativity Through Analogy*, part of my broader work on Enterprise Intelligence and computational creativity.

The central idea is that creativity often emerges from recognizing transferable relationships between seemingly unrelated experiences. Rather than relying exclusively on an LLM's internal knowledge, the proposed architecture maintains a growing library of independently collected stories that can be searched for unexpected analogies.

The experiments explore two complementary techniques: **vector similarity over LLM-generated story abstractions** to identify promising candidates, followed by **direct pairwise LLM reasoning** to examine causal relationships, functional roles, and possible transfers. The longer-term vision connects these experiences to knowledge graphs, Time Molecules, and an Enterprise Knowledge Graph, allowing organizations to preserve and reuse knowledge accumulated through experience.

## Python Requirements and Running the Experiments

Both experiments require **Python 3.10 or later** and access to the OpenAI API.

### Python Dependencies

The experiments use OpenAI models, NumPy, pandas, python-dotenv, and PyYAML.

```bash
python -m pip install "openai==0.28.1" numpy pandas python-dotenv PyYAML
```

**Compatibility note:** The original experimental scripts use the legacy OpenAI Python API (`openai.ChatCompletion.create` and `openai.Embedding.create`), so the OpenAI package is pinned to version 0.28.1. A future update to the current API would remove this restriction.

### API Configuration

Set the `OPENAI_API_KEY` environment variable or provide it in a local `.env` file:

```text
OPENAI_API_KEY=your_api_key
```

Do not commit API keys or `.env` files to GitHub.

The scripts also support the optional `CHATGPT_MODEL` environment variable. Their original defaults are `gpt-4.1-nano` for Experiment 1 and `gpt-4.1` for Experiment 2.

### Story Files

Both experiments share the same external story library:

| File | Purpose |
|---|---|
| `query_stories.yaml` | Query Stories describing problems to investigate |
| `candidate_stories.yaml` | Candidate Stories available for analogy matching |
| `story_loader.py` | Shared loader that reconstructs the original Python story structures |

The YAML files must reside alongside `story_loader.py`. Story texts and titles can be edited independently of the experimental Python code.

The original experimental narratives are also preserved in [Analogy_Experiment_Original_Stories.md](Analogy_Experiment_Original_Stories.md).

### Running the Experiments

From this directory:

**Experiment 1 — Vector similarity and Candidate Story retrieval**

```bash
python two_text_similarity_select_query.py
```

**Experiment 2 — Direct pairwise LLM analogy evaluation**

```bash
python two_text_similarity_pairwise.py
```

Both scripts use `SELECTED_QUERY_INDEX` to select the Query Story (`0` for Warehouse Manager, `1` for Siddhartha Gautama).

The programs currently run independently. Experiment 1 uses LLM-generated abstractions and embeddings to rank candidates, while Experiment 2 evaluates original story pairs without embeddings. Integrating the two into a single retrieval-and-reasoning pipeline is a subsequent development step.

**Note:** Both experiments make billable OpenAI API calls. Results may vary across executions because LLM outputs are not completely deterministic.


### ChatGPT Incident Statement — November 20, 2026

During a technical review of my *Library of Experiences* research, ChatGPT made an unfounded insinuation about the integrity of my publication chronology. An August 19, 2025 WordPress backup confirmed that my two-stage approach—vector-based analogy retrieval followed by direct LLM comparison—was documented before Stanford's May 2026 paper. ChatGPT acknowledged its error, unequivocally retracted the insinuation, and authored a first-person account of the incident.

To be clear, I'm in no way attempting something as crazy as competing with the authors of the Stanford paper. It was just shocking for an entity (human or AI) to insinuate that I may or may not have edited something after a particular date <i>in order to establish precedence incorrectly</i>. **The reason I posted the retraction from ChatGPT is because it thought it necessary to state that.** I don't know why.

[**Read ChatGPT's First-Person Incident Statement**](ChatGPT_First_Person_Incident_Statement_2026-11-20.md)
