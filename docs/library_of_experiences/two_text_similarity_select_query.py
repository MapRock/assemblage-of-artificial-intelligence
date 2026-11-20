# pip install openai numpy python-dotenv pandas

# DISCLAIMER: This script uses OpenAI APIs (chat completions + embeddings) to extract
# structured abstractions from stories and rank them by weighted cosine similarity.
# It is intended for exploratory analogical reasoning research. Results depend on
# the model, temperature, and the quality of the extracted summaries. Do not treat
# rankings as objective truth. API costs apply. Stories are processed independently;
# no cross-story assumptions are made during summarization.

import os
import json
from pathlib import Path

import numpy as np
import openai
from dotenv import load_dotenv
import pandas as pd
from story_loader import load_query_stories, load_candidate_stories

load_dotenv()

# ----------------------------
# Config
# ----------------------------
MODEL = os.getenv("CHATGPT_MODEL", "gpt-4.1-nano")
MAX_TOKENS = int(os.getenv("CHATGPT_MAX_RESPONSE_TOKENS", "220"))

openai.api_key = os.getenv("OPENAI_API_KEY")

EMBED_MODEL = "text-embedding-3-small"

# Change this one number to choose the query story from query_stories.
SELECTED_QUERY_INDEX = 0

# Retrieval: compare like with like. Candidate solutions are retained for
# later inspection/analogical transfer, not mixed into cosine scoring.
#
# WEIGHT COMMENTARY:
# The ranking deliberately emphasizes the abstracted "problem" and "desired_outcome"
# over the raw original text. Problem (0.45) and Desired Outcome (0.50) together
# account for 95% of the score; the original narrative similarity contributes only
# 5%. This reflects the goal of analogical retrieval: two stories can be usefully
# similar even when their surface wording, domain, or characters differ, provided
# the underlying problem structure and the desired end-state align. The tiny original
# weight acts as a weak tie-breaker or sanity check rather than a primary signal.
# If you want surface-level lexical similarity to matter more, raise ORIGINAL_WEIGHT
# and reduce the other two accordingly (they should still sum to 1.0).
PROBLEM_WEIGHT = 0.40
OUTCOME_WEIGHT = 0.50
ORIGINAL_WEIGHT = 0.10

# ----------------------------
# Math helper
# ----------------------------
def cosine_similarity(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0


# ----------------------------
# Summarize story
# ----------------------------
def summarize_story(story_text, is_query=False):
    # The query asks what SHOULD happen (desired_outcome).
    # Candidate stories report what DID happen (outcome).
    # Both retain their problem and any observed solution.
    outcome_field = "desired_outcome" if is_query else "outcome"
    if is_query:
        outcome_instruction = (
            "desired_outcome: Describe the state of the system "
            "that would alleviate or resolve the problem. "
            "The outcome may be explicitly stated or reasonably "
            "inferred. Describe WHAT success means for the affected "
            "participants, not HOW it is achieved. "
            "Do not include mechanisms, interventions, protective "
            "structures, or other solution-specific details. "
            "Preserve important constraints and relationships. "
            "Use generalized, transferable language.\n\n"
        )
    else:
        outcome_instruction = (
            "outcome: Describe WHAT ACTUALLY HAPPENED in this story, "
            "not what anyone wanted or hoped would happen. "
            "Include the observed consequences for affected participants, "
            "including unsuccessful or unintended consequences if present. "
            "Do not describe HOW the result was produced; put mechanisms "
            "in solution instead. Do not invent an outcome. "
            "If none is observed, use an empty string. "
            "Preserve important constraints and relationships. "
            "Use generalized, transferable language.\n\n"
        )

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You analyze stories as systems for analogical reasoning. "
                    "Extract three distinct elements: the problem, the "
                    + ("desired " if is_query else "observed ")
                    + "outcome, and any observed solution. "
                    "Abstract domain-specific objects into functional roles. "
                    "Preserve participant relationships, capabilities, constraints, "
                    "and causal mechanisms. "
                    + ("Desired outcomes may be implied; " if is_query else "Report actual outcomes, not hypothetical desired outcomes; ")
                    + "solutions may be absent or emerge without deliberate design. "
                    "Do not invent events, mechanisms, motives, or solutions. "
                    "Analyze each story independently; do not assume a target analogy."
                )
            },
            {
                "role": "user",
                "content": (
                    "Analyze this story and return a JSON object with "
                    "exactly three string fields: problem, " + outcome_field + ", "
                    "and solution.\n\n"

                    "problem: Describe the vulnerability, conflict, or "
                    "unmet need, from the perspective of the participant "
                    "experiencing it. Preserve the relevant interactions "
                    "and constraints, before any successful solution.\n\n"

                    + outcome_instruction +

                    "solution: Describe an OBSERVED mechanism, arrangement, "
                    "behavior, or intervention that addresses the problem, "
                    "whether intentionally designed or naturally occurring. "
                    "Explain HOW it works, including unusual physical, "
                    "structural, spatial, temporal, or behavioral relations. "
                    "If the story contains no successful solution, use an "
                    "empty string. Do not label failed attempts as solutions.\n\n"

                    "Use abstracted, transferable language, especially for nouns. Preserve causal "
                    "relationships, not just abstract nouns. Distinguish "
                    "observations from inferences and do not invent solutions.\n\n"

                    "Keep in mind that the problem, "
                    + ("desired outcome" if is_query else "observed outcome")
                    + ", and solution will be used on a similarity comparison, "
                    "so focus on capturing the essential elements so that topics across domains have a chance to map.\n\n"

                    "Return only valid JSON, without Markdown.\n\n"
                    "Story:\n" + story_text
                )
            }
        ],
        max_tokens=max(500, MAX_TOKENS),
        temperature=0.2
    )

    content = response["choices"][0]["message"]["content"].strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0]

    result = json.loads(content)

    for field in ("problem", "solution", outcome_field):
        if field not in result or not isinstance(result[field], str):
            raise ValueError(f"Missing or invalid field: {field}")

    return result

