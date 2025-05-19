import os
import json
from glob import glob

EMBED_DIR = "data/embeddings"
OUTPUT_PATH = os.path.join(EMBED_DIR, "vc_hunter_all_embeddings.jsonl")

def merge_embeddings():
    os.makedirs(EMBED_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as outfile:
        for path in glob(os.path.join(EMBED_DIR, "*.json")):
            if "chatbot" in path or "all" in path:
                continue
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        outfile.write(json.dumps(data) + "\n")
                    elif isinstance(data, list):
                        for item in data:
                            outfile.write(json.dumps(item) + "\n")
                except Exception as e:
                    print(f"❌ Failed to process {path}: {e}")
    print(f"✅ Combined embeddings written to: {OUTPUT_PATH}")

if __name__ == "__main__":
    merge_embeddings()
