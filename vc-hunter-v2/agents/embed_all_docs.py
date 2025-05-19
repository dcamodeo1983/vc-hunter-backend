
import os
import json
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.llm_client import get_embedding, count_tokens
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

load_dotenv()

INPUT_DIRS = {
    "portfolio": "data/classified/portfolio",
    "strategy": "data/classified/strategy"
}
OUTPUT_FILE = "data/embedded/embedded.jsonl"
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def embed_directory(input_dir, doc_type):
    embedded = []
    for fname in os.listdir(input_dir):
        if not fname.endswith(".jsonl"):
            continue
        with open(os.path.join(input_dir, fname), "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                text = record.get("content", "") + " " + ", ".join(record.get("sectors", []))
                embedding = get_embedding(text)
                tokens = count_tokens(text)
                record.update({
                    "embedding": embedding,
                    "doc_type": doc_type,
                    "token_count": tokens
                })
                embedded.append(record)
    return embedded

def embed_all():
    all_records = []
    for doc_type, directory in INPUT_DIRS.items():
        all_records.extend(embed_directory(directory, doc_type))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for rec in all_records:
            out.write(json.dumps(rec) + "\n")
    print("✅ All documents embedded.")

if __name__ == "__main__":
    embed_all()
