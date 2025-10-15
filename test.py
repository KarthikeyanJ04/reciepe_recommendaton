import pickle
import sqlite3
from scipy.sparse import load_npz

# Check TF-IDF size
tfidf = load_npz('models/recipe_tfidf_matrix.npz')
print(f"TF-IDF matrix rows: {tfidf.shape[0]:,}")

# Check database size
conn = sqlite3.connect('models/recipes.db')
cursor = conn.execute("SELECT COUNT(*) FROM recipes")
db_count = cursor.fetchone()[0]
conn.close()
print(f"Database recipes: {db_count:,}")

# Check embeddings size
import numpy as np
embeddings = np.load('models/recipe_embeddings.npy', mmap_mode='r')
print(f"Embeddings rows: {embeddings.shape[0]:,}")

print("\n" + "="*60)
if tfidf.shape[0] == db_count == embeddings.shape[0]:
    print("✅ ALL SIZES MATCH - models are aligned")
else:
    print("❌ SIZE MISMATCH - models are NOT aligned!")
    print("\nYou need to:")
    print("  1. python retrain_tfidf.py")
    print("  2. python retrain_embeddings_final.py")
