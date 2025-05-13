import json
import os
from collections import defaultdict
from difflib import SequenceMatcher

STRATEGY_DIR = "data/strategy_profiles"
PORTFOLIO_DIR = "data/classified/portfolio"
VC_INPUT_PATH = "data/vc_input.json"
OUTPUT_DIR = "data/behavior_scores"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load VC input map to know which companies belong to which VC
with open(VC_INPUT_PATH, "r") as f:
    vc_input = json.load(f)

# Build mapping from domain -> VC name
domain_to_vc = {}
for vc in vc_input:
    for url in vc.get("portfolio_urls", []):
        domain = url.replace("https://", "").replace("http://", "").strip("/").lower()
        domain_to_vc[domain] = vc["name"]

# Load all classified portfolio files
portfolio_sector_map = defaultdict(list)
for fname in os.listdir(PORTFOLIO_DIR):
    if not fname.endswith(".jsonl"):
        continue
    domain = fname.replace(".jsonl", "")
    vc_name = domain_to_vc.get(domain)
    if not vc_name:
        continue
    with open(os.path.join(PORTFOLIO_DIR, fname), "r") as f:
        for line in f:
            record = json.loads(line)
            if "sectors" in record:
                portfolio_sector_map[vc_name].extend(record["sectors"])

# Normalize and count sector frequency
vc_sector_summary = {
    vc: {
        "sector_counts": {s: portfolio.count(s) for s in set(portfolio)},
        "total": len(portfolio)
    }
    for vc, portfolio in portfolio_sector_map.items()
}

# Run comparison against strategy tags
def match_score(strategy_tag, sector):
    return SequenceMatcher(None, strategy_tag.lower(), sector.lower()).ratio()

for fname in os.listdir(STRATEGY_DIR):
    if not fname.endswith(".jsonl"):
        continue
    vc_name = fname.replace(".jsonl", "")
    strategy_path = os.path.join(STRATEGY_DIR, fname)
    if vc_name not in vc_sector_summary:
        print(f"❌ Missing classified portfolio data for {vc_name}")
        continue

    with open(strategy_path, "r") as f:
        strategy_tags = [json.loads(line)["tag"] for line in f]

    sector_counts = vc_sector_summary[vc_name]["sector_counts"]
    total_investments = vc_sector_summary[vc_name]["total"]

    match_results = []
    for tag in strategy_tags:
        best_match = max(sector_counts.items(), key=lambda kv: match_score(tag, kv[0]))
        match_results.append({
            "tag": tag,
            "matched_sector": best_match[0],
            "sector_count": best_match[1],
            "score": match_score(tag, best_match[0])
        })

    avg_score = sum(m["score"] for m in match_results) / len(match_results)

    output = {
        "vc_name": vc_name,
        "strategy_tags": strategy_tags,
        "total_investments": total_investments,
        "sector_counts": sector_counts,
        "match_results": match_results,
        "average_alignment_score": round(avg_score, 3)
    }

    with open(os.path.join(OUTPUT_DIR, f"{vc_name}.json"), "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Scored {vc_name}: {round(avg_score, 3)}")

print("🏁 Behavior consistency scoring complete.")
