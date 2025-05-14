import os, json
from utils.llm_client import llm_chat

INPUT_DIR = "data/fusions"
OUTPUT_DIR = "data/strategy_profiles"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_strategy_tags(text):
    prompt = f"""
    Identify 3 to 5 high-level strategic themes in the following VC description:

    "{text}"

    Respond as a JSON list of strings.
    """
    try:
        return json.loads(llm_chat(prompt))
    except Exception as e:
        print(f"❌ Error extracting strategy tags: {e}")
        return []

def process_all():
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".jsonl"):
            continue
        with open(os.path.join(INPUT_DIR, fname), "r", encoding="utf-8") as f:
            lines = f.readlines()

        enriched = []
        for line in lines:
            item = json.loads(line)
            tags = extract_strategy_tags(item.get("content", ""))
            item["strategy_tags"] = tags
            enriched.append(item)

        with open(os.path.join(OUTPUT_DIR, fname), "w", encoding="utf-8") as out:
            for item in enriched:
                out.write(json.dumps(item) + "\n")

    print("✅ Strategy profiling complete.")

if __name__ == "__main__":
    process_all()
