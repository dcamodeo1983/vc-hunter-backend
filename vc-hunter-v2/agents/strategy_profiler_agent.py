import os
import json
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from utils.llm_client import llm_chat, count_tokens

token_usage_total = 0

load_dotenv()

INPUT_DIR = "data/raw/strategy"
OUTPUT_DIR = "data/classified/strategy"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_strategy_tags(text: str):
    global token_usage_total
    prompt = f"""
    As a venture capital analyst preparing a strategic review, extract 3-7 key strategic themes or focus areas mentioned in the following description of a VC firm's investment thesis. Use concise phrases such as: “AI-first SaaS”, “Bioinformatics”, “Frontier Tech”, “Cloud-native apps”, “Verticalized Marketplaces”, etc.

    Text:
    {text}

    Respond with a JSON list of concise tags (strings only).
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        response = llm_chat(messages)
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
