# bedrock_embedder_agent.py

import boto3
import json
from typing import List, Dict

# Optional: switch this to use environment variables or config file if needed
REGION = "us-east-1"
MODEL_ID = "amazon.titan-embed-text-v2:0"

def get_bedrock_client():
    """
    Returns a Boto3 Bedrock Runtime client for the given region.
    """
    return boto3.client("bedrock-runtime", region_name=REGION)

def embed_text(text: str) -> List[float]:
    client = get_bedrock_client()
    payload = json.dumps({"inputText": text})  # 👈 single string only

    response = client.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=payload
    )

    body = response['body'].read()
    result = json.loads(body)
    return result['embedding']



def embed_all(jsonl_path: str, output_path: str):
    """
    Reads a .jsonl file with VC content, embeds each item, and saves embeddings to output.
    """
    embeddings = []

    with open(jsonl_path, "r", encoding="utf-8") as infile:
        for line in infile:
            record = json.loads(line)
            content = record.get("content", "")
            vector = embed_text(content)
            embeddings.append({
                "source": record.get("source"),
                "type": record.get("type"),
                "embedding": vector
            })

    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(embeddings, outfile, indent=2)

    print(f"✅ Saved {len(embeddings)} embeddings to {output_path}")

# Example usage (uncomment to run standalone)
embed_all("data/raw/vc_scraped_data.jsonl", "data/embeddings/vc_embeddings.json")
