# pip install openai numpy python-dotenv

import os

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
PROMPT ="I'm having {problems} with my {plant} plant thriving outdoors in {place}. I've had it for a long time, it grows, but never {blooms}. We tried everything we could think of."

p_tuples = [
    ("problems","kahili ginger", "Boise, ID", "blooms"),
    ("problems","kahili ginger", "Twin Falls, ID", "blooms"),
    ("problems","kahili ginger", "Phoenix, AZ", "blooms"),
    ("problems","kahili ginger", "Yakutsk, Siberia", "blooms"),
    ("problems","white ginger", "Phoenix, AZ", "blooms"),
    ("problems","white ginger", "Boise, ID", "blooms"),
    ("problems","white ginger", "Twin Falls, ID", "blooms"),
    ("problems","white ginger", "Yakutsk, Siberia", "blooms"),
    ("problems","heliconia", "Phoenix, AZ", "blooms"),
    ("problems","heliconia", "Boise, ID", "blooms"),
    ("problems","heliconia", "Twin Falls, ID", "blooms"),
    ("problems","heliconia", "Yakutsk, Siberia", "blooms"),
    ("fun","sequioa", "my mega yacht in the south of France", "falls over"),

]

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

    summary_emb = embed_text(PROMPT)
    pattern1 = summarize_story(PROMPT)
    pattern1_emb = embed_text(pattern1)

    for tup in p_tuples:
        t2 = PROMPT.format(problems=tup[0], plant=tup[1], place=tup[2], blooms=tup[3])


        prompt_emb = embed_text(t2)
        pattern2 = summarize_story(t2)
        pattern2_emb = embed_text(pattern2)
        print(pattern1)
        print(pattern2)

        similarity = 0.7 * cosine_similarity(pattern1_emb, pattern2_emb)  + 0.3 * cosine_similarity(prompt_emb, summary_emb)

        print("\n--- Similarity Score ---\n")
        print(similarity)



if __name__ == "__main__":
    main()