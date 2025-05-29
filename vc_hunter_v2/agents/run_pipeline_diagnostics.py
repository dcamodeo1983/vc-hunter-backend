import subprocess
import os
import sys  # ✅ Add this line

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

agents = [
    ("Sector Classifier", "python3 agents/sector_classifier_agent.py"),
    ("Strategy Profiler", "python3 agents/strategy_profiler_agent.py"),
    ("Embed All Docs", "python3 agents/embed_all_docs.py"),
    ("Behavior Consistency Scorer", "python3 agents/behavior_consistency_scorer.py"),
]

print("🔍 Running VC Hunter Diagnostic Pipeline...\n")

for label, cmd in agents:
    print(f"🛠️  {label}:\n{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"❌ Error in {label}:\n{result.stderr.strip()}")
    except Exception as e:
        print(f"⚠️ Exception in {label}: {e}")
    print("\n" + "-"*60 + "\n")

print("✅ Pipeline diagnostics complete.")
