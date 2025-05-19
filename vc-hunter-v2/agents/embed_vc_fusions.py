
import os
import json
import boto3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
REGION = "us-east-1"
MODEL_ID = "amazon.titan-embed-text-v2:0"
INPUT_DIR = "data/fusion_docs"
OUTPUT_FILE = "data/embeddings/vc_embeddings.json"

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

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    client = get_bedrock_client()
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
                vector = embed_text(text, client)
                embeddings.append({
                    "vc_name": fname.replace(".txt", ""),
                    "type": "vc_fusion",
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
