# behavior_consistency_scorer.py

import os
import json
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm_client import llm_chat, count_tokens
from utils.file_utils import load_jsonl

load_dotenv()

STRATEGY_PATH = "vc-hunter-v2/data/classified/strategy"
OUTPUT_PATH = "vc-hunter-v2/data/analysis/behavior_consistency"
VC_PROFILES_PATH = "vc-hunter-v2/data/processed/vc_profiles.jsonl"
os.makedirs(OUTPUT_PATH, exist_ok=True)

class BehaviorScorer:
    def __init__(self, strategy_path=STRATEGY_PATH, profiles_path=VC_PROFILES_PATH, output_dir=OUTPUT_PATH):
        self.strategy_path = strategy_path
        self.profiles_path = profiles_path
        self.output_dir = output_dir

    def load_strategy_profile(self, vc_name):
        path = os.path.join(self.strategy_path, f"{vc_name}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def score_behavior_consistency(self, vc_summary, strategy_profile):
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

    def run(self):
        summaries = load_jsonl(self.profiles_path)
        summaries = {item["name"]: item["summary"] for item in summaries}

        for vc_name, summary in summaries.items():
            strategy = self.load_strategy_profile(vc_name)
            if not strategy:
                print(f"❌ No strategy profile found for {vc_name}")
                continue
            if not strategy.get("tags"):
                print(f"⚠️ Skipping {vc_name}: no strategy tags.")
                continue

            result = self.score_behavior_consistency(summary, strategy)
            out_path = os.path.join(self.output_dir, f"{vc_name}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

        print("🏁 Behavior consistency scoring complete.")


if __name__ == "__main__":
    scorer = BehaviorScorer()
    scorer.run()
