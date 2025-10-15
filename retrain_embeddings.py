# ============================================================================
# RETRAIN EMBEDDINGS - MEMORY EFFICIENT VERSION (6GB VRAM)
# Saves embeddings incrementally to avoid RAM exhaustion
# ============================================================================

import pandas as pd
import numpy as np
import sqlite3
import time
import gc
import os
from sentence_transformers import SentenceTransformer
import torch

print("="*80)
print("RETRAINING EMBEDDINGS ON LOCAL GPU (MEMORY EFFICIENT)")
print("="*80)

# Check GPU
print(f"\nGPU available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

# ============================================================================
# PART 1: LOAD RECIPES FROM DATABASE
# ============================================================================

print("\n" + "="*80)
print("LOADING RECIPES FROM DATABASE")
print("="*80)

conn = sqlite3.connect('models/recipes.db')

print("\nLoading all recipes...")
start = time.time()

df = pd.read_sql_query("SELECT * FROM recipes", conn)
conn.close()

total_recipes = len(df)
print(f"✓ Loaded {total_recipes:,} recipes in {time.time()-start:.1f}s")

# ============================================================================
# PART 2: CREATE RICH EMBEDDING TEXT
# ============================================================================

print("\n" + "="*80)
print("CREATING RICH EMBEDDING TEXT")
print("="*80)

print("\nBuilding enriched text for embeddings...")
start = time.time()

def create_embedding_text(row):
    """Create rich text combining multiple fields"""
    parts = []
    
    # 1. Recipe name
    name = str(row.get('name', '')).strip()
    if name and name != 'nan':
        parts.append(name)
    
    # 2. Cuisine and course
    cuisine = str(row.get('cuisine', '')).strip()
    if cuisine and cuisine not in ['nan', 'International', '']:
        parts.append(cuisine)
    
    course = str(row.get('course', '')).strip()
    if course and course not in ['nan', 'Main Course', '']:
        parts.append(course)
    
    # 3. Diet type
    diet = str(row.get('diet', '')).strip()
    if diet and diet not in ['nan', 'Non-Vegetarian', '']:
        parts.append(diet)
    
    # 4. Cleaned ingredients
    ingredients = str(row.get('cleaned_ingredients', '')).strip()
    if ingredients and ingredients != 'nan':
        parts.append(ingredients)
    
    # 5. Description (if short)
    description = str(row.get('description', '')).strip()
    if description and description != 'nan' and len(description) < 200:
        parts.append(description)
    
    return ' '.join(parts)

df['embedding_text'] = df.apply(create_embedding_text, axis=1)
df = df[df['embedding_text'].str.len() > 10]
df = df.reset_index(drop=True)

total_recipes = len(df)
print(f"✓ Created embedding text for {total_recipes:,} recipes in {time.time()-start:.1f}s")

print("\nExample embedding texts:")
for i in range(2):
    print(f"\n{i+1}. {df['name'].iloc[i]}")
    print(f"   Text: {df['embedding_text'].iloc[i][:120]}...")

gc.collect()

# ============================================================================
# PART 3: COMPUTE EMBEDDINGS & SAVE INCREMENTALLY (MEMORY EFFICIENT)
# ============================================================================

print("\n" + "="*80)
print("COMPUTING EMBEDDINGS ON GPU (MEMORY EFFICIENT MODE)")
print("="*80)

print("\nLoading sentence transformer model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

if torch.cuda.is_available():
    embedding_model = embedding_model.to('cuda')
    print(f"✓ Model loaded on GPU")
else:
    embedding_model = embedding_model.to('cpu')
    print("✓ Model loaded on CPU")

# Backup old embeddings
old_file = 'models/recipe_embeddings.npy'
temp_file = 'models/recipe_embeddings_temp.npy'

if os.path.exists(old_file):
    backup_file = 'models/recipe_embeddings_old_backup.npy'
    print(f"\nBacking up old embeddings to {backup_file}...")
    if os.path.exists(backup_file):
        os.remove(backup_file)
    os.rename(old_file, backup_file)
    print("✓ Old embeddings backed up")

# Settings
BATCH_SIZE = 3000
INTERNAL_BATCH = 256

print(f"\nComputing and saving embeddings incrementally for {total_recipes:,} recipes...")
print("This avoids RAM exhaustion by writing to disk as we go...")

# Create memory-mapped file for writing
embedding_dim = 384  # all-MiniLM-L6-v2 dimension
embeddings_mmap = np.lib.format.open_memmap(
    temp_file,
    mode='w+',
    dtype=np.float32,
    shape=(total_recipes, embedding_dim)
)

start = time.time()
total_batches = (total_recipes + BATCH_SIZE - 1) // BATCH_SIZE

print("\nProcessing batches:")
for i in range(0, total_recipes, BATCH_SIZE):
    end_idx = min(i + BATCH_SIZE, total_recipes)
    batch = df['embedding_text'].iloc[i:end_idx].tolist()
    
    batch_num = i // BATCH_SIZE + 1
    
    print(f"  Batch {batch_num}/{total_batches}: Processing recipes {i:,} to {end_idx:,}...")
    
    try:
        # Encode on GPU
        batch_embeddings = embedding_model.encode(
            batch,
            batch_size=INTERNAL_BATCH,
            show_progress_bar=True,
            convert_to_numpy=True,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            normalize_embeddings=True
        )
        
        # Write directly to memory-mapped file (no RAM accumulation!)
        embeddings_mmap[i:end_idx] = batch_embeddings
        
        # Flush to disk periodically
        if batch_num % 10 == 0:
            embeddings_mmap.flush()
        
        progress = end_idx / total_recipes * 100
        elapsed_so_far = time.time() - start
        eta = (elapsed_so_far / progress * 100) - elapsed_so_far if progress > 0 else 0
        
        print(f"    ✓ Progress: {progress:.1f}% | Elapsed: {elapsed_so_far/60:.1f}min | ETA: {eta/60:.1f}min")
        
        # Free memory
        del batch_embeddings
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        
    except RuntimeError as e:
        if "out of memory" in str(e):
            print(f"    ⚠ GPU OOM! Retrying with smaller batches...")
            torch.cuda.empty_cache()
            
            # Retry with smaller batches
            for j in range(i, end_idx, 500):
                sub_end = min(j + 500, end_idx)
                sub_batch = df['embedding_text'].iloc[j:sub_end].tolist()
                sub_embeddings = embedding_model.encode(
                    sub_batch,
                    batch_size=64,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    device='cuda' if torch.cuda.is_available() else 'cpu',
                    normalize_embeddings=True
                )
                embeddings_mmap[j:sub_end] = sub_embeddings
                del sub_embeddings
                torch.cuda.empty_cache()
        else:
            raise e

# Final flush
print("\nFlushing final embeddings to disk...")
embeddings_mmap.flush()

elapsed = time.time() - start
print(f"\n✓ Embeddings computed and saved in {elapsed/60:.1f} minutes!")

# Rename temp file to final file
del embeddings_mmap
gc.collect()

print("\nFinalizing embeddings file...")
if os.path.exists(old_file):
    os.remove(old_file)
os.rename(temp_file, old_file)

file_size = os.path.getsize(old_file) / 1024**3
print(f"✓ New embeddings saved: {file_size:.2f} GB")

# ============================================================================
# PART 4: TEST NEW EMBEDDINGS
# ============================================================================

print("\n" + "="*80)
print("TESTING NEW EMBEDDINGS")
print("="*80)

# Reload for testing
embeddings = np.load(old_file, mmap_mode='r')
print(f"\n✓ Loaded new embeddings: {embeddings.shape}")

# Verify
norms = np.linalg.norm(embeddings[:1000], axis=1)
print(f"  Embedding norms (sample): min={norms.min():.3f}, max={norms.max():.3f}, mean={norms.mean():.3f}")

# Test queries
test_queries = [
    "South Indian potato curry with curry leaves",
    "Italian tomato pasta"
]

for test_query in test_queries:
    print(f"\n{'='*60}")
    print(f"Test query: '{test_query}'")
    print('='*60)
    
    query_embedding = embedding_model.encode(
        [test_query],
        convert_to_numpy=True,
        device='cuda' if torch.cuda.is_available() else 'cpu',
        normalize_embeddings=True
    )
    
    print("Searching first 50,000 recipes...")
    sample = np.array(embeddings[:50000])
    scores = np.dot(sample, query_embedding.T).flatten()
    
    top_indices = np.argsort(scores)[-5:][::-1]
    top_scores = scores[top_indices]
    
    print("\nTop 5 semantic matches:")
    for rank, (idx, score) in enumerate(zip(top_indices, top_scores), 1):
        recipe_name = df['name'].iloc[idx]
        cuisine = df['cuisine'].iloc[idx]
        print(f"  {rank}. {recipe_name} ({cuisine}) - Score: {score:.3f}")

# ============================================================================
# DONE!
# ============================================================================

print("\n" + "="*80)
print("✅ RETRAINING COMPLETE!")
print("="*80)

print(f"""
Successfully retrained embeddings with richer context!

📊 Summary:
   - Total recipes: {total_recipes:,}
   - Embedding dimension: {embedding_dim}
   - File size: {file_size:.2f} GB
   - Training time: {elapsed/60:.1f} minutes
   - Memory usage: LOW (incremental writes)

🎯 Improvements:
   ✓ Recipe NAME for context
   ✓ CUISINE for regional understanding
   ✓ COURSE & DIET types
   ✓ DESCRIPTION for flavors
   ✓ INGREDIENTS as core

📥 Next step:
   Restart your Flask app: python app.py

Semantic search should now work much better! 🚀
""")
