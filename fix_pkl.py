# quick_fix_pkl.py - Regenerate pickle from existing chunks

import pickle
import os
from sklearn.feature_extraction.text import HashingVectorizer
import sqlite3

# Get recipe IDs from database
conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()
cursor.execute('SELECT id FROM recipes ORDER BY id')
recipe_ids = [r[0] for r in cursor.fetchall()]
conn.close()

# Create vectorizer
tfidf_vectorizer = HashingVectorizer(
    n_features=2**18,
    ngram_range=(1, 2),
    alternate_sign=False
)

# Get chunk info from files
chunks_dir = 'model_chunks'
chunk_files = [f for f in os.listdir(chunks_dir) if f.startswith('tfidf_chunk_') and f.endswith('.npz')]
chunk_indices = [int(f.split('_')[-1].split('.')[0]) for f in chunk_files]
num_chunks = max(chunk_indices) + 1
chunk_size = 50000

# Save
models = {
    'tfidf_vectorizer': tfidf_vectorizer,
    'recipe_ids': recipe_ids,
    'num_chunks': num_chunks,
    'chunk_size': chunk_size,
    'chunks_dir': chunks_dir
}

with open('recipe_models.pkl', 'wb') as f:
    pickle.dump(models, f, protocol=4)

print(f"✅ Created recipe_models.pkl")
print(f"   Recipes: {len(recipe_ids):,}")
print(f"   Chunks: {num_chunks}")
