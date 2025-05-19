import os
import json
import sys
from dotenv import load_dotenv

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm_client import llm_chat, get_embedding
from utils.embed_utils import cosine_similarity

load_dotenv()

EMBED_PATH = "data/embeddings/vc_embeddings.jsonl"  # New embedding location


def retrieve_relevant_passages(query_embedding, top_k=5):
    with open(EMBED_PATH, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f]

    for chunk in chunks:
        chunk["similarity"] = cosine_similarity(query_embedding, chunk["embedding"])

    return sorted(chunks, key=lambda x: x["similarity"], reverse=True)[:top_k]


def ask_chatgpt(query, context_chunks):
    context = "\n\n---\n\n".join(
        f"{c['type'].upper()} - {c['vc_name']}:\n{c.get('tagged_text') or c.get('content', '')}"
        for c in context_chunks
    )
    prompt = f"""You are an expert analyst helping founders understand venture capital firms.

Using the following information:

{context}

Answer the question: "{query}"
"""
    return llm_chat([{"role": "user", "content": prompt}])


def main():
    print("\n🤖 VC Hunter Chatbot is ready. Ask about any firm, strategy, or trend.\n")
    while True:
        query = input("🔍 Your question (press Enter to quit):\n> ").strip()
        if not query:
            print("👋 Exiting.")
            break
        print("🔄 Embedding your query...")
        query_embedding = get_embedding(query)
        print("📚 Retrieving top relevant documents...")
        top_chunks = retrieve_relevant_passages(query_embedding)
        print("💬 Generating response...\n")
        response = ask_chatgpt(query, top_chunks)
        print(f"\n🧠 Answer:\n{response}\n")


if __name__ == "__main__":
    main()
