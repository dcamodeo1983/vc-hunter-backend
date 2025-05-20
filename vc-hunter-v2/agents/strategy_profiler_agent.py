# strategy_profiler_agent.py

import os
import json
from utils.llm_client import llm_chat
from tqdm import tqdm

INPUT_DIR = "vc-hunter-v2/data/raw/vcs"
OUTPUT_DIR = "vc-hunter-v2/data/classified/strategy"

def slugify(name):
    return name.replace(" ", "").replace(".", "").replace(",", "")

class StrategyProfilerAgent:
    def __init__(self, input_dir=INPUT_DIR, output_dir=OUTPUT_DIR):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        for fname in tqdm(os.listdir(self.input_dir), desc="Profiling strategy"):
            if not fname.endswith(".jsonl"):
                continue
            path = os.path.join(self.input_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                lines = [json.loads(line) for line in f if line.strip()]
                text = "\n\n".join([entry.get("content", "") for entry in lines])

            prompt = f"""
You are an analyst reviewing a VC firm's public website content. Extract 3-5 key strategic tags and a short paragraph summarizing their investment focus and thesis.

VC Content:
{text}

Respond in the following JSON format:
{{
  "tags": [str],
  "summary": str
}}
"""

            try:
                response = llm_chat([{"role": "user", "content": prompt}])
                result = json.loads(response)
                outname = slugify(fname.replace(".jsonl", "")) + ".json"
                with open(os.path.join(self.output_dir, outname), "w", encoding="utf-8") as out:
                    json.dump(result, out, indent=2)
            except Exception as e:
                print(f"❌ Failed to profile {fname}: {e}")

if __name__ == "__main__":
    StrategyProfilerAgent().run()
