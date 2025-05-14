
import os
import json
import difflib
from collections import defaultdict

VC_INPUT_PATH = "data/vc_input.json"
CLASSIFIED_PORTFOLIO_DIR = "data/classified/portfolio"
STRATEGY_PROFILE_DIR = "data/strategy_profiles"
OUTPUT_DIR = "data/scores"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_strategy_tags(vc_name):
    path = os.path.join(STRATEGY_PROFILE_DIR, f"{vc_name}.jsonl")
    if not os.path.exists(path):
        print(f"❌ No strategy profile found for {vc_name}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.loads(f.read()).get("strategy_tags", [])
        except Exception as e:
            print(f"❌ Error loading strategy tags for {vc_name}: {e}")
            return []

def resolve_domain_variants(domain):
    base = domain.replace("www.", "")
    return [base, f"www.{base}"]

def match_strategy_to_portfolio(vc_name, strategy_tags, portfolio_domains):
    match_results = []
    missing_domains = []

    for domain in portfolio_domains:
        matched = False
        variants = resolve_domain_variants(domain)
        for variant in variants:
            fpath = os.path.join(CLASSIFIED_PORTFOLIO_DIR, f"{variant}.jsonl")
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            sectors = data.get("sectors", [])
                            score = len(set(sectors) & set(strategy_tags)) / max(len(strategy_tags), 1)
                            match_results.append({
                                "portfolio": variant,
                                "sectors": sectors,
                                "score": round(score, 2),
                                "matched_tags": list(set(sectors) & set(strategy_tags))
                            })
                            matched = True
                            break
                        except Exception as e:
                            print(f"❌ Failed parsing {variant}: {e}")
                if matched:
                    break
        if not matched:
            missing_domains.append(domain)

    return match_results, missing_domains

def main():
    with open(VC_INPUT_PATH, "r", encoding="utf-8") as f:
        vc_data = json.load(f)

    if isinstance(vc_data, list):
        vc_entries = vc_data
    else:
        vc_entries = list(vc_data.values())

    for vc in vc_entries:
        vc_name = vc["name"]
        strategy_tags = get_strategy_tags(vc_name)
        if not strategy_tags:
            print(f"⚠️ Skipping {vc_name}: no strategy tags.")
            continue

        match_results, missing = match_strategy_to_portfolio(vc_name, strategy_tags, vc["portfolio_urls"])
        if not match_results:
            print(f"⚠️ No classified portfolio matches found for {vc_name}")
            continue

        avg_score = round(sum(m["score"] for m in match_results) / len(match_results), 2)
        output = {
            "vc_name": vc_name,
            "strategy_tags": strategy_tags,
            "matches": match_results,
            "missing_portfolios": missing,
            "behavior_consistency_score": avg_score
        }

        outpath = os.path.join(OUTPUT_DIR, f"{vc_name}.json")
        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"✅ Scored {vc_name}: {avg_score}")

    print("🏁 Behavior consistency scoring complete.")

if __name__ == "__main__":
    main()