# ----------------------------
# Embeddings
# ----------------------------
def embed_text(text):

    response = openai.Embedding.create(
        model=EMBED_MODEL,
        input=text
    )

    return response["data"][0]["embedding"]


# ----------------------------
# Readable reports (Markdown and plain text)
# ----------------------------
def write_summary_reports(query_title, query, query_text, df, weights):
    """Write the query and all candidate summaries in ranked order.

    The resulting Markdown is readable directly on GitHub. Both reports
    contain the model-generated Problem, query Desired Outcome, candidate Outcome, and Solution,
    along with the original story for checking the abstractions.
    """
    md = [
        "# Story Similarity: Extracted Summaries", "",
        f"Model: `{MODEL}` | Embedding model: `{EMBED_MODEL}`", "",
        ("Similarity weights: "
         f"Problem {weights[0]:.0%}, Desired outcome {weights[1]:.0%}, "
         f"Original text {weights[2]:.0%}"), "",
        f"## Query: {query_title}", "",
        "### Problem", query["problem"] or "[none described]", "",
        "### Desired outcome", query["desired_outcome"] or "[none described]", "",
        "### Solution", query["solution"] or "[none described]", "",
        "### Original story", query_text, "",
        "---", ""
    ]
    txt = [
        "STORY SIMILARITY: EXTRACTED SUMMARIES", "",
        f"Model: {MODEL} | Embedding model: {EMBED_MODEL}",
        ("Weights: "
         f"Problem {weights[0]:.0%}, Desired outcome {weights[1]:.0%}, "
         f"Original text {weights[2]:.0%}"), "",
        f"QUERY: {query_title}", "",
        "PROBLEM:", query["problem"] or "[none described]", "",
        "DESIRED OUTCOME:", query["desired_outcome"] or "[none described]", "",
        "SOLUTION:", query["solution"] or "[none described]", "",
        "ORIGINAL STORY:", query_text, "",
        "=" * 72, ""
    ]

    for rank, (_, row) in enumerate(df.iterrows(), start=1):
        story_name = str(row["Story"])
        score = float(row["Weighted Similarity"])
        md.extend([
            f"## Rank {rank}: {story_name}", "",
            f"**Weighted similarity:** {score:.4f}  ",
            f"**Problem similarity:** {row['Problem Similarity']:.4f}  ",
            f"**Desired vs. observed outcome similarity:** {row['Outcome Similarity']:.4f}  ",
            f"**Original similarity:** {row['Original Similarity']:.4f}", "",
            "### Problem", row["Problem"] or "[none described]", "",
            "### Observed outcome", row["Outcome"] or "[none described]", "",
            "### Solution", row["Solution"] or "[none described]", "",
            "### Original story", row["Original Story"], "",
            "---", ""
        ])
        txt.extend([
            f"RANK {rank}: {story_name}",
            (f"Weighted: {score:.4f} | Problem: {row['Problem Similarity']:.4f} | "
             f"Outcome: {row['Outcome Similarity']:.4f} | "
             f"Original: {row['Original Similarity']:.4f}"), "",
            "PROBLEM:", row["Problem"] or "[none described]", "",
            "OBSERVED OUTCOME:", row["Outcome"] or "[none described]", "",
            "SOLUTION:", row["Solution"] or "[none described]", "",
            "ORIGINAL STORY:", row["Original Story"], "",
            "=" * 72, ""
        ])

    markdown_path = Path("story_similarity_summaries.md")
    text_path = Path("story_similarity_summaries.txt")
    markdown_path.write_text("\n".join(md), encoding="utf-8")
    text_path.write_text("\n".join(txt), encoding="utf-8")
    return markdown_path, text_path


