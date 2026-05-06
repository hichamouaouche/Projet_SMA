import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import json

load_dotenv()

model_name = os.getenv("modelName")
if not model_name:
    raise ValueError("Missing modelName")

model = ChatOllama(
    model=model_name,
    base_url="https://ollama.com",
    client_kwargs={
        "headers": {
            "Authorization": f"Bearer {os.getenv('Ollama_api_key')}"
        }
    },
)

# ===== TEST DATASET =====
test_sentences = [
    {"input": "I goed to the store yesterday", "expected": "I went to the store yesterday"},
    {"input": "She don't like apples", "expected": "She doesn't like apples"},
    {"input": "We was happy to see him", "expected": "We were happy to see him"},
    {"input": "He run very fastly", "expected": "He runs very fast"},
    {"input": "The childs are playing outside", "expected": "The children are playing outside"},
    {"input": "I have went there before", "expected": "I have gone there before"},
    {"input": "Its a beautiful day today", "expected": "It's a beautiful day today"},
    {"input": "They doesnt know the answer", "expected": "They don't know the answer"},
    {"input": "Me and him went to school", "expected": "He and I went to school"},
    {"input": "The dog barked loudlier than the cat", "expected": "The dog barked louder than the cat"},
]

# ===== PROMPT VERSIONS TO COMPARE =====
prompts = {
    "Version A (Minimal)": "correct the input and give the grammer correction just if needed and nesseccery bias to not correct if it is acceptble , not synthaxe correction ! responde just in 10~15 word ;",
    "Version B (Strict)": "You are a grammar expert. Correct ALL grammatical errors in the user input. Return ONLY the corrected sentence with a brief explanation of the main error. Keep the response under 20 words.",
    "Version C (Pedagogical)": "You are a language teacher. First show the corrected sentence, then explain the grammar rule that was violated in 1-2 sentences. Be encouraging. Keep the response under 25 words.",
}

# ===== EVALUATION =====
def run_evaluation():
    print("=" * 80)
    print("PROMPT EVALUATION - A/B/C TESTING")
    print("=" * 80)
    print(f"Model: {model_name}")
    print(f"Test sentences: {len(test_sentences)}")
    print(f"Prompt versions: {len(prompts)}")
    print("=" * 80)

    results = {}

    for prompt_name, prompt_text in prompts.items():
        print(f"\n{'='*60}")
        print(f"Testing: {prompt_name}")
        print(f"{'='*60}")

        corrections = []
        total_words = 0

        for i, test in enumerate(test_sentences):
            messages = [
                ("system", prompt_text),
                ("human", test["input"])
            ]
            response = model.invoke(messages)
            content = response.content.strip()
            word_count = len(content.split())
            total_words += word_count

            has_correction = content.lower() != test["input"].lower()
            is_correct_length = word_count <= 25

            corrections.append({
                "input": test["input"],
                "expected": test["expected"],
                "output": content,
                "word_count": word_count,
                "has_correction": has_correction,
                "is_correct_length": is_correct_length
            })

            print(f"  [{i+1}] Input:    {test['input']}")
            print(f"      Output:   {content}")
            print(f"      Expected: {test['expected']}")
            print()

        # Calculate metrics
        avg_words = total_words / len(test_sentences)
        correction_rate = sum(1 for c in corrections if c["has_correction"]) / len(test_sentences) * 100
        length_compliance = sum(1 for c in corrections if c["is_correct_length"]) / len(test_sentences) * 100

        results[prompt_name] = {
            "avg_words": round(avg_words, 1),
            "correction_rate": round(correction_rate, 1),
            "length_compliance": round(length_compliance, 1),
            "corrections": corrections
        }

    # ===== FINAL COMPARISON TABLE =====
    print("\n" + "=" * 80)
    print("FINAL COMPARISON")
    print("=" * 80)
    print(f"{'Prompt':<25} {'Avg Words':<12} {'Correction Rate':<18} {'Length OK':<12}")
    print("-" * 80)

    for prompt_name, metrics in results.items():
        print(f"{prompt_name:<25} {metrics['avg_words']:<12} {metrics['correction_rate']:<18} {metrics['length_compliance']}%")

    # ===== RECOMMENDATION =====
    print("\n" + "=" * 80)
    best = max(results.items(), key=lambda x: x[1]["correction_rate"] + x[1]["length_compliance"])
    print(f"RECOMMENDED: {best[0]}")
    print(f"Reason: Best balance of correction accuracy ({best[1]['correction_rate']}%) and length compliance ({best[1]['length_compliance']}%)")
    print("=" * 80)

    # Save results
    with open("prompt_evaluation_results.json", "w") as f:
        json.dump({k: {"avg_words": v["avg_words"], "correction_rate": v["correction_rate"], "length_compliance": v["length_compliance"]} for k, v in results.items()}, f, indent=2)
    print(f"\nResults saved to files/prompt_evaluation_results.json")

if __name__ == "__main__":
    run_evaluation()
