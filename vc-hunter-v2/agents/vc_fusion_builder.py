# vc_fusion_builder.py

import os
import json
from utils.llm_client import llm_chat
from utils.file_utils import load_jsonl

VC_RAW_DIR = "vc-hunter-v2/data/raw/vcs"
PORTFOLIO_EMBED_PATH = "vc-hunter-v2/data/embeddings/portfolio_embeddings.json"
FUSION_OUT_DIR = "vc-hunter-v2/data/fusion_docs"

class FusionBuilder:
    def __init__(self, vc_dir=VC_RAW_DIR, portfolio_path=PORTFOLIO_EMBED_PATH, output_dir=FUSION_OUT_DIR):
        self.vc_dir = vc_dir
        self.portfolio_path = portfolio_path
        self.output_dir = output_dir

    def build_fusion_text(self, vc_text, portfolio_summaries):
        portfolio_snippets = "\n\n".join(portfolio_summaries)
        prompt = f"""
You are an investment analyst tasked with fusing a venture capital firm's stated strategy with the behavior implied by their portfolio investments. Given their website text and a set of startup investment descriptions, synthesize a concise and coherent description (200-300 words) of how this VC behaves and what they care about. Use a neutral, professional tone.

VC Text:
{vc_text}

Portfolio:
{portfolio_snippets}

Synthesized Summary:
"""
        response = llm_chat([{"role": "user", "content": prompt}])
        return response.strip()

    def run(self):
        os.makedirs(self.output_dir, exist_ok=True)

        with open(self.portfolio_path, "r", encoding="utf-8") as f:
            portfolio_data = json.load(f)

        for fname in os.listdir(self.vc_dir):
            if not fname.endswith(".jsonl"):
                continue

            vc_name = fname.replace(".jsonl", "")
            vc_path = os.path.join(self.vc_dir, fname)

            with open(vc_path, "r", encoding="utf-8") as f:
                vc_lines = f.readlines()

            vc_text = "\n\n".join([json.loads(line)["content"] for line in vc_lines if line.strip()])

            portfolio_summaries = [entry["content"] for entry in portfolio_data if entry.get("vc_name") == vc_name and "content" in entry]
            if not portfolio_summaries:
                print(f"⚠️ Skipping {vc_name}: no portfolio summaries found.")
                continue

            try:
                fused = self.build_fusion_text(vc_text, portfolio_summaries)
                out_path = os.path.join(self.output_dir, f"{vc_name}.txt")
                with open(out_path, "w", encoding="utf-8") as out:
                    out.write(fused)
                print(f"✅ Fused: {vc_name}")
            except Exception as e:
                print(f"❌ Failed to build fusion for {vc_name}: {e}")


if __name__ == "__main__":
    builder = FusionBuilder()
    builder.run()
