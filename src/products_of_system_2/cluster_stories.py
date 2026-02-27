import re
import requests
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

import os

import openai
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# Config
# ----------------------------
MAX_TOKENS = int(os.getenv("CHATGPT_MAX_RESPONSE_TOKENS", "220"))

openai.api_key = os.getenv("OPENAI_API_KEY")

FILE_URL = "https://raw.githubusercontent.com/MapRock/assemblage-of-artificial-intelligence/main/src/products_of_system_2/example_stories.txt"

EMBED_MODEL = "text-embedding-3-large"
SUMMARY_MODEL = "gpt-4.1-mini"

SUMMARY_WEIGHT = 0.7
TEXT_WEIGHT = 0.3

def summarize_story(story_text):

    response = openai.ChatCompletion.create(
        model=SUMMARY_MODEL,
        messages=[
            {"role": "system", "content": "You are a concise summarizer."},
            {
                "role": "user",
                "content":
                    "Summarize the following story into a one sentence, Summarize the causal pattern of the story. Ignore the domain and objects. Describe the underlying situation and outcome. \n\n"
                    + story_text
                ,
            },
        ],
        max_tokens=MAX_TOKENS,
        temperature=0.2,
    )

    return response["choices"][0]["message"]["content"].strip()

def embed_text(text):

    response = openai.Embedding.create(
        model=EMBED_MODEL,
        input=text
    )

    return response["data"][0]["embedding"]

