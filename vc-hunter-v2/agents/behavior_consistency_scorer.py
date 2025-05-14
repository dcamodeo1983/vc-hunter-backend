import os
import json
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from utils.llm_client import llm_chat

VC_INPUT = "data/vc_input.json"
CLASSIFIED_DIR = "data/classified/portfolio"
STRATEGY_DIR = "data/strategy_profiles"

def score_alignment(strategy_tags, sector_list):
    prompt = f"""
    Compare the strategy tags below with the list of sectors from a portfolio company.
    Strategy Tags: {strategy_tags}
    Portfolio Sectors: {sector_list}

    Respond with a single float between 0 and 1 reflecting alignment (1 = perfect alignment).
    """
    try:
        return float(llm_chat(prompt))
    except:
        return 0.0

def main():
    with open(VC_INPUT, "r", encoding="utf-8") as f:
        vcs = json.load(f)

    for vc in vcs:
        name = vc["name"]
        strategy_path = os.path.join(STRATEGY_DIR, f"{name}.jsonl")
        if not os.path.exists(strategy_path):
            print(f"❌ No strategy profile found for {name}")
            continue

        with open(strategy_path, "r", encoding="utf-8") as f:
            strategy_data = json.loads(f.readline())
            strategy_tags = strategy_data.get("strategy_tags", [])
            if not strategy_tags:
                print(f"⚠️ Skipping {name}: no strategy tags.")
                continue

        match_results = []
        for p_url in vc.get("portfolio_urls", []):
            domain = p_url.split("//")[-1].replace("/", "")
            portfolio_path = os.path.join(CLASSIFIED_DIR, f"{domain}.jsonl")
            if not os.path.exists(portfolio_path):
                print(f"⚠️ Missing classified portfolio data for {domain}")
                continue

            with open(portfolio_path, "r", encoding="utf-8") as f:
                for line in f:
                    item = json.loads(line)
                    score = score_alignment(strategy_tags, item.get("sectors", []))
                    match_results.append({"portfolio": domain, "score": score})

        if match_results:
            avg_score = sum(m["score"] for m in match_results) / len(match_results)
            print(f"✅ {name} behavior consistency score: {avg_score:.2f}")
        else:
            print(f"⚠️ No classified portfolio matches found for {name}")
    print("🏁 Behavior consistency scoring complete.")

if __name__ == "__main__":
    main()
