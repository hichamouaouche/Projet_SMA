import os
import json
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

model_name = os.getenv("modelName")
if not model_name:
    raise ValueError("Missing environment variable: modelName")

model = ChatOllama(
    model=model_name,
    base_url="https://ollama.com",
    client_kwargs={
        "headers": {
            "Authorization": f"Bearer {os.getenv('Ollama_api_key')}"
        }
    },
)

# ── Test Dataset ───────────────────────────────────────────────────────────────

TEST_SENTENCES = [
    {"input": "I goed to the store yesterday",          "expected": "I went to the store yesterday"},
    {"input": "She don't like apples",                   "expected": "She doesn't like apples"},
    {"input": "We was happy to see him",                 "expected": "We were happy to see him"},
    {"input": "He run very fastly",                      "expected": "He runs very fast"},
    {"input": "The childs are playing outside",          "expected": "The children are playing outside"},
    {"input": "I have went there before",                "expected": "I have gone there before"},
    {"input": "Its a beautiful day today",               "expected": "It's a beautiful day today"},
    {"input": "They doesnt know the answer",             "expected": "They don't know the answer"},
    {"input": "Me and him went to school",               "expected": "He and I went to school"},
    {"input": "The dog barked loudlier than the cat",    "expected": "The dog barked louder than the cat"},
]

# ── Prompt Versions ────────────────────────────────────────────────────────────

PROMPTS = {
    "Version A (Minimal)": (
        "Correct the user's input only if there is a clear grammatical error. "
        "Ignore style. Respond in 10 to 15 words."
    ),
    "Version B (Strict)": (
        "You are a grammar expert. Correct ALL grammatical errors in the input. "
        "Return only the corrected sentence with a brief explanation of the main error. "
        "Keep the response under 20 words."
    ),
    "Version C (Pedagogical)": (
        "You are a language teacher. Show the corrected sentence first, "
        "then explain the grammar rule that was violated in one or two sentences. "
        "Be encouraging. Keep the response under 25 words."
    ),
}

# ── Evaluation ─────────────────────────────────────────────────────────────────

def run_evaluation() -> None:
    print("=" * 72)
    print("PROMPT EVALUATION — A/B/C TESTING")
    print("=" * 72)
    print(f"Model            : {model_name}")
    print(f"Test sentences   : {len(TEST_SENTENCES)}")
    print(f"Prompt versions  : {len(PROMPTS)}")
    print("=" * 72)

    results: dict = {}

    for version_name, prompt_text in PROMPTS.items():
        print(f"\n{'─'*60}")
        print(f"  {version_name}")
        print(f"{'─'*60}")

        corrections = []
        total_words = 0

        for i, test in enumerate(TEST_SENTENCES, start=1):
            messages = [("system", prompt_text), ("human", test["input"])]
            response = model.invoke(messages)
            output = response.content.strip()
            word_count = len(output.split())
            total_words += word_count

            corrections.append({
                "input":             test["input"],
                "expected":          test["expected"],
                "output":            output,
                "word_count":        word_count,
                "has_correction":    output.lower() != test["input"].lower(),
                "length_compliant":  word_count <= 25,
            })

            print(f"  [{i:02d}] Input    : {test['input']}")
            print(f"       Output   : {output}")
            print(f"       Expected : {test['expected']}")
            print()

        count = len(TEST_SENTENCES)
        avg_words        = round(total_words / count, 1)
        correction_rate  = round(sum(1 for c in corrections if c["has_correction"]) / count * 100, 1)
        length_compliance = round(sum(1 for c in corrections if c["length_compliant"]) / count * 100, 1)

        results[version_name] = {
            "avg_words":         avg_words,
            "correction_rate":   correction_rate,
            "length_compliance": length_compliance,
            "corrections":       corrections,
        }

    # ── Summary table ──────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("RESULTS SUMMARY")
    print("=" * 72)
    print(f"{'Version':<28} {'Avg Words':<12} {'Correction %':<16} {'Length OK %'}")
    print("─" * 72)

    for name, m in results.items():
        print(f"{name:<28} {m['avg_words']:<12} {m['correction_rate']:<16} {m['length_compliance']}%")

    best = max(results.items(), key=lambda x: x[1]["correction_rate"] + x[1]["length_compliance"])
    print("\n" + "=" * 72)
    print(f"RECOMMENDED  : {best[0]}")
    print(
        f"Reason       : Best combined score — "
        f"correction rate {best[1]['correction_rate']}%, "
        f"length compliance {best[1]['length_compliance']}%"
    )
    print("=" * 72)

    # ── Export ─────────────────────────────────────────────────────────────────
    output_path = "prompt_evaluation_results.json"
    export = {
        k: {
            "avg_words":         v["avg_words"],
            "correction_rate":   v["correction_rate"],
            "length_compliance": v["length_compliance"],
        }
        for k, v in results.items()
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2)
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    run_evaluation()
