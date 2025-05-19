
import os
import json
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from utils.llm_client import llm_chat, count_tokens

load_dotenv()

INPUT_DIR = "data/raw/strategy"
OUTPUT_DIR = "data/classified/strategy"
os.makedirs(OUTPUT_DIR, exist_ok=True)

token_usage_total = 0

def extract_strategy_tags(text: str):
    prompt = f"""
    You are a strategic analyst. Review the following startup description and identify key strategic themes or positioning angles.

    Text:
    {text}

    Return a JSON list of 3-6 strategic tags (strings only), such as "platform play", "deep tech", "government alignment", "consumer convenience", etc.
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        response = llm_chat(messages)
        global token_usage_total
        token_usage_total += count_tokens(messages)
        return json.loads(response)
    except Exception as e:
        print(f"❌ Error extracting strategy tags: {e}")
        return []

def process_all():
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".jsonl"):
            continue
        with open(os.path.join(INPUT_DIR, fname), "r", encoding="utf-8") as f:
            lines = f.readlines()

        tagged = []
        for line in lines:
            item = json.loads(line)
            tags = extract_strategy_tags(item.get("content", ""))
            item["strategy_tags"] = tags
            tagged.append(item)

        with open(os.path.join(OUTPUT_DIR, fname), "w", encoding="utf-8") as out:
            for item in tagged:
                out.write(json.dumps(item) + "\n")

    print(f"✅ Strategy profiling complete. Tokens used: {token_usage_total}")

if __name__ == "__main__":
    process_all()
