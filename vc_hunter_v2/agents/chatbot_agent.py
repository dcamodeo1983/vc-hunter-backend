import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDINGS_FILE = "data/embeddings/vc_hunter_all_embeddings.jsonl"

def load_embeddings(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f]

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_embedding(text, model="text-embedding-3-small"):
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def retrieve_relevant_passages(query_embedding, top_k=5):
    chunks = load_embeddings(EMBEDDINGS_FILE)
    for chunk in chunks:
        chunk["similarity"] = cosine_similarity(query_embedding, chunk["embedding"])
    sorted_chunks = sorted(chunks, key=lambda x: x["similarity"], reverse=True)
    return sorted_chunks[:top_k]

def main():
    print("\n🧠 VC Hunter Terminal Chatbot Ready")
    print("Type your questions about VC firms or strategy. Press Enter with no input to exit.\n")

    while True:
        query = input("🔍 Your question (press Enter to quit):\n> ").strip()
        if not query:
            break

        print("🔄 Embedding your query...")
        query_embedding = get_embedding(query)

        print("📚 Retrieving top relevant documents...")
        top_chunks = retrieve_relevant_passages(query_embedding)

        print("\n💡 Top Relevant Insights:")
        for i, chunk in enumerate(top_chunks, 1):
            print(f"#{i} — {chunk.get('source', 'unknown')}:\n{chunk.get('content', '')[:400]}\n")

if __name__ == "__main__":
    main()
