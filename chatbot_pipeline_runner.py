# chatbot_pipeline_runner.py

import os
import time
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "vc-hunter-v2"))

from agents.vc_scraper_agent import VCScraperAgent
from agents.strategy_profiler_agent import StrategyProfilerAgent
from agents.behavior_consistency_scorer import BehaviorScorer
from agents.vc_fusion_builder import FusionBuilder
from agents.embed_vc_fusions import embed_text
from utils.llm_client import get_embedding
import json

# Constants
RAW_VC_DIR = "vc-hunter-v2/data/raw/vcs"
STRATEGY_DIR = "vc-hunter-v2/data/classified/strategy"
BEHAVIOR_DIR = "vc-hunter-v2/data/analysis/behavior_consistency"
FUSION_DIR = "vc-hunter-v2/data/fusion_docs"
EMBEDDINGS_OUTPUT = "vc-hunter-v2/data/embeddings/vc_embeddings.json"
VC_PROFILES_PATH = "vc-hunter-v2/data/processed/vc_profiles.jsonl"

# Hardcoded VC URLs for now
vc_urls = [
    "https://8vc.com",
    "https://www.sequoiacap.com",
    "https://www.az16.com"
]

def run_full_pipeline():
    print("\n🧠 VC Hunter Diagnostic Chatbot Pipeline Starting...")

    # Step 1: Scrape VC websites
    print("\n🔍 Scraping VC websites...")
    scraper = VCScraperAgent(vc_urls=vc_urls, output_dir=RAW_VC_DIR)
    scraper.run()

    # Step 2: Profile strategies
    print("\n📄 Generating strategy profiles...")
    profiler = StrategyProfilerAgent(input_dir=RAW_VC_DIR, output_dir=STRATEGY_DIR)
    profiler.run()

    # Step 3: Score behavior
    print("\n📊 Scoring behavioral consistency...")
    scorer = BehaviorScorer(strategy_path=STRATEGY_DIR, profiles_path=VC_PROFILES_PATH, output_dir=BEHAVIOR_DIR)
    scorer.run()

    # Step 4: Build fusion docs
    print("\n🧬 Building fusion docs (site content only)...")
    fusion_builder = FusionBuilder(vc_dir=RAW_VC_DIR, output_dir=FUSION_DIR)
    fusion_builder.run()

    # Step 5: Embed fusion docs
    print("\n📡 Embedding fusion documents...")
    os.makedirs(os.path.dirname(EMBEDDINGS_OUTPUT), exist_ok=True)
    embeddings = []
    for fname in os.listdir(FUSION_DIR):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(FUSION_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if not text:
                continue
            try:
                vector = embed_text(text)
                if len(vector) != 1536:
                    raise ValueError(f"Invalid embedding length: {len(vector)}")
                embeddings.append({
                    "vc_name": fname.replace(".txt", ""),
                    "type": "vc_fusion",
                    "embedding": vector
                })
                print(f"✅ Embedded {fname}")
            except Exception as e:
                print(f"❌ Failed to embed {fname}: {e}")
    with open(EMBEDDINGS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(embeddings, f, indent=2)
    print(f"\n✅ Saved {len(embeddings)} embeddings to {EMBEDDINGS_OUTPUT}")

    # Step 6: Launch chatbot
    print("\n💬 Launching VC Hunter chatbot...")
    os.system("python vc-hunter-v2/scripts/chatbot_console.py")

if __name__ == "__main__":
    run_full_pipeline()
