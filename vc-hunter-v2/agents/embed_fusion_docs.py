
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FUSION_DIR = "data/fusions"
THESIS_DIR = "data/raw/vcs"
OUTPUT_PATH = "data/embeddings/chatbot_embeddings.json"

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def tag_text(vc_name, content, doc_type):
    if doc_type == "fusion":
        return f"TYPE: FUSION\nVC: {vc_name}\nSUMMARY:\n{content.strip()}"
    else:
        return f"TYPE: THESIS\nVC: {vc_name}\nCONTENT:\n{content.strip()}"

def embed_directory(directory, doc_type):
    records = []
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
    all_records.extend(embed_directory(FUSION_DIR, "fusion"))
    all_records.extend(embed_directory(THESIS_DIR, "thesis"))

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)

    print(f"✅ Embedded {len(all_records)} items to {OUTPUT_PATH}")

if __name__ == "__main__":
    embed_all()
