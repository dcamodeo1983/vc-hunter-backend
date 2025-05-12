
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_PATH = "data/embeddings/chatbot_embeddings.json"

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def embed_query(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def retrieve_relevant_passages(query_embedding, top_k=5):
    with open(EMBED_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    for record in records:
        record["similarity"] = cosine_similarity(query_embedding, record["embedding"])

    sorted_records = sorted(records, key=lambda x: x["similarity"], reverse=True)
    return sorted_records[:top_k]

def ask_chatgpt(query, context_chunks):
    context = "\n\n---\n\n".join(
        f"{c['type'].upper()} - {c['vc_name']}:\n{c['tagged_text']}" for c in context_chunks
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions about venture capital firms and their investments."},
            {"role": "user", "content": f"Using the following information:

{context}

Answer this question:
{query}"}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

def main():
    print("\n🔍 Ask a question about any VC firm (press Enter to quit):")
    while True:
        query = input("> ").strip()
        if not query:
            break
        print("🔄 Embedding your question...")
        query_embedding = embed_query(query)
        print("📚 Retrieving top relevant documents...")
        top_chunks = retrieve_relevant_passages(query_embedding, top_k=6)
        print("💬 Generating response with GPT...\n")
        answer = ask_chatgpt(query, top_chunks)
        print(f"\n🧠 Answer:\n{answer}\n")

if __name__ == "__main__":
    main()
