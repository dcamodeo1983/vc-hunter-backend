import os
import json
import sys  # ✅ Required for path manipulation

# Add parent directory to sys.path to access utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm_client import get_embedding  # ✅ Uses your OpenAI wrapper

INPUT_DIR = "data/fusion_docs"
OUTPUT_FILE = "data/embeddings/vc_embeddings.json"

def embed_text(text):
    return get_embedding(text)

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    embeddings = []

    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(INPUT_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if not text:
                continue
            try:
                vector = embed_text(text)
                embeddings.append({
                    "vc_name": fname.replace(".txt", ""),
                    "type": "vc_fusion",
                    "embedding": vector
                    "text": text,  # ✅ embed the raw text for chatbot reference
                    "embedding": vector
                })
                print(f"✅ Embedded {fname}")
            except Exception as e:
                print(f"❌ Failed to embed {fname}: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(embeddings, f, indent=2)
    print(f"✅ Saved {len(embeddings)} VC embeddings to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
