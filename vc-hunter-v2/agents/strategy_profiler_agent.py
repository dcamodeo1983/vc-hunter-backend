import os
import json
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from utils.llm_client import llm_chat

load_dotenv()

INPUT_DIR = "data/raw/strategy"
OUTPUT_DIR = "data/classified/strategy"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_strategy_tags(text: str):
    prompt = f"""
    Assume the role of HArvard Business School Professor.  You have deep knowledge of strategic frameworks including but not limited to ; HAmilton Helmers 7 Powers, Porters FiveForces, Clayton Christenson's Disruptive Innovation, PEter Thiel's Zero to One, BCG Matrix, and McKinsey 9 Box Matrix, and Ansoff Matrix.  YOur goal is to review VC funds and by looking at their website and derive their stated and latent strategy. Analyze the following venture firm's public material and extract 3-7 investment strategy tags.

    Strategy tags should be high-level themes such as:
    Dual-Use Tech, Bio + Health, Network Effects, GovTech, AI/ML, DeepTech, Climate + ESG, Vertical SaaS, Founders First, etc.

    Text:
    {text}

    Respond with a JSON list of strings.
    """
    try:
        return json.loads(llm_chat([{"role": "user", "content": prompt}]))
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

    print("✅ Strategy profiling complete.")

if __name__ == "__main__":
    process_all()
