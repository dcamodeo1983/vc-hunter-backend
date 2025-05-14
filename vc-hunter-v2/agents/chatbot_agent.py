import os
import json
import numpy as np
from dotenv import load_dotenv
from utils.llm_client import llm_chat
from utils.embed_utils import get_embedding, cosine_similarity

load_dotenv()
EMBED_PATH = "data/embeddings/chatbot_embeddings.json"

def retrieve_relevant_passages(query_embedding, top_k=5):
    with open(EMBED_PATH, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f]

    for chunk in chunks:
        chunk["similarity"] = cosine_similarity(query_embedding, chunk["embedding"])

    return sorted(chunks, key=lambda x: x["similarity"], reverse=True)[:top_k]

def ask_chatgpt(query, context_chunks):
    context = "\n\n---\n\n".join(
        f"{c['type'].upper()} - {c['vc_name']}:\n{c.get('tagged_text') or c.get('content')}" for c in context_chunks
    )
    prompt = f"""Using the following information:

{context}

Answer the question: {query}"""
    return llm_chat(prompt)

def main():
    while True:
        query = input("\n🔍 Ask a question about any VC firm (press Enter to quit):\n> ").strip()
        if not query:
            break
        print("🔄 Embedding your question...")
        embedding = get_embedding(query)
        print("📚 Retrieving top relevant documents...")
        top_chunks = retrieve_relevant_passages(embedding, top_k=5)
        print("💬 Generating response with GPT...\n")
        answer = ask_chatgpt(query, top_chunks)
        print(f"\n🧠 Answer:\n{answer}")

if __name__ == "__main__":
    main()
