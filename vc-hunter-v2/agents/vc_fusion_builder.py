# vc_fusion_builder.py

import os
import json
from utils.llm_client import llm_chat

VC_RAW_DIR = "vc-hunter-v2/data/raw/vcs"
FUSION_OUT_DIR = "vc-hunter-v2/data/fusion_docs"
BEHAVIOR_DIR = "vc-hunter-v2/data/analysis/behavior_consistency"
STRATEGY_DIR = "vc-hunter-v2/data/classified/strategy"

class FusionBuilder:
    def __init__(self, vc_dir=VC_RAW_DIR, output_dir=FUSION_OUT_DIR):
        self.vc_dir = vc_dir
        self.output_dir = output_dir

    def build_fusion_text(self, vc_text):
        prompt = f"""
You are an investment analyst. Write a 200-word synthesis of this VC firm's website content. Highlight their thesis, areas of focus, tone, and personality as inferred from the text.

Website Content:
{vc_text}

Synthesis:
"""
        response = llm_chat([{"role": "user", "content": prompt}])
        return response.strip()

    def run(self):
        os.makedirs(self.output_dir, exist_ok=True)

        for fname in os.listdir(self.vc_dir):
            if not fname.endswith(".jsonl"):
                continue

            vc_name = fname.replace(".jsonl", "")
            vc_path = os.path.join(self.vc_dir, fname)

            with open(vc_path, "r", encoding="utf-8") as f:
                lines = [json.loads(line) for line in f if line.strip()]
            vc_text = "\n\n".join([entry.get("content", "") for entry in lines if "content" in entry])

            if not vc_text.strip():
                print(f"⚠️ Skipping {vc_name}: no usable VC content.")
                continue

            try:
                fused = self.build_fusion_text(vc_text)

                # 🧠 Append behavior consistency score
                behavior_path = os.path.join(BEHAVIOR_DIR, f"{vc_name}.json")
                if os.path.exists(behavior_path):
                    with open(behavior_path, "r", encoding="utf-8") as b:
                        behavior = json.load(b)
                        score = behavior.get("score", "N/A")
                        justification = behavior.get("justification", "")
                        fused += f"\n\n🤖 Behavior Consistency Score: {score}\nJustification: {justification}"

                # 🧠 Append strategy classification summary
                strategy_path = os.path.join(STRATEGY_DIR, f"{vc_name}.json")
                if os.path.exists(strategy_path):
                    with open(strategy_path, "r", encoding="utf-8") as s:
                        strategy = json.load(s)
                        summary = strategy.get("summary", "")
                        tags = ", ".join(strategy.get("tags", []))
                        fused += f"\n\n📌 Strategy Summary: {summary}\n🏷️ Tags: {tags}"

                out_path = os.path.join(self.output_dir, f"{vc_name}.txt")
                with open(out_path, "w", encoding="utf-8") as out:
                    out.write(fused)
                print(f"✅ Fused: {vc_name}")
            except Exception as e:
                print(f"❌ Failed to build fusion for {vc_name}: {e}")

if __name__ == "__main__":
    builder = FusionBuilder()
    builder.run()
