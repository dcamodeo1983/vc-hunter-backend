# chatbot_console.py

import os
import json
import numpy as np
from utils.llm_client import get_embedding, llm_chat

EMBEDDING_PATH = "vc-hunter-v2/data/embeddings/vc_embeddings.json"

class StrategyProfilerAgent:
    def __init__(self, input_dir="vc-hunter-v2/data/raw/vcs", output_dir="vc-hunter-v2/data/classified/strategy"):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self):
        # Loop through files in input_dir and call OpenAI to summarize
        pass  # ← placeholder logic


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve_relevant_passages(query_embedding, top_k=3):
    if not os.path.exists(EMBEDDING_PATH):
        print(f"❌ Embedding file not found: {EMBEDDING_PATH}")
        return []

    with open(EMBEDDING_PATH, "r", encoding="utf-8") as f:
        vectors = json.load(f)

    for chunk in vectors:
        chunk["similarity"] = cosine_similarity(query_embedding, chunk["embedding"])

    ranked = sorted(vectors, key=lambda x: x["similarity"], reverse=True)
    return ranked[:top_k]


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

        if not top_chunks:
            print("⚠️ No relevant documents found.")
            continue

if __name__ == "__main__":
    StrategyProfilerAgent().run()


