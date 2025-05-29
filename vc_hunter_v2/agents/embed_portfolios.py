import os
import json
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Constants
MODEL_ID = "text-embedding-3-small"
INPUT_DIR = "data/raw/portfolio"
OUTPUT_FILE = "data/embeddings/portfolio_embeddings.json"

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_text(text):
    try:
        response = client.embeddings.create(
            input=[text[:8000]],
            model=MODEL_ID
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return None

def process_all():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    results = []

    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".jsonl"):
            continue
        path = os.path.join(INPUT_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    text = record.get("content", "").strip()
                    if not text:
                        continue
                    vector = embed_text(text)
                    if vector:
                        results.append({
                            "url": record.get("url"),
                            "type": "portfolio",
                            "embedding": vector
                        })
                except Exception as e:
                    print(f"❌ Failed to embed {fname}: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Saved {len(results)} portfolio embeddings to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_all()
