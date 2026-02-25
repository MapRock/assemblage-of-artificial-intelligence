# pip install openai numpy python-dotenv

import json
import os
import time
from pathlib import Path
import numpy as np
import openai
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# Config
# ----------------------------
MODEL = os.getenv("CHATGPT_MODEL", "gpt-4.1-nano")
MAX_TOKENS = int(os.getenv("CHATGPT_MAX_RESPONSE_TOKENS", "220"))

openai.api_key = os.getenv("OPENAI_API_KEY")

EMBED_MODEL = "text-embedding-3-small"

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

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a concise summarizer."},
            {
                "role": "user",
                "content": 
                    "Summarize the following story into a one sentence,abstracting the nouns. \n\n"
                    + story_text
                ,
            },
        ],
        max_tokens=MAX_TOKENS,
        temperature=0.2,
    )

    return response["choices"][0]["message"]["content"].strip()


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
# Main
# ----------------------------
def main():


    text1 = (
        "In 2003 I brought home a small kahili ginger root from Hawaiʻi and began growing it in Boise. "
        "For more than twenty years the plant looked healthy and produced plenty of leaves, but it never "
        "formed a flower. Each summer I placed it outside in partial shade and brought it indoors during "
        "the winter to protect it from the cold. I assumed Boise’s intense sun would harm a tropical plant, "
        "so I kept it sheltered. Eventually the plant grew too large for that spot, and I moved it into an "
        "area with several hours of direct sunlight. I compensated by watering and misting the leaves more "
        "often. That same season the plant finally produced its first flower spike."
    )

    text2 = [
        (
            "One evening I realized my cat hadn’t come home. At first I assumed he was hiding somewhere "
            "inside, but after checking every room I began searching the neighborhood. I walked the nearby "
            "streets calling his name and shaking a bag of treats, hoping he would recognize the sound. "
            "For two days there was no sign of him. I started leaving small bowls of food outside and asking "
            "neighbors if they had seen a gray cat wandering around. Late on the second evening I heard a "
            "faint meow beneath a hedge, and when I crouched down two yellow eyes appeared in the shadows."
        ),
        (
            "One afternoon I wondered whether white ginger from the garden could be used to make ginger ale "
            "the way common ginger root is used. I dug up a small piece of the rhizome and grated it into a "
            "pot of water with sugar and lime. As the mixture simmered, the kitchen filled with a strong "
            "floral aroma that was different from the familiar smell of culinary ginger. After letting the "
            "mixture cool, I strained it and added sparkling water to make a fizzy drink. The result looked "
            "promising, but the flavor was much stronger and wilder than expected."
        ),
        (
            "Early one morning I went fishing along a rocky shoreline where small trevally, called papio, "
            "often hunt near the reef. The water was calm and clear, and I could see baitfish moving in the "
            "shallows. I cast a small lure beyond the reef and began reeling it back slowly, trying to imitate "
            "an injured fish. For several casts nothing happened. Then the line suddenly tightened and the rod "
            "bent sharply as a fish pulled away. After a short fight in the current, a bright silver papio "
            "flashed near the surface and I guided it onto the rocks."
        ),
        (
            "In 2003 I brought a small plumeria back from Hawaiʻi and started growing it in Twin Falls, Idaho. For more than twenty years the plant remained healthy and leafy, but it never produced any flowers. Each summer I kept it outside in a partially shaded spot, and during the winter I moved it indoors to protect it from the cold. Because the sun in Twin Falls can be strong and dry, I assumed the plant needed shelter from too much direct light. Eventually it grew too large for its original location, so I moved it to a place where it received several hours of direct sunlight each day. To help it handle the heat, I increased watering and occasionally misted the leaves. That same season the plant finally bloomed for the first time."
        ), 
        (
            "A few years ago I brought back a small white ginger rhizome from Hawaiʻi and began growing it at my home in Boise. The plant stayed vigorous for more than twenty years, producing plenty of leaves and looking perfectly healthy, yet it never once produced a flower. During the warmer months I kept it outside in a shaded area, and each winter I moved it indoors so it wouldn’t be damaged by freezing temperatures. Because Boise’s sunlight can be intense and dry, I assumed the plant needed protection from too much direct sun. Eventually the plant grew too large for its original spot, so I relocated it to an area that received several hours of direct sunlight each day. To help it cope with the heat, I watered it more frequently and occasionally misted the leaves. That season, for the first time, the plant produced a tall flower spike."
        ) 
    ]  
    for t2 in text2:
        print(t2)


        summary_emb = embed_text(text1)
        prompt_emb = embed_text(t2)

        pattern1 = summarize_story(text1)
        pattern2 = summarize_story(t2)
        print(pattern1)
        print(pattern2)
        pattern1_emb = embed_text(pattern1)
        pattern2_emb = embed_text(pattern2)

        similarity = 0.7 * cosine_similarity(pattern1_emb, pattern2_emb)  + 0.3 * cosine_similarity(prompt_emb, summary_emb)

        print("\n--- Similarity Score ---\n")
        print(similarity)



if __name__ == "__main__":
    main()