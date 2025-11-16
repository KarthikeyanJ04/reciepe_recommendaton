# app.py - Auto-calculate missing values

import os
import sqlite3
import numpy as np
import pickle
from flask import Flask, render_template, request, jsonify
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
from sentence_transformers import SentenceTransformer
from nlg_generator import nlg
import re
import json

app = Flask(__name__)

DB_FILE = 'recipes.db'
MODELS_FILE = 'recipe_models.pkl'

print("=" * 60)
print("AI Recipe Finder (Chunk-based)")
print("=" * 60)

# Load metadata
print("\nLoading models...")
with open(MODELS_FILE, 'rb') as f:
    models = pickle.load(f)

tfidf_vectorizer = models['tfidf_vectorizer']
recipe_ids = models['recipe_ids']

# In app.py, replace the auto-detection part:

if 'num_chunks' in models:
    num_chunks = models['num_chunks']
    chunk_size = models['chunk_size']
    chunks_dir = models['chunks_dir']
else:
    # Auto-detect from actual files
    chunks_dir = models.get('chunks_dir', 'model_chunks')
    
    # Get all chunk files and find max index
    chunk_files = [f for f in os.listdir(chunks_dir) if f.startswith('tfidf_chunk_') and f.endswith('.npz')]
    
    # Extract chunk indices from filenames
    chunk_indices = [int(f.split('_')[-1].split('.')[0]) for f in chunk_files]
    num_chunks = max(chunk_indices) + 1  # +1 because indices start at 0
    
    # Calculate chunk size from first chunk
    first_chunk = sparse.load_npz(f'{chunks_dir}/tfidf_chunk_0.npz')
    chunk_size = first_chunk.shape[0]
    
    print(f"Auto-detected {num_chunks} chunks (indices 0-{max(chunk_indices)})")


print(f"\nLoaded metadata for {len(recipe_ids):,} recipes")
print(f"   Chunks: {num_chunks} x ~{chunk_size:,} recipes")

# Initialize embedding model
print("\nLoading embedding model (this may take 30-60 seconds on first run)...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Embedding model loaded!")


def _normalize_instruction(step):
    """Normalize a single instruction string."""
    if not isinstance(step, str):
        return step

    s = step.strip()

    # If looks like a JSON array, try to parse and join tokens
    if s.startswith('[') and s.endswith(']'):
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                text = ' '.join([str(t).strip() for t in parsed if t])
                text = re.sub(r"\s+([.,;:!?])", r"\1", text)
                s = text
        except Exception:
            pass

    # Decode escaped unicode sequences
    try:
        if '\\u' in s or '\\n' in s:
            s = s.encode('utf-8').decode('unicode_escape')
    except Exception:
        pass

    # Common mojibake fixes
    s = s.replace('â', '')
    s = s.replace('\u00b0', '')
    s = s.replace('Â', '')
    s = re.sub(r'[\x00-\x1f\x7f]', '', s)

    return s.strip()

