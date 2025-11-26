# app.py - Pure AI Recipe Generator
import subprocess
import time
import os
import re
import json
import pickle
import numpy as np
import sqlite3
from flask import Flask, render_template, request, jsonify, session
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Start Ollama model automatically
def start_ollama_model():
    try:
        print("\n[INFO] Starting Ollama model 'mistral'...")
        proc = subprocess.Popen(
            ["ollama", "run", "mistral"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # give some time for the model to load
        return proc
    except Exception as e:
        print(f"[ERROR] Failed to start Ollama automatically: {e}")
        return None

ollama_process = start_ollama_model()

app = Flask(__name__)
app.secret_key = os.urandom(24)

print("=" * 60)
print("AI Recipe Generator")
print("=" * 60)

# --- Load Models & Embeddings ---
print("\n[INFO] Loading models and metadata...")
try:
    # Load metadata
    with open('recipe_models.pkl', 'rb') as f:
        models_data = pickle.load(f)
    
    recipe_ids = models_data['recipe_ids']
    chunks_dir = models_data['chunks_dir']
    chunk_size = models_data.get('chunk_size', 10000) # Default from build_models.py
    num_chunks = models_data.get('num_chunks', 0)
    
    # If num_chunks is missing, try to count them
    if not num_chunks:
        import glob
        num_chunks = len(glob.glob(os.path.join(chunks_dir, 'emb_chunk_*.npy')))

    # Detect chunk_size from the first chunk
    if num_chunks > 0:
        first_chunk_path = os.path.join(chunks_dir, 'emb_chunk_0.npy')
        if os.path.exists(first_chunk_path):
            try:
                first_chunk = np.load(first_chunk_path)
                chunk_size = len(first_chunk)
                print(f"[INFO] Detected chunk_size: {chunk_size}")
            except Exception as e:
                print(f"[WARNING] Could not load first chunk to detect size: {e}")
                chunk_size = models_data.get('chunk_size', 10000)
        else:
             chunk_size = models_data.get('chunk_size', 10000)
    else:
        chunk_size = models_data.get('chunk_size', 10000)

    # Load Sentence Transformer
    print("[INFO] Loading Sentence Transformer...")
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # TF-IDF vectorizer (matrix is in chunks)
    print("[INFO] Loading TF-IDF vectorizer...")
    tfidf_vectorizer = models_data.get('tfidf_vectorizer')
    
    if tfidf_vectorizer:
        print(f"[INFO] TF-IDF vectorizer loaded")
    else:
        print("[WARNING] TF-IDF vectorizer not available.")
    
    print(f"[INFO] Ready to search {len(recipe_ids)} recipes across {num_chunks} chunks.")
    models_loaded = True
except Exception as e:
    print(f"[ERROR] Failed to load models: {e}")
    print("Ensure you have run 'build_models.py' first.")
    models_loaded = False
    recipe_ids = []
    encoder = None
    chunks_dir = None
    tfidf_vectorizer = None

# Local LLM (optional) - using Ollama for stable inference
llm = None
ollama_available = False
try:
    import requests
    # Check if Ollama is running on default port
    resp = requests.get('http://localhost:11434/api/tags', timeout=2)
    if resp.status_code == 200:
        ollama_available = True
        print("\n[INFO] Ollama detected. Using Ollama for local LLM inference.")
        print("   Ensure 'ollama run mistral' is running in another terminal.")
except Exception:
    pass

if not ollama_available:
    print("\n[WARNING] Ollama not running. Local LLM disabled.")
    print("   To enable:")
    print("   1. Download Ollama from https://ollama.ai")
    print("   2. Run: ollama run mistral")
    print("   3. Keep that terminal open and start this Flask app")
    llm = None
else:
    llm = "ollama"  # Marker that Ollama is available

def _parse_mistral_recipe_list(llm_output):
    """Parse Mistral-generated recipe list from JSON block."""
    try:
        # Find the JSON block
        json_start = llm_output.find('```json')
        if json_start == -1:
            json_start = llm_output.find('[')
        else:
            json_start += 7 # Move past ```json

        json_end = llm_output.rfind('```')
        if json_end == -1:
            json_end = llm_output.rfind(']') + 1
        
        if json_start == -1 or json_end == -1:
            print("[_parse_mistral_recipe_list] No JSON block found")
            return None

        json_str = llm_output[json_start:json_end].strip()
        
        recipes = json.loads(json_str)
        
        if not isinstance(recipes, list):
            return None
            
        for recipe in recipes:
            if 'name' not in recipe or 'ingredients' not in recipe or 'instructions' not in recipe:
                return None
        
        return recipes

    except Exception as e:
        print(f"[_parse_mistral_recipe_list] Error parsing JSON: {e}")
        print(f"LLM output was:\n{llm_output}")
        return None

def search_db(query, top_k=5):
    """Search database using chunked embeddings."""
    print(f"[search_db] Called with query: {query}")
    print(f"[search_db] models_loaded: {models_loaded}")
    
    if not models_loaded:
        print("[search_db] Models not loaded, returning empty.")
        return []
    
    try:
        # Encode query
        query_emb = encoder.encode([query]) # Shape: (1, 384)
        
        global_top_scores = []
        global_top_indices = []
        
        # Iterate through chunks
        print(f"[search_db] Starting search across {num_chunks} chunks...")
        for i in range(num_chunks):
            if i % 5 == 0:
                print(f"[search_db] Processing chunk {i+1}/{num_chunks}...")
            
            chunk_path = os.path.join(chunks_dir, f'emb_chunk_{i}.npy')
            if not os.path.exists(chunk_path):
                continue
                
            # Load chunk
            chunk_emb = np.load(chunk_path) # Shape: (N_chunk, 384)
            
            # Compute similarity
            sims = cosine_similarity(query_emb, chunk_emb)[0] # Shape: (N_chunk,)
            
            # Get top k in this chunk
            # We take top_k from EACH chunk to be safe, then merge later
            k_chunk = min(top_k, len(sims))
            chunk_top_indices = np.argsort(sims)[-k_chunk:][::-1]
            chunk_top_scores = sims[chunk_top_indices]
            
            # Map back to global indices
            # Global index = (chunk_index * chunk_size) + local_index
            # BUT we need to be careful if chunks are not perfectly equal or if recipe_ids list aligns perfectly.
            # Assuming recipe_ids list aligns with the concatenation of all chunks.
            global_indices = (i * chunk_size) + chunk_top_indices
            
            global_top_scores.extend(chunk_top_scores)
            global_top_indices.extend(global_indices)
            
            # Clean up
            del chunk_emb, sims
        
        # Now find the global top k from the candidates
        global_top_scores = np.array(global_top_scores)
        global_top_indices = np.array(global_top_indices)
        
        if len(global_top_scores) == 0:
            return []
            
        final_top_args = np.argsort(global_top_scores)[-top_k:][::-1]
        final_indices = global_top_indices[final_top_args]
        
        results = []
        conn = sqlite3.connect('recipes.db')
        cursor = conn.cursor()
        
        for idx in final_indices:
            if idx < len(recipe_ids):
                r_id = recipe_ids[idx]
                cursor.execute('SELECT name, description, cuisine, ingredients, instructions FROM recipes WHERE id = ?', (r_id,))
                row = cursor.fetchone()
                if row:
                    results.append({
                        'name': row[0],
                        'description': row[1],
                        'cuisine': row[2],
                        'ingredients': row[3],
                        'instructions': row[4]
                    })
        
        conn.close()
        return results
    except Exception as e:
        print(f"[search_db] Error: {e}")
        return []

def hybrid_search_db(query, top_k=10):
    """Hybrid search using both TF-IDF and embeddings."""
    if not models_loaded:
        print("[hybrid_search_db] Models not loaded, returning empty.")
        return []
    
    print(f"[hybrid_search_db] Called with query: {query}")
    
    # 1. TF-IDF Search (from chunks)
    tfidf_results = []
    if tfidf_vectorizer:
        try:
            from scipy import sparse
            query_vec = tfidf_vectorizer.transform([query])
            
            # Load and search TF-IDF chunks
            global_tfidf_scores = []
            global_tfidf_indices = []
            
            for i in range(num_chunks):
                tfidf_chunk_path = os.path.join(chunks_dir, f'tfidf_chunk_{i}.npz')
                if not os.path.exists(tfidf_chunk_path):
                    continue
                
                chunk_matrix = sparse.load_npz(tfidf_chunk_path)
                scores = cosine_similarity(query_vec, chunk_matrix)[0]
                
                # Get top candidates from this chunk
                k_chunk = min(top_k, len(scores))
                chunk_top_indices = np.argsort(scores)[-k_chunk:][::-1]
                chunk_top_scores = scores[chunk_top_indices]
                
                # Map to global indices
                global_indices = (i * chunk_size) + chunk_top_indices
                
                global_tfidf_scores.extend(chunk_top_scores)
                global_tfidf_indices.extend(global_indices)
                
                del chunk_matrix, scores
            
            # Get top 10 overall from TF-IDF (keep as list to preserve order)
            if len(global_tfidf_scores) > 0:
                global_tfidf_scores = np.array(global_tfidf_scores)
                global_tfidf_indices = np.array(global_tfidf_indices)
                
                final_top_args = np.argsort(global_tfidf_scores)[-10:][::-1]
                final_indices = global_tfidf_indices[final_top_args]
                tfidf_results = final_indices.tolist()  # Keep as list to preserve order
                print(f"[hybrid_search_db] TF-IDF found {len(tfidf_results)} candidates")
        except Exception as e:
            print(f"[hybrid_search_db] TF-IDF error: {e}")
    
    # 2. Embedding Search
    embedding_results = []
    try:
        query_emb = encoder.encode([query])
        
        global_top_scores = []
        global_top_indices = []
        
        for i in range(num_chunks):
            if i % 10 == 0:
                print(f"[hybrid_search_db] Processing chunk {i+1}/{num_chunks}...")
            
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
            
            del chunk_emb, sims
        
        global_top_scores = np.array(global_top_scores)
        global_top_indices = np.array(global_top_indices)
        
        if len(global_top_scores) > 0:
            final_top_args = np.argsort(global_top_scores)[-10:][::-1]
            final_indices = global_top_indices[final_top_args]
            embedding_results = final_indices.tolist()  # Keep as list to preserve order
            print(f"[hybrid_search_db] Embeddings found {len(embedding_results)} candidates")
    except Exception as e:
        print(f"[hybrid_search_db] Embedding error: {e}")
    
    # 3. Combine top 10 from each (already sorted by score)
    final_indices = tfidf_results + embedding_results
    print(f"[hybrid_search_db] Taking {len(tfidf_results)} from TF-IDF + {len(embedding_results)} from embeddings = {len(final_indices)} total")
    
    if len(final_indices) == 0:
        return []
    
    # 4. Retrieve from DB (with deduplication)
    results = []
    seen_ids = set()
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    
    for idx in final_indices:
        if idx < len(recipe_ids):
            r_id = recipe_ids[idx]
            if r_id in seen_ids:
                continue
            seen_ids.add(r_id)
            
            cursor.execute('SELECT name, description, cuisine, ingredients, instructions FROM recipes WHERE id = ?', (r_id,))
            row = cursor.fetchone()
            if row:
                results.append({
                    'name': row[0],
                    'description': row[1],
                    'cuisine': row[2],
                    'ingredients': row[3],
                    'instructions': row[4]
                })
    
    conn.close()
    print(f"[hybrid_search_db] Returning {len(results)} unique recipes")
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cooking_assistant.html')
def cooking_assistant():
    return render_template('cooking_assistant.html')

@app.route('/cook-with-ai', methods=['POST'])
def cook_with_ai():
    """Get a specific recipe from the session."""
    try:
        data = request.json
        recipe_id = data.get('recipe_id')
        
        recipes = session.get('recipes', [])
        
        recipe_data = None
        for r in recipes:
            if r.get('id') == recipe_id:
                recipe_data = {
                    'recipe': r,
                    'parsed_steps': r.get('parsed_steps', [])
                }
                break
        
        if recipe_data:
            return jsonify({'success': True, **recipe_data})
        else:
            return jsonify({'success': False, 'error': 'Recipe not found in session.'}), 404

    except Exception as e:
        print(f"Error in /cook-with-ai: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """Generate recipes using Embeddings + Mistral AI."""
    try:
        data = request.json
        query = data.get('query', '').strip()
        dietary_preference = data.get('dietary_preference', 'all')

        if not query:
            return jsonify({'success': False, 'error': 'No query provided'})

        if llm != "ollama":
            return jsonify({'success': False, 'error': 'Ollama not running. Start it with: ollama run mistral'}), 503

        print(f"[search] Searching for: {query}")
        print(f"[search] Dietary preference: {dietary_preference}")

        # 1. Hybrid Search (TF-IDF + Embeddings)
        # This will return up to 20 recipes (10 from TF-IDF + 10 from embeddings)
        found_dishes = hybrid_search_db(query, top_k=10)
        
        if not found_dishes:
            print("[search] No matches found in DB.")
            return jsonify({'success': False, 'error': 'No matching recipes found in database.'})
        
        print(f"[search] Found {len(found_dishes)} matches in DB for enhancement.")
        context_str = "I found these similar recipes in our database:\n\n"
        for i, dish in enumerate(found_dishes):
            context_str += f"Recipe {i+1}: {dish['name']} ({dish['cuisine']})\n"
            context_str += f"Description: {dish['description']}\n"
            context_str += f"Ingredients: {dish['ingredients']}\n"
            context_str += f"Instructions: {dish['instructions']}\n"
            context_str += "-" * 20 + "\n"

        # Build dietary constraint for prompt
        dietary_constraint = ""
        if dietary_preference == 'vegetarian':
            dietary_constraint = "IMPORTANT: Generate ONLY VEGETARIAN recipes. Do not include any meat, poultry, fish, or seafood."
        elif dietary_preference == 'non-vegetarian':
            dietary_constraint = "IMPORTANT: Generate ONLY NON-VEGETARIAN recipes that include meat, poultry, fish, or seafood."
        
        # 2. Generate DB-Enhanced Recipes
        prompt = f"""You are a creative chef. A user wants recipes using ONLY these ingredients: "{query}" (plus basic pantry staples like salt, pepper, oil, water, sugar).

{dietary_constraint}

{context_str}

Task:
1. Use the retrieved recipes above as INSPIRATION for techniques and flavor profiles.
2. ADAPT them to use ONLY the user's specific ingredients listed in the query.
3. Do NOT add significant new ingredients that are not in the user's query.
4. Generate 10 diverse recipes based on the database recipes above.

Your response MUST be a valid JSON array of recipe objects. Each object should have the following structure:
{{
  "name": "Recipe Name",
  "description": "A short, enticing description of the dish.",
  "ingredients": ["Ingredient 1", "Ingredient 2", "...", "Ingredient N"],
  "instructions": ["Step 1", "Step 2", "...", "Step N"]
}}

Do not include any text outside of the JSON array. The response should start with `[` and end with `]`.
"""

        import requests
        resp = requests.post('http://localhost:11434/api/generate', json={
            'model': 'mistral',
            'prompt': prompt,
            'stream': False,
            'temperature': 0.7,
        }, timeout=180)

        if resp.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to generate recipes from AI.'})

        result = resp.json()
        llm_output = result.get('response', '').strip()

        recipes = _parse_mistral_recipe_list(llm_output)
        
        if not recipes:
            return jsonify({'success': False, 'error': 'Failed to parse AI-generated recipes.'})

        def normalize_instructions(instructions):
            """Ensure instructions are a flat list of single steps."""
            if isinstance(instructions, str):
                instructions = [instructions]
            
            normalized = []
            for item in instructions:
                if not item or not isinstance(item, str):
                    continue
                
                # 1. Split by newlines first
                lines = item.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 2. Split by numbered patterns (e.g. "1. Step", "2) Step")
                    # Split before number at start of line or in middle
                    # (?<!\d) ensures we don't split 1.5
                    # (?=\d+[\.\)]\s+) lookahead for "1. " or "1) "
                    parts = re.split(r'(?<!\d)(?=\d+[\.\)]\s+)', line)
                    
                    for part in parts:
                        part = part.strip()
                        if not part:
                            continue
                            
                        # 3. Split by sentence boundaries
                        # Look for punctuation [.!?] followed by whitespace and a Capital letter
                        # This handles "Cook pasta. Drain it." -> "Cook pasta.", "Drain it."
                        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', part)
                        
                        for sentence in sentences:
                            sentence = sentence.strip()
                            
                            # Remove leading numbers/bullets (e.g. "1.", "1)", "-")
                            sentence = re.sub(r'^[\d\-\*\•]+[\.\)\:]?\s*', '', sentence)
                            
                            if len(sentence) > 3:
                                # Ensure it ends with punctuation
                                if not sentence[-1] in '.!?':
                                    sentence += '.'
                                normalized.append(sentence)
            
            return normalized if normalized else ["Follow the recipe instructions."]

        for i, recipe in enumerate(recipes):
            recipe['id'] = f"ai-{i}"
            
            # Normalize instructions
            raw_instructions = recipe.get('instructions', [])
            recipe['instructions'] = normalize_instructions(raw_instructions)
            
            parsed_steps = []
            for j, instruction in enumerate(recipe['instructions']):
                timers = re.findall(r'(\d+)\s*min', instruction)
                parsed_steps.append({
                    'step_number': j + 1,
                    'text': instruction,
                    'timers': [int(t) for t in timers],
                    'has_timer': bool(timers)
                })
            recipe['parsed_steps'] = parsed_steps
        
        session['recipes'] = recipes

        return jsonify({'success': True, 'recipes': recipes})

    except Exception as e:
        print(f"[search] ERROR: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    print("\nStarting server on http://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)