# ----------------------------
# Main
# ----------------------------
def main():


    # Choose the active query by its zero-based index.
    # 0 = Warehouse manager; 1 = Siddhartha Gautama.
    query_stories = load_query_stories()

    if not 0 <= SELECTED_QUERY_INDEX < len(query_stories):
        raise IndexError(
            f"SELECTED_QUERY_INDEX must be between 0 and {len(query_stories) - 1}"
        )
    query_title, text1 = query_stories[SELECTED_QUERY_INDEX]
    print(f"\nSelected query [{SELECTED_QUERY_INDEX}]: {query_title}")

    # Each label stays attached to its corresponding story.
    text2 = load_candidate_stories()




    # Process the selected query story once
    query = summarize_story(text1, is_query=True)
    if not query["problem"].strip() or not query["desired_outcome"].strip():
        raise ValueError("The query story must contain a problem and desired outcome")

    query_problem_emb = embed_text(query["problem"])
    query_goal_emb = embed_text(query["desired_outcome"])
    query_original_emb = embed_text(text1)

    results = []



    for story_label, t2 in text2.items():

        candidate = summarize_story(t2, is_query=False)

        candidate_problem_emb = embed_text(candidate["problem"])
        candidate_original_emb = embed_text(t2)

        # Compare the problems
        problem_similarity = cosine_similarity(
            query_problem_emb,
            candidate_problem_emb
        )

        # Compare the query's DESIRED outcome with the candidate's OBSERVED outcome.
        # The source's solution remains available for later analogical transfer.
        if candidate["outcome"].strip():
            candidate_goal_emb = embed_text(candidate["outcome"])
            outcome_similarity = cosine_similarity(
                query_goal_emb,
                candidate_goal_emb
            )
        else:
            outcome_similarity = 0.0

        # Compare original narratives
        original_similarity = cosine_similarity(
            query_original_emb,
            candidate_original_emb
        )

        # Weighted score — problem and outcome dominate (95% combined).
        # Original text is only a minor factor so that structural analogy can surface
        # even when surface language differs substantially.
        similarity = (
            PROBLEM_WEIGHT * problem_similarity
            + OUTCOME_WEIGHT * outcome_similarity
            + ORIGINAL_WEIGHT * original_similarity
        )

        results.append({
            "Story": story_label,
            "Problem Similarity": problem_similarity,
            "Outcome Similarity": outcome_similarity,
            "Original Similarity": original_similarity,
            "Weighted Similarity": similarity,
            "Problem": candidate["problem"],
            "Solution": candidate["solution"],
            "Outcome": candidate["outcome"],
            "Original Story": t2
        })

    df = pd.DataFrame(results)

    df = df.sort_values(
        "Weighted Similarity",
        ascending=False
    ).reset_index(drop=True)

    df.index += 1
    df.index.name = "Rank"

    print(f"\n--- {query_title}: Problem ---")
    print(query["problem"])

    print(f"\n--- {query_title}: Desired Outcome ---")
    print(query["desired_outcome"])

    print(f"\n--- {query_title}: Solution (empty means unresolved) ---")
    print(query["solution"] or "[none described]")

    print("\n--- Similarity Rankings ---\n")

    print(
        df[[
            "Story",
            "Problem Similarity",
            "Outcome Similarity",
            "Original Similarity",
            "Weighted Similarity"
        ]].to_string(float_format=lambda x: f"{x:.4f}")
    )

    # Full CSV includes all three extracted fields and the original text.
    df.to_csv("story_similarity_results.csv", index=True, encoding="utf-8-sig")

    markdown_path, text_path = write_summary_reports(
        query_title, query, text1, df,
        (PROBLEM_WEIGHT, OUTCOME_WEIGHT, ORIGINAL_WEIGHT)
    )
    print(f"\nSaved CSV: story_similarity_results.csv")
    print(f"Saved readable summaries: {markdown_path} and {text_path}")

if __name__ == "__main__":
    main()