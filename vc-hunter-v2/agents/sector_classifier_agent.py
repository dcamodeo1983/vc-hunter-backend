import os
import json
from dotenv import load_dotenv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.llm_client import llm_chat, count_tokens
token_usage_total = 0

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

load_dotenv()

INPUT_DIR = "data/raw/portfolio"
OUTPUT_DIR = "data/classified/portfolio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def classify_sectors(text: str):
    prompt = f"""
    Assume the role of a professor at a world-class business university. You are preparing course material that requires students to classify startups into sectors. Classify the following startup description into 1 to 5 high-level sectors such as:
    Defense, Healthcare, AI, SaaS, Robotics, Fintech, Logistics, GovTech, Climate, or Consumer Tech.

    Text:
    {text}

    Respond with a JSON list of 1-5 sector names (strings only).
    """
    try:
        result = llm_chat([{"role": "user", "content": prompt}])
        if isinstance(result, str):
            return json.loads(result)
        return result
    except Exception as e:
        print(f"❌ Failed to parse sectors: {e}")
        return []


def process_all():
    global token_usage_total
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".jsonl"):
            continue
        with open(os.path.join(INPUT_DIR, fname), "r", encoding="utf-8") as f:
            lines = f.readlines()

        tagged = []
        for line in lines:
            item = json.loads(line)
            sectors = classify_sectors(item.get("content", ""))
            item["sectors"] = sectors
            tagged.append(item)

        with open(os.path.join(OUTPUT_DIR, fname), "w", encoding="utf-8") as out:
            for item in tagged:
                out.write(json.dumps(item) + "\n")

    print("✅ Sector classification complete.")
    print(f"🔢 Total tokens used: {token_usage_total}")

if __name__ == "__main__":
    process_all()
