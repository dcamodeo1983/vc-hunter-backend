
import os
import json
import openai

# 🔐 Set OpenAI API key (Line 14)
openai.api_key = os.getenv("OPENAI_API_KEY")

VC_RAW_DIR = "data/raw/vcs"
PORTFOLIO_RAW_DIR = "data/raw/portfolio"
OUTPUT_DIR = "data/fusion_docs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_domain(url):
    return url.split("//")[-1].split("/")[0]

def build_fusion_doc(vc_name):
    vc_file = os.path.join(VC_RAW_DIR, f"{vc_name}.jsonl")
    if not os.path.exists(vc_file):
        print(f"❌ No VC thesis found for {vc_name}")
        return

    # Load VC thesis
    with open(vc_file, "r", encoding="utf-8") as f:
        thesis_lines = [json.loads(line).get("content", "") for line in f if line.strip()]
    thesis = "\n".join(thesis_lines)

    # Load related portfolios
    related_texts = []
    for fname in os.listdir(PORTFOLIO_RAW_DIR):
        if fname.endswith(".jsonl"):
            with open(os.path.join(PORTFOLIO_RAW_DIR, fname), "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    if data.get("vc_linked") and vc_name in data["vc_linked"]:
                        content = data.get("content", "")
                        if content:
                            related_texts.append(content)

    portfolios_combined = "\n---\n".join(related_texts[:5])  # limit for token safety

    prompt = f"""
You are analyzing a venture capital firm. Below is their self-described thesis and a sample of companies they have invested in.

[VC Thesis]
{thesis}

[Portfolio Behavior Sample]
{portfolios_combined}

Write a summary that fuses what the VC says they do with what their actual investments suggest.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a VC research analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=800
        )
        fusion_text = response["choices"][0]["message"]["content"]
        with open(os.path.join(OUTPUT_DIR, f"{vc_name}.txt"), "w", encoding="utf-8") as out:
            out.write(fusion_text)
        print(f"✅ Fusion doc written for {vc_name}")
    except Exception as e:
        print(f"❌ Error creating fusion doc for {vc_name}: {e}")

def main():
    for fname in os.listdir(VC_RAW_DIR):
        if fname.endswith(".jsonl"):
            vc_name = fname.replace(".jsonl", "")
            build_fusion_doc(vc_name)

if __name__ == "__main__":
    main()
