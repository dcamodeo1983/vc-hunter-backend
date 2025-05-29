import json

INPUT_JSON = "data/embeddings/vc_embeddings.json"
OUTPUT_JSONL = "data/embeddings/vc_hunter_all_embeddings.jsonl"

with open(INPUT_JSON, "r") as f:
    records = json.load(f)

with open(OUTPUT_JSONL, "w") as out:
    for record in records:
        record.setdefault("content", record.get("text", ""))
        record.setdefault("source", record.get("vc_name", "unknown"))
        out.write(json.dumps(record) + "\n")

print(f"✅ Rebuilt: {OUTPUT_JSONL}")
