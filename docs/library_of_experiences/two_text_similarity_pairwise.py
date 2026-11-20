# pip install openai python-dotenv pandas
# Independent experiment: one LLM call per original-story pair. No embeddings.

import os
import json
from pathlib import Path

import openai
from dotenv import load_dotenv
import pandas as pd
from story_loader import load_query_stories, load_candidate_stories

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("CHATGPT_MODEL", "gpt-4.1")

# 0 = Warehouse manager; 1 = Siddhartha Gautama.
SELECTED_QUERY_INDEX = 0


def compare_stories(query_text, candidate_text):
    """Evaluate one candidate against the query, using ONLY their original stories."""
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You evaluate analogies between two independent stories. "
                    "The QUERY has a problem and a desired outcome. "
                    "The CANDIDATE may contain a mechanism, intervention, or arrangement "
                    "that suggests an approach to the query's problem. "
                    "Look for transferable causal relationships and functional roles, "
                    "not shared vocabulary, setting, or broad themes. "
                    "Respect who is helped, who is harmed, and who acts on whom; "
                    "do not treat reversed roles as equivalent. "
                    "A candidate may be a good analogy even across completely different domains. "
                    "Do not invent events or claim that a speculative application has been tested. "
                    "Judge each candidate independently, without assuming a winner."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Compare these TWO ORIGINAL STORIES for analogical transfer.\n\n"
                    "QUERY STORY (the problem we want to solve):\n"
                    + query_text
                    + "\n\nCANDIDATE STORY (a possible source of inspiration):\n"
                    + candidate_text
                    + "\n\nEvaluate whether the candidate offers a concrete, transferable "
                    "approach to the query's problem and desired outcome. "
                    "Pay particular attention to the relationships among participants "
                    "and what actually caused the candidate's result. "
                    "Do not reward a candidate merely because it contains danger, "
                    "competition, or coexistence; explain how its mechanism could transfer. "
                    "If its roles or objectives are inverted, penalize the score. "
                    "If no credible mechanism transfers, give a low score.\n\n"
                    "Give an analogy_quality score from 0 to 100: "
                    "0 = no meaningful analogy; 25 = mostly superficial; "
                    "50 = partial but limited transfer; 75 = strong functional/causal analogy; "
                    "100 = exceptionally direct, credible transfer.\n\n"
                    "Return ONLY a JSON object with four fields:\n"
                    "analogy_quality: integer 0-100;\n"
                    "mapping: short explanation of corresponding roles and relationships;\n"
                    "transfer: concrete idea the candidate could suggest for the query;\n"
                    "limitation: most important mismatch or obstacle (empty if none)."
                ),
            },
        ],
        temperature=0.2,
        max_tokens=650,
    )

    content = response["choices"][0]["message"]["content"].strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0]
    result = json.loads(content)
    score = result["analogy_quality"]
    if type(score) is not int or not 0 <= score <= 100:
        raise ValueError(f"Invalid analogy_quality: {score!r}")
    for field in ("mapping", "transfer", "limitation"):
        if not isinstance(result.get(field), str):
            raise ValueError(f"Missing or invalid field: {field}")
    return result


def main():
    # Original story texts loaded unchanged from the YAML files.
    query_stories = load_query_stories()

    text2 = load_candidate_stories()

    if not 0 <= SELECTED_QUERY_INDEX < len(query_stories):
        raise IndexError("Invalid SELECTED_QUERY_INDEX")
    query_title, query_text = query_stories[SELECTED_QUERY_INDEX]
    print(f"\nSelected query [{SELECTED_QUERY_INDEX}]: {query_title}")
    print(f"Model: {MODEL} | Pairwise comparisons: {len(text2)}\n")

    results = []
    for candidate_title, candidate_text in text2.items():
        assessment = compare_stories(query_text, candidate_text)
        print(f"{candidate_title}: {assessment['analogy_quality']}/100", flush=True)
        results.append({
            "Story": candidate_title,
            "Analogy Quality": assessment["analogy_quality"],
            "Mapping": assessment["mapping"],
            "Transfer": assessment["transfer"],
            "Limitation": assessment["limitation"],
        })

    df = pd.DataFrame(results).sort_values(
        "Analogy Quality", ascending=False, kind="stable"
    ).reset_index(drop=True)
    df.index += 1
    df.index.name = "Rank"

    print("\n--- Ranked Analogies ---\n")
    print(df[["Story", "Analogy Quality"]].to_string())
    print(f"\nBest candidate: {df.iloc[0]['Story']}")
    print(f"Suggested transfer: {df.iloc[0]['Transfer']}")

    csv_path = Path("story_pairwise_results.csv")
    md_path = Path("story_pairwise_results.md")
    df.to_csv(csv_path, index=True, encoding="utf-8-sig")

    lines = [
        "# Pairwise Analogy Comparison", "",
        f"Query: {query_title}", "",
        f"Model: `{MODEL}`", "",
        "One independent LLM evaluation per candidate; original stories only.", "",
    ]
    for rank, (_, row) in enumerate(df.iterrows(), start=1):
        lines += [
            f"## {rank}. {row['Story']} — {row['Analogy Quality']}/100", "",
            f"**Mapping:** {row['Mapping']}", "",
            f"**Transfer:** {row['Transfer']}", "",
            f"**Limitation:** {row['Limitation'] or '[none identified]'}", "",
        ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved: {csv_path} and {md_path}")


if __name__ == "__main__":
    main()
