import pickle
import os
import numpy as np
import glob

def diagnose():
    print("="*60)
    print("DIAGNOSTIC TOOL")
    print("="*60)

    # 1. Load Metadata
    if not os.path.exists('recipe_models.pkl'):
        print("[ERROR] recipe_models.pkl not found!")
        return

    with open('recipe_models.pkl', 'rb') as f:
        data = pickle.load(f)
    
    recipe_ids = data.get('recipe_ids', [])
    print(f"Total Recipe IDs in metadata: {len(recipe_ids)}")
    
    chunks_dir = data.get('chunks_dir', 'model_chunks')
    print(f"Chunks Directory: {chunks_dir}")

    # 2. Check Chunks
    chunk_files = glob.glob(os.path.join(chunks_dir, 'emb_chunk_*.npy'))
    print(f"Found {len(chunk_files)} embedding chunk files.")

    total_embeddings = 0
    chunk_sizes = []
    
    # Sort files to check order 0, 1, 2...
    # We expect filenames like emb_chunk_0.npy, emb_chunk_1.npy
    # Let's check the size of each index i
    
    max_idx = -1
    for f in chunk_files:
        try:
            # Extract number
            base = os.path.basename(f)
            num = int(base.replace('emb_chunk_', '').replace('.npy', ''))
            if num > max_idx:
                max_idx = num
        except:
            pass
            
    print(f"Max chunk index found: {max_idx}")
    
    for i in range(max_idx + 1):
        path = os.path.join(chunks_dir, f'emb_chunk_{i}.npy')
        if not os.path.exists(path):
            print(f"[WARNING] Missing chunk {i} at {path}")
            chunk_sizes.append(0)
            continue
            
        try:
            arr = np.load(path)
            size = len(arr)
            chunk_sizes.append(size)
            total_embeddings += size
            if i < 5: # Print first few
                print(f"  Chunk {i}: {size} items")
        except Exception as e:
            print(f"[ERROR] Failed to load chunk {i}: {e}")

    print(f"Total Embeddings found: {total_embeddings}")
    
    # 3. Compare
    diff = len(recipe_ids) - total_embeddings
    if diff == 0:
        print("✅ SUCCESS: Recipe IDs match total embeddings count.")
    else:
        print(f"❌ FAILURE: Mismatch! {len(recipe_ids)} IDs vs {total_embeddings} embeddings. Diff: {diff}")

    # 4. Check Consistency of Chunk Sizes
    # Usually all chunks except last should be same size
    if chunk_sizes:
        common_size = max(set(chunk_sizes), key=chunk_sizes.count)
        print(f"Most common chunk size: {common_size}")
        
        irregular_chunks = []
        for i, size in enumerate(chunk_sizes):
            if size != common_size and i != max_idx:
                irregular_chunks.append((i, size))
        
        if irregular_chunks:
            print(f"❌ WARNING: Found irregular chunks (not last one): {irregular_chunks}")
        else:
            print("✅ Chunk sizes look consistent (only last one differs).")

if __name__ == "__main__":
    diagnose()
