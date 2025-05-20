# sector_classifier_agent.py

import os
import json
from utils.llm_client import call_chat_model

INPUT_DIR = "vc-hunter-v2/data/raw/portfolio"
OUTPUT_DIR = "vc-hunter-v2/data/classified/portfolio"
token_usage_total = 0


class SectorClassifierAgent:
    def __init__(self, input_dir=INPUT_DIR, output_dir=OUTPUT_DIR):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def classify_sector(self, text):
        global token_usage_total
        prompt = f"""
You are a market analyst. Based on the business description below, classify the company into 1–2 high-level sectors such as 'Fintech', 'Defense', 'Logistics', 'Enterprise SaaS', 'Healthcare', etc. Respond with a comma-separated list.

Description:
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

            classified = []
            for line in lines:
                item = json.loads(line)
                tags = self.classify_sector(item.get("content", ""))
                item["sector_tags"] = tags
                classified.append(item)

            with open(os.path.join(self.output_dir, fname), "w", encoding="utf-8") as out:
                for item in classified:
                    out.write(json.dumps(item) + "\n")

        print(f"✅ Sector classification complete. Tokens used: {token_usage_total}")


if __name__ == "__main__":
    agent = SectorClassifierAgent()
    agent.run()
