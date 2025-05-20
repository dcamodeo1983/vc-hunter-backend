import os
import json
from utils.llm_client import call_chat_model

INPUT_DIR = "vc-hunter-v2/data/raw/strategy"
OUTPUT_DIR = "vc-hunter-v2/data/classified/strategy"
token_usage_total = 0


class StrategyProfilerAgent:
    def __init__(self, input_dir=INPUT_DIR, output_dir=OUTPUT_DIR):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def extract_strategy_tags(self, text):
        global token_usage_total
        prompt = f"""
You are an analyst. Read the following venture capital firm strategy and extract 3–6 high-quality strategic tags that capture their focus areas, such as 'biotech', 'defense tech', 'AI infrastructure', etc.
Respond with a comma-separated list.

Strategy:
{text}
"""
        response, tokens = call_chat_model(prompt)
        token_usage_total += tokens
        tags = [t.strip() for t in response.split(",") if t.strip()]
        return tags

    def run(self):
        global token_usage_total
        os.makedirs(self.output_dir, exist_ok=True)
        for fname in os.listdir(self.input_dir):
            if not fname.endswith(".jsonl"):
                continue
            with open(os.path.join(self.input_dir, fname), "r", encoding="utf-8") as f:
                lines = f.readlines()

            tagged = []
            for line in lines:
                item = json.loads(line)
                tags = self.extract_strategy_tags(item.get("content", ""))
                item["strategy_tags"] = tags
                tagged.append(item)

            with open(os.path.join(self.output_dir, fname), "w", encoding="utf-8") as out:
                for item in tagged:
                    out.write(json.dumps(item) + "\n")

        print(f"✅ Strategy profiling complete. Tokens used: {token_usage_total}")


if __name__ == "__main__":
    agent = StrategyProfilerAgent()
    agent.run()
