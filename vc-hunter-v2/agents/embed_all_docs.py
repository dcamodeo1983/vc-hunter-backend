
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OUTPUT_PATH = "data/embeddings/chatbot_embeddings.json"
DIRS = {
    "fusion": "data/fusions",
    "thesis": "data/raw/vcs",
    "portfolio": "data/raw/portfolio"
}

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def tag_text(vc_name, content, doc_type):
    return f"TYPE: {doc_type.upper()}\nVC: {vc_name}\nCONTENT:\n{content.strip()}"

def embed_directory(directory, doc_type):
    records = []
    if not os.path.exists(directory):
        return records
    for fname in os.listdir(directory):
        if not fname.endswith(".jsonl"):
            continue
        vc_name = fname.replace(".jsonl", "")
        path = os.path.join(directory, fname)
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            data = json.loads(line)
            content = data.get("content", "")
            if not content.strip():
                continue
            tagged = tag_text(vc_name, content, doc_type)
            embedding = get_embedding(tagged)
            records.append({
                "vc_name": vc_name,
                "type": doc_type,
                "tagged_text": tagged,
                "embedding": embedding
            })
    return records

def embed_all():
    all_records = []
    for doc_type, directory in DIRS.items():
        all_records.extend(embed_directory(directory, doc_type))
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)
    print(f"✅ Embedded {len(all_records)} tagged documents to {OUTPUT_PATH}")

if __name__ == "__main__":
    embed_all()