def get_recipe_by_id(recipe_id):
    """Get recipe from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, image_url, description, cuisine, course, diet, 
               prep_time, ingredients, instructions, category
        FROM recipes WHERE id = ?
    ''', (recipe_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'id': row[0],
        'name': row[1],
        'image_url': row[2],
        'description': row[3],
        'cuisine': row[4],
        'course': row[5],
        'diet': row[6],
        'prep_time': row[7],
        'ingredients': [i.strip() for i in row[8].split('|') if i.strip()],
        'instructions': [_normalize_instruction(i.strip()) for i in row[9].split('|') if i.strip()],
        'category': row[10]
    }

def search_recipes(query, category='all', top_k=10):
    """Search using chunked models"""
    
    # Filter by category
    if category != 'all':
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM recipes WHERE category = ?', (category,))
        category_ids = set([r[0] for r in cursor.fetchall()])
        conn.close()
        filtered_indices = [i for i, rid in enumerate(recipe_ids) if rid in category_ids]
    else:
        filtered_indices = list(range(len(recipe_ids)))
    
    if not filtered_indices:
        return []
    
    q = query.lower()
    
    # Transform query
    q_tfidf = tfidf_vectorizer.transform([q])
    q_emb = embedding_model.encode([q])
    
    # Calculate scores by loading chunks
    all_scores = np.zeros(len(recipe_ids))
    
    for chunk_idx in range(num_chunks):
        # Load chunks
        try:
            tfidf_chunk = sparse.load_npz(f'{chunks_dir}/tfidf_chunk_{chunk_idx}.npz')
        except FileNotFoundError:
            print(f"Warning: tfidf_chunk_{chunk_idx}.npz not found")
            continue
            
        try:
            emb_chunk = np.load(f'{chunks_dir}/emb_chunk_{chunk_idx}.npy')
        except FileNotFoundError:
            print(f"Warning: emb_chunk_{chunk_idx}.npy not found")
            continue
    
        # Calculate actual chunk size (last chunk may be smaller)
        actual_chunk_size = tfidf_chunk.shape[0]  # Get actual size from the chunk
        start_idx = chunk_idx * chunk_size
        end_idx = start_idx + actual_chunk_size  # Use actual size, not chunk_size
    
        tfidf_scores = cosine_similarity(q_tfidf, tfidf_chunk).flatten()
        emb_scores = cosine_similarity(q_emb, emb_chunk).flatten()
    
        # Hybrid
        chunk_scores = 0.6 * tfidf_scores + 0.4 * emb_scores
        all_scores[start_idx:end_idx] = chunk_scores  # Now sizes match
    
        del tfidf_chunk, emb_chunk, tfidf_scores, emb_scores, chunk_scores
    
    # Get top results
    filtered_scores = all_scores[filtered_indices]
    top_idx = np.argsort(filtered_scores)[::-1][:top_k]
    
    results = []
    for idx in top_idx:
        orig_idx = filtered_indices[idx]
        recipe = get_recipe_by_id(recipe_ids[orig_idx])
        
        if recipe:
            recipe['similarity'] = float(filtered_scores[idx])
            if not recipe['description']:
                recipe['description'] = nlg.generate_full_description(recipe)
            recipe['tips'] = nlg.generate_tips(recipe)
            results.append(recipe)
    
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cooking-assistant')
def cooking_assistant():
    return render_template('cooking_assistant.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        query = data.get('query', '').strip()
        category = data.get('category', 'all')
        
        if not query:
            return jsonify({'success': False, 'error': 'No query'})
        
        recipes = search_recipes(query, category)
        return jsonify({'success': True, 'recipes': recipes})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cook-with-ai', methods=['POST'])
def cook_with_ai():
    """Parse recipe and extract timers"""
    try:
        print("\n[cook-with-ai] Received request")
        data = request.json
        print(f"[cook-with-ai] Data: {data}")
        recipe_id = data.get('recipe_id')
        print(f"[cook-with-ai] Recipe ID: {recipe_id}")
        
        recipe = get_recipe_by_id(recipe_id)
        print(f"[cook-with-ai] Recipe fetched: {recipe is not None}")
        if not recipe:
            return jsonify({'success': False, 'error': 'Recipe not found'})
        
        # Parse instructions for timers
        parsed_steps = []
        instructions = recipe.get('instructions', [])
        print(f"[cook-with-ai] Instructions count: {len(instructions)}")
        
        for i, instruction in enumerate(instructions):
            if not isinstance(instruction, str):
                instruction = str(instruction)
            
            # Extract time patterns
            timers = []
            
            # Check for minutes
            minute_matches = re.findall(r'(\d+)\s*(?:minutes?|mins?)', instruction, re.IGNORECASE)
            for match in minute_matches:
                timers.append(int(match))
            
            # Check for hours
            hour_matches = re.findall(r'(\d+)\s*(?:hours?|hrs?)', instruction, re.IGNORECASE)
            for match in hour_matches:
                timers.append(int(match) * 60)  # Convert to minutes
            
            # Check for seconds
            second_matches = re.findall(r'(\d+)\s*(?:seconds?|secs?)', instruction, re.IGNORECASE)
            for match in second_matches:
                timers.append(int(match) / 60.0)  # Convert to minutes
            
            parsed_steps.append({
                'step_number': i + 1,
                'text': instruction,
                'timers': timers,
                'has_timer': len(timers) > 0
            })
        
        print(f"[cook-with-ai] Parsed {len(parsed_steps)} steps")
        return jsonify({
            'success': True,
            'recipe': recipe,
            'parsed_steps': parsed_steps
        })
        
    except Exception as e:
        print(f"[cook-with-ai] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    print("\nStarting server on http://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)



