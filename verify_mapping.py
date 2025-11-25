import pickle
import os
import numpy as np
import sqlite3
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def verify():
    print("="*60)
    print("VERIFYING MAPPING INTEGRITY")
    print("="*60)

    # 1. Load Metadata
    if not os.path.exists('recipe_models.pkl'):
        print("[ERROR] recipe_models.pkl not found!")
        return

    with open('recipe_models.pkl', 'rb') as f:
        data = pickle.load(f)
    
    recipe_ids = data.get('recipe_ids', [])
    chunks_dir = data.get('chunks_dir', 'model_chunks')
    
    # Detect chunk size
    first_chunk_path = os.path.join(chunks_dir, 'emb_chunk_0.npy')
    if not os.path.exists(first_chunk_path):
        print("[ERROR] No chunks found.")
        return
    
    first_chunk = np.load(first_chunk_path)
    chunk_size = len(first_chunk)
    print(f"Detected chunk size: {chunk_size}")

    # 2. Load Encoder
    print("Loading encoder...")
    encoder = SentenceTransformer('all-MiniLM-L6-v2')

    # 3. Test a few indices
    test_indices = [0, 10, 100, 1000, 5000]
    
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()

    for idx in test_indices:
        if idx >= len(recipe_ids):
            continue
            
        # A. Get Expected Recipe
        r_id = recipe_ids[idx]
        cursor.execute('SELECT name, search_text FROM recipes WHERE id = ?', (r_id,))
        row = cursor.fetchone()
        if not row:
            print(f"Index {idx}: ID {r_id} not found in DB.")
            continue
            
        name, text = row
        print(f"\n--- Testing Index {idx} (ID: {r_id}) ---")
        print(f"Expected Name: {name}")
        
        # B. Get Stored Embedding
        chunk_idx = idx // chunk_size
        local_idx = idx % chunk_size
        
        chunk_path = os.path.join(chunks_dir, f'emb_chunk_{chunk_idx}.npy')
        if not os.path.exists(chunk_path):
            print(f"Chunk {chunk_idx} missing.")
            continue
            
        # Optimization: Don't reload chunk if same
        # For this script, we just load it.
        chunk_emb = np.load(chunk_path)
        stored_vector = chunk_emb[local_idx].reshape(1, -1)
        
        # C. Generate Fresh Embedding
        fresh_vector = encoder.encode([text])
        
        # D. Compare
        sim = cosine_similarity(stored_vector, fresh_vector)[0][0]
        print(f"Similarity: {sim:.4f}")
        
        if sim > 0.9:
            print("✅ MATCH")
        else:
            print("❌ MISMATCH - The stored embedding does NOT match the recipe text.")

    conn.close()

if __name__ == "__main__":
    verify()