if __name__ == "__main__":

    # -----------------------------
    # Step 1 — Download file
    # -----------------------------
    print("\nSTEP 1 — Downloading stories file\n")

    response = requests.get(FILE_URL)
    response.raise_for_status()

    text = response.text

    print("Downloaded file length:", len(text))


    # -----------------------------
    # Step 2 — Extract stories
    # -----------------------------
    print("\nSTEP 2 — Extracting stories\n")

    pattern = r"(Story\s+\d+):\s*(.*?)\s*<end>"

    matches = re.findall(pattern, text, re.DOTALL)
    print(text)

    stories = []

    for label, story in matches:
        story = story.strip()
        story = " ".join(story.split())  # normalize whitespace

        stories.append({
            "label": label,
            "text": story
        })

    print("Stories extracted:", len(stories))

    for s in stories:
        print(s["label"], "length:", len(s["text"]))


    # -----------------------------
    # Step 3 — Create summaries
    # -----------------------------
    print("\nSTEP 3 — Generating generalized summaries\n")


    for story in stories:
        print("\nSummarizing:", story["label"])
        summary = summarize_story(story["text"])
        story["summary"] = summary
        print("Summary:", summary)


    # -----------------------------
    # Step 4 — Create embeddings
    # -----------------------------
    print("\nSTEP 4 — Creating embeddings\n")


    summary_embeddings = []
    text_embeddings = []

    for story in stories:

        print("Embedding summary:", story["label"])
        s_vec = embed_text(story["summary"])
        summary_embeddings.append(s_vec)

        print("Embedding full text:", story["label"])
        t_vec = embed_text(story["text"])
        text_embeddings.append(t_vec)

    summary_embeddings = np.array(summary_embeddings)
    text_embeddings = np.array(text_embeddings)

    combined_embeddings = (
        SUMMARY_WEIGHT * summary_embeddings +
        TEXT_WEIGHT * text_embeddings
    )


    # -----------------------------
    # Step 5 — Clustering
    # -----------------------------
    print("\nSTEP 5 — Clustering stories\n")

    NUM_CLUSTERS = min(3, len(stories))

    kmeans = KMeans(n_clusters=NUM_CLUSTERS, random_state=0)
    clusters = kmeans.fit_predict(combined_embeddings)


    # -----------------------------
    # Step 5b — Distance from centroid
    # -----------------------------
    print("\nSTEP 5b — Distance from centroid\n")

    centroids = kmeans.cluster_centers_  # shape: (k, dim)

    # For each point i, use the centroid of its assigned cluster clusters[i]
    distances = np.linalg.norm(
        combined_embeddings - centroids[clusters],
        axis=1
    )

    # store + print
    for i, story in enumerate(stories):
        story["cluster"] = int(clusters[i])
        story["dist"] = float(distances[i])
        print(f"{story['label']} -> cluster {clusters[i]}, dist={distances[i]:.4f}")


    # Optional: print cluster radius (tightness)
    print("\nSTEP 5c — Cluster radius (max distance in each cluster)\n")

    for cid in range(NUM_CLUSTERS):
        member_dists = [s["dist"] for s in stories if s["cluster"] == cid]
        if member_dists:
            print(f"Cluster {cid} radius = {max(member_dists):.4f}")
        else:
            print(f"Cluster {cid} radius = (no members)")


    # -----------------------------
    # Step 6 — Show clusters
    # -----------------------------
    print("\nSTEP 6 — Cluster Results\n")

    cluster_map = {}

    for story in stories:
        cluster_map.setdefault(story["cluster"], []).append(story)

    for cluster_id, group in cluster_map.items():

        print("\n==============================")
        print("CLUSTER", cluster_id)
        print("==============================")

        # Sort by distance: prototype first
        for story in sorted(group, key=lambda s: s["dist"]):
            print("\n", story["label"])
            print("Distance:", f"{story['dist']:.4f}")
            print("Summary:", story["summary"])
            print("Text:", story["text"][:200], "...")


    # -----------------------------
    # Step 7 — Similarity matrix
    # -----------------------------
    print("\nSTEP 7 — Story similarity (combined embeddings)\n")

    sim = cosine_similarity(combined_embeddings)

    for i, s1 in enumerate(stories):
        for j, s2 in enumerate(stories):

            if i < j:
                print(
                    f"{s1['label']} vs {s2['label']} = {sim[i][j]:.3f}"
                )


    # -----------------------------
    # Step 8 — Plot clusters (2D)
    # -----------------------------
    print("\nSTEP 8 — Plotting clusters (PCA -> 2D)\n")

    # Reduce embeddings to 2D for visualization (deterministic)
    pca = PCA(n_components=2, random_state=0)
    points_2d = pca.fit_transform(combined_embeddings)

    plt.figure()
    plt.title("Story Clusters (PCA 2D)")

    # Scatter per cluster
    for cid in range(NUM_CLUSTERS):
        idx = [i for i, s in enumerate(stories) if s["cluster"] == cid]
        if not idx:
            continue
        plt.scatter(points_2d[idx, 0], points_2d[idx, 1], label=f"Cluster {cid}")

    # Label each point with Story #
    for i, s in enumerate(stories):
        plt.annotate(
            s["label"].replace("Story ", "S"),
            (points_2d[i, 0], points_2d[i, 1]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9
        )

    plt.xlabel("PCA-1")
    plt.ylabel("PCA-2")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Step 9 — Classify a new story
    # -----------------------------
    print("\nSTEP 9 — Classify a new story\n")

    new_story_text = """
    My grandfather knew much about botany. He was an expert at grafting plants, especially azaleas, fruit trees. But not just that, 
    propagation in general, orchids, Easter lilies. I used to hang out in this huge hothouse in the yard, where he performed his
    experiments. I'm pretty such all of those plants are gone by now, but it carries on in my own gardening adventures.
    """
    # --- summarize ---
    print("\nSummarizing new story...")

    new_summary = summarize_story(new_story_text)

    print("Summary:", new_summary)


    # --- embeddings ---
    print("\nEmbedding new story...")

    new_summary_vec = embed_text(new_summary)
    new_text_vec = embed_text(new_story_text)

    new_summary_vec = np.array(new_summary_vec)
    new_text_vec = np.array(new_text_vec)


    # --- combine embeddings ---
    new_combined = (
        SUMMARY_WEIGHT * new_summary_vec +
        TEXT_WEIGHT * new_text_vec
    )


    # --- distance to clusters ---
    print("\nDistances to clusters:")

    distances = []

    for cid, centroid in enumerate(centroids):

        dist = np.linalg.norm(new_combined - centroid)

        distances.append(dist)

        print(f"Cluster {cid} distance = {dist:.4f}")


    # --- choose best cluster ---
    best_cluster = int(np.argmin(distances))

    print("\nBest matching cluster:", best_cluster)