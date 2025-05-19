import os
import json

STRATEGY_DIR = "data/classified/strategy"
OUTPUT_FILE = "data/processed/vc_profiles.jsonl"

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    for fname in os.listdir(STRATEGY_DIR):
        if not fname.endswith(".json"):
            continue
        vc_name = fname.replace(".json", "")
        fpath = os.path.join(STRATEGY_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            summary = data.get("summary", "")
            if summary:
                out.write(json.dumps({"vc_name": vc_name, "summary": summary}) + "\n")
            else:
                print(f"⚠️ Missing summary in {vc_name}")
        except Exception as e:
            print(f"❌ Error processing {fname}: {e}")

print("✅ vc_profiles.jsonl rebuilt.")
