# pip install openai python-dotenv pandas
# Independent experiment: one LLM call per original-story pair. No embeddings.

import os
import json
from pathlib import Path

import openai
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("CHATGPT_MODEL", "gpt-4.1")

# 0 = Warehouse manager; 1 = Siddhartha Gautama.
SELECTED_QUERY_INDEX = 1


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
    # Original story texts copied unchanged from the existing script.
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
