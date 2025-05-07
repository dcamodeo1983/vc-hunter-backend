
# validate_embeddings.py

import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sklearn.decomposition import PCA
    import matplotlib.pyplot as plt
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

# Load embeddings
with open("data/embeddings/vc_embeddings.json", "r") as f:
    data = json.load(f)

print(f"✅ Loaded {len(data)} embeddings.\n")

# Inspect each embedding
for i, item in enumerate(data):
    print(f"{i+1}. Source: {item['source']} | Type: {item['type']}")
    print(f"   Length: {len(item['embedding'])}")
    print(f"   First 5 values: {item['embedding'][:5]}")
    print()

# Check similarity between first 2
if len(data) >= 2:
    vec1 = np.array(data[0]["embedding"]).reshape(1, -1)
    vec2 = np.array(data[1]["embedding"]).reshape(1, -1)
    score = cosine_similarity(vec1, vec2)[0][0]
    print(f"🔍 Cosine similarity between VC #1 and VC #2: {score:.4f}")
else:
    print("ℹ️ Not enough data points to compute cosine similarity.")

# Optional: 2D Plot
if PLOTTING_AVAILABLE and len(data) >= 2:
    vectors = np.array([item["embedding"] for item in data])
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(vectors)

    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 6))
    plt.scatter(reduced[:, 0], reduced[:, 1], c='blue')
    for i, item in enumerate(data):
        plt.text(reduced[i, 0], reduced[i, 1], f"{i+1}", fontsize=8)
    plt.title("🧭 VC Embeddings (2D PCA)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("📉 Skipping plot (matplotlib or scikit-learn not installed).")
