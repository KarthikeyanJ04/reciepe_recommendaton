# build_models.py
"""
Save TF-IDF + embeddings to project folder (not temp)
"""

import sqlite3
import pickle
import numpy as np
import torch
from sklearn.feature_extraction.text import HashingVectorizer
from sentence_transformers import SentenceTransformer
from scipy import sparse
from tqdm import tqdm
import gc
import os

DB_FILE = 'recipes.db'
OUTPUT_FILE = 'recipe_models.pkl'
CHUNKS_DIR = 'model_chunks'  # Save in project folder

# Create chunks directory
os.makedirs(CHUNKS_DIR, exist_ok=True)

print("=" * 60)
print("🔧 Building Models (TF-IDF + Embeddings)")
print("=" * 60)

# CUDA
if torch.cuda.is_available():
    device = 'cuda'
    print(f"\n🚀 GPU: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    device = 'cpu'

# Load database
print("\n📚 Loading database...")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM recipes')
total = cursor.fetchone()[0]
print(f"✅ {total:,} recipes")

cursor.execute('SELECT id FROM recipes')
recipe_ids = [r[0] for r in cursor.fetchall()]

# TF-IDF in chunks
print("\n🔍 Building TF-IDF...")
tfidf_vectorizer = HashingVectorizer(
    n_features=2**18,
    ngram_range=(1, 2),
    alternate_sign=False
)

chunk_size = 10000
tfidf_chunks = []

print("   Processing TF-IDF chunks...")
for i in tqdm(range(0, len(recipe_ids), chunk_size), desc="TF-IDF"):
    end_idx = min(i + chunk_size, len(recipe_ids))
    chunk_ids = recipe_ids[i:end_idx]
    
    placeholders = ','.join(['?'] * len(chunk_ids))
    cursor.execute(f'SELECT search_text FROM recipes WHERE id IN ({placeholders})', chunk_ids)
    texts = [r[0] for r in cursor.fetchall()]
    
    chunk_matrix = tfidf_vectorizer.transform(texts)
    tfidf_chunks.append(chunk_matrix)
    
    del texts, chunk_matrix
    gc.collect()

# Combine TF-IDF chunks
print("   Combining TF-IDF chunks...")
tfidf_matrix = sparse.vstack(tfidf_chunks)
del tfidf_chunks
gc.collect()

print(f"✅ TF-IDF shape: {tfidf_matrix.shape}")

# Save TF-IDF to disk
tfidf_file = os.path.join(CHUNKS_DIR, 'tfidf_matrix.npz')
sparse.save_npz(tfidf_file, tfidf_matrix)
print(f"💾 TF-IDF saved: {tfidf_file}")

# Free memory
del tfidf_matrix
gc.collect()

# Embeddings in chunks
print(f"\n🤖 Loading transformer on {device.upper()}...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

batch_size = 64 if device == 'cuda' else 16

print(f"🔄 Creating embeddings (batch={batch_size})...")
emb_chunks = []

for i in tqdm(range(0, len(recipe_ids), chunk_size), desc="Embeddings"):
    end_idx = min(i + chunk_size, len(recipe_ids))
    chunk_ids = recipe_ids[i:end_idx]
    
    placeholders = ','.join(['?'] * len(chunk_ids))
    cursor.execute(f'SELECT search_text FROM recipes WHERE id IN ({placeholders})', chunk_ids)
    texts = [r[0] for r in cursor.fetchall()]
    
    chunk_emb = embedding_model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        device=device
    )
    
    emb_chunks.append(chunk_emb)
    
    del texts, chunk_emb
    gc.collect()
    if device == 'cuda':
        torch.cuda.empty_cache()

conn.close()

# Combine embeddings
print("   Combining embeddings...")
recipe_embeddings = np.vstack(emb_chunks)
del emb_chunks
gc.collect()

print(f"✅ Embeddings shape: {recipe_embeddings.shape}")

# Save embeddings
emb_file = os.path.join(CHUNKS_DIR, 'embeddings.npy')
np.save(emb_file, recipe_embeddings)
print(f"💾 Embeddings saved: {emb_file}")

del recipe_embeddings
gc.collect()

# Save metadata
print("\n💾 Saving model metadata...")
models = {
    'tfidf_vectorizer': tfidf_vectorizer,
    'tfidf_file': tfidf_file,
    'embeddings_file': emb_file,
    'recipe_ids': recipe_ids,
    'chunks_dir': CHUNKS_DIR
}

with open(OUTPUT_FILE, 'wb') as f:
    pickle.dump(models, f, protocol=4)

file_size = os.path.getsize(OUTPUT_FILE) / 1024
print(f"✅ Metadata saved: {OUTPUT_FILE} ({file_size:.1f} KB)")

# Show chunk sizes
tfidf_size = os.path.getsize(tfidf_file) / (1024*1024)
emb_size = os.path.getsize(emb_file) / (1024*1024)

print("\n" + "=" * 60)
print(f"✅ Processed {total:,} recipes!")
print(f"   TF-IDF: {tfidf_size:.0f} MB")
print(f"   Embeddings: {emb_size:.0f} MB")
print(f"   Saved in: {CHUNKS_DIR}/")
print("=" * 60)
