
import os
import json
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.llm_client import llm_chat, count_tokens

load_dotenv()

STRATEGY_PATH = "data/classified/strategy"
OUTPUT_PATH = "data/analysis/behavior_consistency"
os.makedirs(OUTPUT_PATH, exist_ok=True)

def load_strategy_profile(vc_name):
    path = os.path.join(STRATEGY_PATH, f"{vc_name}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def score_behavior_consistency(vc_summary, strategy_profile):
    prompt = f"""
You are an analyst evaluating how consistent a venture capital firm's stated investment strategy is with its actual behavior. Given the firm's public summary and a synthesized strategy profile (tags and inferred priorities), rate the level of alignment on a scale from 1 to 5 and explain the rationale.

VC Summary:
{vc_summary}

Strategy Tags:
{strategy_profile}

Respond in the following JSON format:
{{
  "score": int,   // 1 (low consistency) to 5 (high consistency)
  "justification": str
}}
"""
    try:
        response = llm_chat([{"role": "user", "content": prompt}])
        return json.loads(response)
    except Exception as e:
        print(f"❌ Error scoring consistency: {e}")
        return {"score": 0, "justification": "LLM error"}

def process_all():
    from utils.file_manager import load_vc_summaries
    summaries = load_vc_summaries()
    for vc_name, summary in summaries.items():
        strategy = load_strategy_profile(vc_name)
        if not strategy:
            print(f"❌ No strategy profile found for {vc_name}")
            continue
        if not strategy.get("tags"):
            print(f"⚠️ Skipping {vc_name}: no strategy tags.")
            continue
        result = score_behavior_consistency(summary, strategy)
        out_path = os.path.join(OUTPUT_PATH, f"{vc_name}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    print("🏁 Behavior consistency scoring complete.")

if __name__ == "__main__":
    process_all()
