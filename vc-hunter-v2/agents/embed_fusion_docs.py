
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VC_DIR = "data/raw/vcs"
FUSION_DIR = "data/fusion_docs"
OUTPUT_PATH = "data/embeddings/chatbot_embeddings.json"

os.makedirs("data/embeddings", exist_ok=True)

def embed_text(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def main():
    embedded_docs = []

    # Embed thesis content
    for filename in os.listdir(VC_DIR):
        if filename.endswith(".jsonl"):
            vc_name = filename.replace(".jsonl", "")
            with open(os.path.join(VC_DIR, filename), "r", encoding="utf-8") as f:
                lines = [json.loads(line).get("content", "") for line in f]
            full_text = "\n".join(lines).strip()
            if full_text:
                embedding = embed_text(full_text)
                embedded_docs.append({
                    "vc_name": vc_name,
                    "type": "thesis",
                    "content": full_text,
                    "embedding": embedding
                })

    # Embed fusion summaries
    for filename in os.listdir(FUSION_DIR):
        if filename.endswith(".txt"):
            vc_name = filename.replace(".txt", "")
            with open(os.path.join(FUSION_DIR, filename), "r", encoding="utf-8") as f:
                text = f.read().strip()
            if text:
                embedding = embed_text(text)
                embedded_docs.append({
                    "vc_name": vc_name,
                    "type": "fusion",
                    "content": text,
                    "embedding": embedding
                })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(embedded_docs, f, indent=2)

    print(f"✅ Embedded {len(embedded_docs)} items to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
