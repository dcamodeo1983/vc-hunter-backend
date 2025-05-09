
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_DIR = "data/embeddings/portfolio_embeddings.json"
VC_DIR = "data/raw/vcs"
OUTPUT_DIR = "data/fusion_docs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_portfolio_summary(vc_name):
    try:
        with open(INPUT_DIR, "r", encoding="utf-8") as f:
            portfolio_data = json.load(f)
            summaries = []
            for item in portfolio_data:
                if item.get("vc_name") == vc_name:
                    summaries.append(item.get("summary", ""))
            return "\n".join(summaries)
    except Exception as e:
        print(f"⚠️ Error loading portfolio for {vc_name}: {e}")
        return ""

def load_thesis_content(vc_name):
    try:
        path = os.path.join(VC_DIR, f"{vc_name}.jsonl")
        with open(path, "r", encoding="utf-8") as f:
            lines = [json.loads(line).get("content", "") for line in f]
        return "\n".join(lines)
    except Exception as e:
        print(f"⚠️ Error loading thesis for {vc_name}: {e}")
        return ""

def generate_fusion(vc_name, thesis, portfolio):
    system_prompt = (
        "You are an expert venture analyst. You will read a VC firm's public statements (thesis) "
        "and compare them with the types of companies they invest in (portfolio) to produce a synthesized behavioral profile. "
        "Be concise and strategic. Provide an integrated summary of how they talk and how they act."
    )

    user_prompt = (
        f"THESIS:\n{thesis}\n\n"
        f"PORTFOLIO SIGNALS:\n{portfolio}\n\n"
        "Write a behavioral intelligence summary of this VC's true investment behavior."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error creating fusion doc for {vc_name}:\n{e}")
        return None

def main():
    vc_names = [f.replace(".jsonl", "") for f in os.listdir(VC_DIR) if f.endswith(".jsonl")]
    for vc in vc_names:
        thesis = load_thesis_content(vc)
        portfolio = load_portfolio_summary(vc)
        if not thesis:
            print(f"⚠️ Skipping {vc}: no thesis data found.")
            continue

        fusion = generate_fusion(vc, thesis, portfolio)
        if fusion:
            with open(f"{OUTPUT_DIR}/{vc}.txt", "w", encoding="utf-8") as f:
                f.write(fusion)
            print(f"✅ Fusion doc written for {vc}")

if __name__ == "__main__":
    main()
