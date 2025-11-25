import os
import pickle
import numpy as np
import sqlite3
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def test_search_logic():
    with open('test_output.txt', 'w', encoding='utf-8') as log:
        log.write("Loading models...\n")
        try:
            with open('recipe_models.pkl', 'rb') as f:
                models_data = pickle.load(f)
            
            recipe_ids = models_data['recipe_ids']
            chunks_dir = models_data['chunks_dir']
            chunk_size = models_data.get('chunk_size', 10000)
            num_chunks = models_data.get('num_chunks', 0)
            
            if not num_chunks:
                import glob
                num_chunks = len(glob.glob(os.path.join(chunks_dir, 'emb_chunk_*.npy')))
            
            encoder = SentenceTransformer('all-MiniLM-L6-v2')
            log.write(f"Loaded {len(recipe_ids)} recipes. Chunks: {num_chunks}\n")
            
            def search(query, top_k=3):
                log.write(f"\nSearching for: '{query}'\n")
                query_emb = encoder.encode([query])
                
                global_top_scores = []
                global_top_indices = []
                
                for i in range(num_chunks):
                    chunk_path = os.path.join(chunks_dir, f'emb_chunk_{i}.npy')
                    if not os.path.exists(chunk_path):
                        continue
                    
                    chunk_emb = np.load(chunk_path)
                    sims = cosine_similarity(query_emb, chunk_emb)[0]
                    
                    k_chunk = min(top_k, len(sims))
                    chunk_top_indices = np.argsort(sims)[-k_chunk:][::-1]
                    chunk_top_scores = sims[chunk_top_indices]
                    
                    global_indices = (i * chunk_size) + chunk_top_indices
                    
                    global_top_scores.extend(chunk_top_scores)
                    global_top_indices.extend(global_indices)
                
                global_top_scores = np.array(global_top_scores)
                global_top_indices = np.array(global_top_indices)
                
                if len(global_top_scores) > 0:
                    final_top_args = np.argsort(global_top_scores)[-top_k:][::-1]
                    final_indices = global_top_indices[final_top_args]
                    
                    conn = sqlite3.connect('recipes.db')
                    cursor = conn.cursor()
                    
                    for idx in final_indices:
                        if idx < len(recipe_ids):
                            r_id = recipe_ids[idx]
                            cursor.execute('SELECT name, description, cuisine FROM recipes WHERE id = ?', (r_id,))
                            row = cursor.fetchone()
                            if row:
                                log.write(f"  - {row[0]} ({row[2]})\n")
                    conn.close()

            search("pasta")
            search("spicy chicken")
            search("paneer")
            
        except Exception as e:
            log.write(f"Error: {e}\n")
            import traceback
            log.write(traceback.format_exc())

if __name__ == "__main__":
    test_search_logic()
