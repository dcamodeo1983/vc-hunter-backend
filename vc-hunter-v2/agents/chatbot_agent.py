
import os
import json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from numpy.linalg import norm

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_PATH = "data/embeddings/chatbot_embeddings.json"

def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def retrieve_relevant_passages(query_embedding, top_k=10, doc_type=None):
    with open(EMBED_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)

    scored = []
    for doc in docs:
        if doc_type and doc["type"] != doc_type:
            continue
        similarity = cosine_similarity(query_embedding, doc["embedding"])
        scored.append((similarity, doc))

    top_matches = sorted(scored, reverse=True, key=lambda x: x[0])[:top_k]
    return [match[1] for match in top_matches]

def ask_chatgpt(query, context_chunks):
    context = "\n\n---\n\n".join(
        f"{c['type'].upper()} - {c['vc_name']}:\n{c['tagged_text']}" for c in context_chunks
    )
    prompt = f"""You are an expert on venture capital firm behavior. Use the context below to answer the question.

Context:
{context}

Question: {query}
Answer:
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def main():
    print("🔍 Ask a question about any VC firm (press Enter to quit):")
    while True:
        query = input("> ").strip()
        if not query:
            print("👋 Exiting.")
            break

        doc_type = None
        if query.lower().startswith("fusion:"):
            doc_type = "fusion"
            query = query[len("fusion:"):].strip()
        elif query.lower().startswith("thesis:"):
            doc_type = "thesis"
            query = query[len("thesis:"):].strip()

        print("🔄 Embedding your question...")
        query_embedding = get_embedding(query)

        print(f"📚 Retrieving top relevant {doc_type or 'all'} documents...")
        top_chunks = retrieve_relevant_passages(query_embedding, top_k=5, doc_type=doc_type)

        print("💬 Generating response with GPT...")
        answer = ask_chatgpt(query, top_chunks)

        print("\n🧠 Answer:")
        print(answer)
        print("\n---\n")

if __name__ == "__main__":
    main()
