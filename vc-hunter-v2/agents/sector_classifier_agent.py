import os
import json
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from utils.llm_client import llm_chat

load_dotenv()

INPUT_DIR = "data/raw/portfolio"
OUTPUT_DIR = "data/classified/portfolio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def classify_sectors(text: str):
    prompt = f"""
    Assume the role of an professor at a world class business university.  You preparing soem course material which will require students to classify start-ups into sectors.  YOu want to make sure you have already worked through the assignment before handing it to your students.  Classify the following startup description into 1 to 5 high-level sectors such as:
    Defense, Healthcare, AI, SaaS, Robotics, Fintech, Logistics, GovTech, Climate, or Consumer Tech.

    Text:
    {text}

    Respond with a JSON list of 1-5 sector names (strings only).
    """
    try:
        return json.loads(llm_chat([{"role": "user", "content": prompt}]))
    except Exception as e:
        print(f"❌ Failed to parse sectors: {e}")
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
            sectors = classify_sectors(item.get("content", ""))
            item["sectors"] = sectors
            tagged.append(item)

        with open(os.path.join(OUTPUT_DIR, fname), "w", encoding="utf-8") as out:
            for item in tagged:
                out.write(json.dumps(item) + "\n")

    print("✅ Sector classification complete.")

if __name__ == "__main__":
    process_all()
