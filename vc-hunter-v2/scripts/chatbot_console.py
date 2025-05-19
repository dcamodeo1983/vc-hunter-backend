import os
import json
import numpy as np
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.llm_client import llm_chat, get_embedding, count_tokens
from utils.vector_utils import cosine_similarity

load_dotenv()

EMBED_PATH = "data/embeddings/vc_hunter_all_embeddings.jsonl"


def retrieve_relevant_passages(query_embedding, top_k=5):
    if not os.path.exists(EMBED_PATH):
        print(f"❌ Embedding file not found: {EMBED_PATH}")
        return []

    with open(EMBED_PATH, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]

    for chunk in chunks:
        chunk["similarity"] = cosine_similarity(query_embedding, chunk["embedding"])

    return sorted(chunks, key=lambda x: x["similarity"], reverse=True)[:top_k]


def ask_chatgpt(query, context_chunks):
    context = "\n\n---\n\n".join(
        f"{c['type'].upper()} - {c['vc_name']}:\n{c.get('tagged_text') or c.get('content')}"
        for c in context_chunks
    )
    prompt = f"""You are a VC intelligence assistant. Based on the following information:

{context}

Answer the question: {query}.

If uncertain, say so explicitly."""

    print("💬 Querying LLM...")
    return llm_chat([{"role": "user", "content": prompt}])


def main():
    print("\n🧠 VC Hunter Terminal Chatbot Ready")
    print("Type your questions about VC firms or strategy. Press Enter with no input to exit.\n")
    while True:
        query = input("🔍 Your question (press Enter to quit):\n> ").strip()
        if not query:
            print("👋 Exiting chatbot.")
            break

        print("🔄 Embedding your query...")
        query_embedding = get_embedding(query)
        print(f"📊 [get_embedding] Tokens used: {count_tokens(query)}")

        print("📚 Retrieving top relevant documents...")
        top_chunks = retrieve_relevant_passages(query_embedding)
        if not top_chunks:
            print("⚠️ No relevant documents found.")
            continue

        print("💬 Generating response with GPT...\n")
        answer = ask_chatgpt(query, top_chunks)
        print(f"\n🧠 Answer:\n{answer}\n")


if __name__ == "__main__":
    main()
