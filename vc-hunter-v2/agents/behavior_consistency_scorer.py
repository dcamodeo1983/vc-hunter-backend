import os
import json
from statistics import mean

INPUT_DIR = "data/classified/portfolio"
FUSION_DIR = "data/fusions"
OUTPUT_DIR = "data/behavior_scores"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def calculate_overlap(vc_name):
    try:
        with open(os.path.join(FUSION_DIR, f"{vc_name}.jsonl"), "r", encoding="utf-8") as f:
            fusion_data = [json.loads(line) for line in f]
        with open(os.path.join(INPUT_DIR, f"{vc_name}.jsonl"), "r", encoding="utf-8") as f:
            portfolio_data = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"❌ Missing data for {vc_name}")
        return

    strategy_sectors = set()
    for record in fusion_data:
        strategy_sectors.update(record.get("sectors", []))

    overlaps = []
    for company in portfolio_data:
        company_sectors = set(company.get("sectors", []))
        if company_sectors:
            overlap = len(strategy_sectors & company_sectors) / len(company_sectors)
            overlaps.append(overlap)

    score = round(mean(overlaps), 2) if overlaps else 0.0
    result = {"vc_name": vc_name, "consistency_score": score}
    with open(os.path.join(OUTPUT_DIR, f"{vc_name}.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Scored {vc_name}: {score}")

def main():
    vc_names = [fname.replace(".jsonl", "") for fname in os.listdir(FUSION_DIR) if fname.endswith(".jsonl")]
    for vc in vc_names:
        calculate_overlap(vc)

if __name__ == "__main__":
    main()
