import pickle
import os
import numpy as np
import sqlite3
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load metadata
with open('recipe_models.pkl', 'rb') as f:
    data = pickle.load(f)

recipe_ids = data['recipe_ids']
chunks_dir = data['chunks_dir']

# Detect chunk size
first_chunk = np.load(os.path.join(chunks_dir, 'emb_chunk_0.npy'))
chunk_size = len(first_chunk)
num_chunks = 45

print(f"Chunk size: {chunk_size}, Num chunks: {num_chunks}")

# Load encoder
encoder = SentenceTransformer('all-MiniLM-L6-v2')

# Test query
query = "chicken, tomato, onions, basmati rice, garlic"
print(f"\nSearching for: {query}")

query_emb = encoder.encode([query])

global_top_scores = []
global_top_indices = []

# Search through chunks
for i in range(num_chunks):
    chunk_path = os.path.join(chunks_dir, f'emb_chunk_{i}.npy')
    if not os.path.exists(chunk_path):
        continue
    
    chunk_emb = np.load(chunk_path)
    sims = cosine_similarity(query_emb, chunk_emb)[0]
    
    k_chunk = min(10, len(sims))
    chunk_top_indices = np.argsort(sims)[-k_chunk:][::-1]
    chunk_top_scores = sims[chunk_top_indices]
    
    global_indices = (i * chunk_size) + chunk_top_indices
    
    global_top_scores.extend(chunk_top_scores)
    global_top_indices.extend(global_indices)

# Get global top 10
global_top_scores = np.array(global_top_scores)
global_top_indices = np.array(global_top_indices)

final_top_args = np.argsort(global_top_scores)[-10:][::-1]
final_indices = global_top_indices[final_top_args]
final_scores = global_top_scores[final_top_args]

# Retrieve from DB
conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()

print("\nTop 10 Results:")
for idx, score in zip(final_indices, final_scores):
    if idx < len(recipe_ids):
        r_id = recipe_ids[idx]
        cursor.execute('SELECT name FROM recipes WHERE id = ?', (r_id,))
        row = cursor.fetchone()
        if row:
            print(f"{score:.4f} - {row[0]}")

conn.close()
