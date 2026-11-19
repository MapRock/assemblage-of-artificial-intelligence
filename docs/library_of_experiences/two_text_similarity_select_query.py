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
def summarize_story(story_text):
    # The system + user prompt forces the model to return exactly three fields
    # (problem, desired_outcome, solution) in abstracted, transferable language.
    # Failed attempts are not labeled as solutions; empty string is used when none exists.
    # SBAR: 
    #    Situation corresponds to the problem, 
    #    Background provides context,
    #    Assessment evaluates the desired outcome,
    #    Recommendation aligns with the solution.

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You analyze stories as systems for analogical reasoning. "
                    "Extract three distinct elements: the problem, the desired "
                    "outcome, and any observed solution. "
                    "Abstract domain-specific objects into functional roles. "
                    "Preserve participant relationships, capabilities, constraints, "
                    "and causal mechanisms. Desired outcomes may be implied; "
                    "solutions may be absent or emerge without deliberate design. "
                    "Do not invent events, mechanisms, motives, or solutions. "
                    "Analyze each story independently; do not assume a target analogy."
                )
            },
            {
                "role": "user",
                "content": (
                    "Analyze this story and return a JSON object with "
                    "exactly three string fields: problem, desired_outcome, "
                    "and solution.\n\n"

                    "problem: Describe the vulnerability, conflict, or "
                    "unmet need, from the perspective of the participant "
                    "experiencing it. Preserve the relevant interactions "
                    "and constraints, before any successful solution.\n\n"

                    "desired_outcome: Describe the state of the system "
                    "that would alleviate or resolve the problem. "
                    "The outcome may be explicitly stated or reasonably "
                    "inferred. Describe WHAT success means for the affected "
                    "participants, not HOW it is achieved. "
                    "Do not include mechanisms, interventions, protective "
                    "structures, or other solution-specific details. "
                    "Preserve important constraints and relationships. "
                    "Use generalized, transferable language.\n\n"

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

                    "Keep in mind that the problem, desired outcome, and solution will be used on a similarity comparison, "
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

    for field in ("problem", "solution", "desired_outcome"):
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
    contain the model-generated Problem, Desired Outcome, and Solution,
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
        "### Desired Outcome", query["desired_outcome"] or "[none described]", "", # The outcome for the stories we're matching to have an outcome. Only the problem at hand has a "desired outcome".
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
            f"**Outcome similarity:** {row['Desired Outcome Similarity']:.4f}  ",
            f"**Original similarity:** {row['Original Similarity']:.4f}", "",
            "### Problem", row["Problem"] or "[none described]", "",
            "### Outcome", row["Desired Outcome"] or "[none described]", "",
            "### Solution", row["Solution"] or "[none described]", "",
            "### Original story", row["Original Story"], "",
            "---", ""
        ])
        txt.extend([
            f"RANK {rank}: {story_name}",
            (f"Weighted: {score:.4f} | Problem: {row['Problem Similarity']:.4f} | "
             f"Outcome: {row['Desired Outcome Similarity']:.4f} | "
             f"Original: {row['Original Similarity']:.4f}"), "",
            "PROBLEM:", row["Problem"] or "[none described]", "",
            "DESIRED OUTCOME:", row["Desired Outcome"] or "[none described]", "",
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
    query_stories = [
        (
            "Warehouse manager",
            (
                "A warehouse manager keeps seeing little mobile drones get squashed by much larger robots. "
                "The manager tries improving the little drones so they are smarter and better at predicting "
                "when a collision is about to happen. But the big robots keep becoming faster and smarter "
                "as the warehouse tries to operate more efficiently, and the smaller drones continue to get "
                "crushed. The manager needs inspiration for a way to keep the little drones from being "
                "squashed, without continually trying to outpredict the increasingly capable big robots."
            ),
        ),
        (
            "Siddhartha Gautama",
            (
                "Siddhartha Gautama grew up surrounded by comfort and privilege. His father sought to shield him from the harsher realities of life, providing everything a young prince could desire. Yet Siddhartha grew increasingly troubled when he ventured beyond the palace and encountered an elderly man, a sick person, and a dead body. He realized that neither wealth nor privilege could protect anyone from aging, illness, and death. "
                "Determined to understand why human beings suffer and whether suffering could be overcome, Siddhartha left his comfortable life behind. He studied with spiritual teachers and eventually embraced severe asceticism, depriving himself of food and physical comforts. After years of such practices, he recognized that punishing his body had brought him no closer to the understanding he sought. "
                "He abandoned extreme self-denial, regained his strength, and sat beneath a bodhi tree to meditate. There, according to Buddhist tradition, he came to understand how craving, attachment, and ignorance perpetuate suffering, and how freedom becomes possible when these causes cease. "
                "Rather than returning to a life of indulgence or self-punishment, Siddhartha began teaching a path of ethical conduct, disciplined attention, and wisdom. He spent the remainder of his life helping others understand and practice what he had discovered."
            ),
        ),
    ]

    if not 0 <= SELECTED_QUERY_INDEX < len(query_stories):
        raise IndexError(
            f"SELECTED_QUERY_INDEX must be between 0 and {len(query_stories) - 1}"
        )
    query_title, text1 = query_stories[SELECTED_QUERY_INDEX]
    print(f"\nSelected query [{SELECTED_QUERY_INDEX}]: {query_title}")

    # Each label stays attached to its corresponding story.
    text2 = {
        'Missing cat': (
            "One evening I realized my cat hadn’t come home. At first I assumed he was hiding "
            "somewhere inside, but after checking every room I began searching the neighborhood. I "
            "walked the nearby streets calling his name and shaking a bag of treats, hoping he would "
            "recognize the sound. For two days there was no sign of him. I started leaving small bowls"
            " of food outside and asking neighbors if they had seen a gray cat wandering around. Late "
            "on the second evening I heard a faint meow beneath a hedge, and when I crouched down two "
            "yellow eyes appeared in the shadows."
        ),
        'Ginger beverage': (
            "One afternoon I wondered whether white ginger from the garden could be used to make "
            "ginger ale the way common ginger root is used. I dug up a small piece of the rhizome and "
            "grated it into a pot of water with sugar and lime. As the mixture simmered, the kitchen "
            "filled with a strong floral aroma that was different from the familiar smell of culinary "
            "ginger. After letting the mixture cool, I strained it and added sparkling water to make a"
            " fizzy drink. The result looked promising, but the flavor was much stronger and wilder "
            "than expected."
        ),
        'Papio fishing': (
            "Early one morning I went fishing along a rocky shoreline where small trevally, called "
            "papio, often hunt near the reef. The water was calm and clear, and I could see baitfish "
            "moving in the shallows. I cast a small lure beyond the reef and began reeling it back "
            "slowly, trying to imitate an injured fish. For several casts nothing happened. Then the "
            "line suddenly tightened and the rod bent sharply as a fish pulled away. After a short "
            "fight in the current, a bright silver papio flashed near the surface and I guided it onto"
            " the rocks."
        ),
        'Plumeria': (
            "In 2003 I brought a small plumeria back from Hawaiʻi and started growing it in Twin "
            "Falls, Idaho. For more than twenty years the plant remained healthy and leafy, but it "
            "never produced any flowers. Each summer I kept it outside in a partially shaded spot, and"
            " during the winter I moved it indoors to protect it from the cold. Because the sun in "
            "Twin Falls can be strong and dry, I assumed the plant needed shelter from too much direct"
            " light. Eventually it grew too large for its original location, so I moved it to a place "
            "where it received several hours of direct sunlight each day. To help it handle the heat, "
            "I increased watering and occasionally misted the leaves. That same season the plant "
            "finally bloomed for the first time."
        ),
        'White ginger': (
            "A few years ago I brought back a small white ginger rhizome from Hawaiʻi and began "
            "growing it at my home in Boise. The plant stayed vigorous for more than twenty years, "
            "producing plenty of leaves and looking perfectly healthy, yet it never once produced a "
            "flower. During the warmer months I kept it outside in a shaded area, and each winter I "
            "moved it indoors so it wouldn’t be damaged by freezing temperatures. Because Boise’s "
            "sunlight can be intense and dry, I assumed the plant needed protection from too much "
            "direct sun. Eventually the plant grew too large for its original spot, so I relocated it "
            "to an area that received several hours of direct sunlight each day. To help it cope with "
            "the heat, I watered it more frequently and occasionally misted the leaves. That season, "
            "for the first time, the plant produced a tall flower spike."
        ),
        'Data vault': (
            "A customer of mine was in acquisition mode and looking to expand their business. The rate"
            " of acquisitions outpaced the ability to onboard the data into the data warehouse. I "
            "proposed a data vault strategy. Getting the data into the raw vault meant it was at least"
            " accessible, even though it wasn't fully integrated.Still, a tougher SQL statement at the"
            " user end was better than having no access to the data at all.Eventually, the new data "
            "would be properly onboarded into the integrated data vault."
        ),
        'Star magnolia': (
            "one of the valuable characteristics of star magnolia in my yard is that the thick mesh of"
            " short stubby branches provides excellent protection for juncos, chickadees, and finches."
            " cats, hawks, dogs, cannot easily pentrate the thicket. it's a great retreat from our "
            "nearby bird feeder."
        ),
        'Furniture Maker': (
            "A carpenter spent decades building beautiful furniture. He took great pride in his craftsmanship and reputation. But as he grew older, his hands became less steady, younger carpenters adopted unfamiliar techniques, and customers began favoring different styles. He grew increasingly frustrated, working harder to preserve the life and reputation he had known."
            " One evening, after ruining a piece of wood he had spent days carving, he realized that much of his unhappiness came not from his aging hands or changing customers, but from his insistence that things remain as they once were."
            " He wondered whether he could continue enjoying his craft without needing every piece to be perfect or every customer to admire his work."
            " Over the following months, he practiced paying closer attention to his thoughts, speaking more thoughtfully to his apprentices, acting with patience, and approaching each day's work with care rather than expectation. His hands continued aging, and customers' tastes continued changing, but he gradually found peace in his workshop again."
        ),
        'Marcus Aurellius': (
            "Marcus Aurelius, the Roman emperor and Stoic philosopher, faced numerous challenges during his reign, including wars, plagues, and political intrigue. Despite these external pressures, he sought to maintain inner tranquility and moral integrity. He reflected on the impermanence of life, the importance of rational thought, and the value of virtue over external success."
            " In his personal writings, later compiled as 'Meditations,' he emphasized self-discipline, the acceptance of fate, and the cultivation of wisdom and compassion. Through these practices, he aimed to navigate the complexities of leadership while remaining true to his philosophical principles."
        ),
        'Time Molecules': (
            "In an enterprise, there data is still fragmented and siloed, making it difficult to gain comprehensive insights and make informed decisions."
            "There could be hundreds of data sources, all involved with the activities, but only a fraction of them are effectively integrated and analyzed to provide actionable insights."
            "This fragmentation hinders the organization's ability to make data-driven decisions and respond effectively to changing business conditions."
            "However, the dimenension of time is common to all data sources, providing a potential axis for integration and analysis."
            "There's much we can do with time such as tracking trends, identifying patterns, and correlating events across different data sources."
        ),
        'Trophic Cascade': (
            "In 1963, ecologist Robert Paine began studying a rocky stretch of Washington's Pacific coast. "
            "The shoreline was home to mussels, barnacles, limpets, sea stars, and numerous other creatures "
            "competing for space on the rocks. Paine noticed that ochre sea stars regularly preyed on mussels "
            "and wondered what would happen to the other organisms if the sea stars disappeared. "
            "He began removing sea stars from a small section of shoreline while leaving nearby areas undisturbed. "
            "Over the following months, mussels spread rapidly across the cleared rocks. "
            "Without the sea stars feeding on them, the mussels increasingly occupied space that other species needed. "
            "Barnacles and other organisms were crowded out, and the number of species occupying the experimental "
            "area fell from fifteen to eight. The nearby undisturbed shoreline remained more varied. "
            "Paine discovered that the sea stars, despite eating other animals, had been preventing one "
            "competitor from dominating the community."
        )
    }




    # Process the selected query story once
    query = summarize_story(text1)
    if not query["problem"].strip() or not query["desired_outcome"].strip():
        raise ValueError("The query story must contain a problem and desired outcome")

    query_problem_emb = embed_text(query["problem"])
    query_goal_emb = embed_text(query["desired_outcome"])
    query_original_emb = embed_text(text1)

    results = []



    for story_label, t2 in text2.items():

        candidate = summarize_story(t2)

        candidate_problem_emb = embed_text(candidate["problem"])
        candidate_original_emb = embed_text(t2)

        # Compare the problems
        problem_similarity = cosine_similarity(
            query_problem_emb,
            candidate_problem_emb
        )

        # Compare desired outcomes, NOT the target outcome to the source solution.
        # The source's solution remains available for later analogical transfer.
        if candidate["desired_outcome"].strip():
            candidate_goal_emb = embed_text(candidate["desired_outcome"])
            desired_outcome_similarity = cosine_similarity(
                query_goal_emb,
                candidate_goal_emb
            )
        else:
            desired_outcome_similarity = 0.0

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
            + OUTCOME_WEIGHT * desired_outcome_similarity
            + ORIGINAL_WEIGHT * original_similarity
        )

        results.append({
            "Story": story_label,
            "Problem Similarity": problem_similarity,
            "Desired Outcome Similarity": desired_outcome_similarity,
            "Original Similarity": original_similarity,
            "Weighted Similarity": similarity,
            "Problem": candidate["problem"],
            "Solution": candidate["solution"],
            "Desired Outcome": candidate["desired_outcome"],
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
            "Desired Outcome Similarity",
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