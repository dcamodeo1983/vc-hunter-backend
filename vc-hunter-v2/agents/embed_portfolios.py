
import os
import json
import boto3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
REGION = "us-east-1"
MODEL_ID = "text-embedding-3-small"
INPUT_DIR = "data/raw/portfolio"
OUTPUT_FILE = "data/embeddings/portfolio_embeddings.json"

def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name=REGION)

def embed_text(text, client):
    body = json.dumps({ "inputText": text[:8000] })
    response = client.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body
    )
    response_body = json.loads(response["body"].read())
    return response_body["embedding"]

def process_all():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    client = get_bedrock_client()
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
                    vector = embed_text(text, client)
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
