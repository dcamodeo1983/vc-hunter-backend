import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

INPUT_DIR = "data/raw/portfolio"
OUTPUT_DIR = "data/classified/portfolio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def classify_sectors(text: str):
    prompt = f"""
    Classify the following startup description into 1 to 3 high-level sectors such as:
    Defense, Healthcare, AI, SaaS, Robotics, Fintech, Logistics, GovTech, Climate, or Consumer Tech.

    Text:
    {text}

    Respond with a JSON list of 1-3 sector names (strings only).
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return json.loads(response.choices[0].message.content)
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
            item["sector_tags"] = sectors
            tagged.append(item)

        with open(os.path.join(OUTPUT_DIR, fname), "w", encoding="utf-8") as out:
            for item in tagged:
                out.write(json.dumps(item) + "\n")

    print("✅ Sector classification complete.")

if __name__ == "__main__":
    process_all()
