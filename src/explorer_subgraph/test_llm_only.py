import json
import os
import time
import openai
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# Config
# ----------------------------
MODEL = os.getenv("CHATGPT_MODEL", "gpt-4.1-nano")
MAX_TOKENS = int(os.getenv("CHATGPT_MAX_RESPONSE_TOKENS", "220"))

openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT_FILE = "test_llm_only.txt"

# ----------------------------
# Helpers
# ----------------------------
def now_ms() -> float:
    return time.perf_counter() * 1000.0


def load_prompt(filename: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def fill_prompt(template: str, source_label: str, source_iri: str, context_text: str) -> str:
    # Ensure optional IRI is represented as empty string if None
    source_iri = source_iri or ""

    # Simple string replacement (keeps your prompt format unchanged)
    return (
        template
        .replace("{SOURCE_LABEL}", source_label)
        .replace("{SOURCE_IRI_OR_EMPTY}", source_iri)
        .replace("{CONTEXT_TEXT}", context_text)
    )


def call_chatgpt(prompt: str) -> dict:
    t0 = now_ms()

    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON. No markdown. No commentary."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=MAX_TOKENS,
    )

    t1 = now_ms()

    text = resp["choices"][0]["message"]["content"].strip()
    data = json.loads(text)

    return {"latency_ms": (t1 - t0), "data": data}

def prepare_output_files(
    base_dir: str,
    prefix: str = "debug_test_llm_only"
) -> dict:
    """
    Ensures output directory exists and returns
    fully-qualified paths for prompt + output files.
    """
    os.makedirs(base_dir, exist_ok=True)

    return {
        "prompt_path": os.path.join(base_dir, f"{prefix}.txt"),
        "output_path": os.path.join(base_dir, f"{prefix}_output.json"),
    }

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    SOURCE_LABEL = "magnacut"
    SOURCE_IRI = ""
    CONTEXT_TEXT = ""

    template = load_prompt(PROMPT_FILE)
    prompt = fill_prompt(template, SOURCE_LABEL, SOURCE_IRI, CONTEXT_TEXT)

    # ---------------------------------------------
    # Prepare output paths
    # ---------------------------------------------
    output_dir = os.path.join(os.getcwd(), "C:\MapRock\AssemblageOfAI\src\explorer_subgraph\output")
    paths = prepare_output_files(output_dir)
    print(f"Prompt will be saved to: {paths['prompt_path']}")

    # Save prompt for debugging
    with open(paths["prompt_path"], "w", encoding="utf-8") as f:
        f.write(prompt)

    result = call_chatgpt(prompt)

    print(f"LLM latency ms: {result['latency_ms']:.1f}")
    print(json.dumps(result["data"], indent=2))

    # Save JSON output for debugging
    with open(paths["output_path"], "w", encoding="utf-8") as f:
        json.dump(result["data"], f, indent=2)
