import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

INPUT_DIR = "data/fusions"
OUTPUT_DIR = "data/strategy_profiles"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_strategy_tags(text: str):
    prompt = f"""
    From the following venture firm strategy summary, extract 3-5 tags that represent their investment philosophy, strategic posture, or startup preferences.
    
    Examples include: Thesis-led, Deep Tech, GovTech, Repeat Founders, Contrarian, Platform Builders, AI-Centric, Long-Horizon, Risk-Tolerant, Defense-Oriented.

    Text:
    {text}

    Respond with a JSON list of short string tags.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Strategy tag parse error: {e}")
        return []

def process_all():
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".jsonl"):
            continue
        with open(os.path.join(INPUT_DIR, fname), "r", encoding="utf-8") as f:
            items = [json.loads(line) for line in f]

        for item in items:
            tags = extract_strategy_tags(item.get("content", ""))
            item["strategy_tags"] = tags

        with open(os.path.join(OUTPUT_DIR, fname), "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item) + "\n")

    print("✅ Strategy profiling complete.")

if __name__ == "__main__":
    process_all()
