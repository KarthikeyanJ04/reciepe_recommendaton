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

    # Load Sentence Transformer
    print("[INFO] Loading Sentence Transformer...")
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"[INFO] Ready to search {len(recipe_ids)} recipes across {num_chunks} chunks.")
    models_loaded = True
except Exception as e:
    print(f"[ERROR] Failed to load models: {e}")
    print("Ensure you have run 'build_models.py' first.")
    models_loaded = False
    recipe_ids = []
    encoder = None
    chunks_dir = None

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
    if not models_loaded:
        return []
    
    try:
        # Encode query
        query_emb = encoder.encode([query]) # Shape: (1, 384)
        
        global_top_scores = []
        global_top_indices = []
        
        # Iterate through chunks
        for i in range(num_chunks):
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
                cursor.execute('SELECT name, description, cuisine FROM recipes WHERE id = ?', (r_id,))
                row = cursor.fetchone()
                if row:
                    results.append({
                        'name': row[0],
                        'description': row[1],
                        'cuisine': row[2]
                    })
        
        conn.close()
        return results
    except Exception as e:
        print(f"[search_db] Error: {e}")
        return []

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

        if not query:
            return jsonify({'success': False, 'error': 'No query provided'})

        if llm != "ollama":
            return jsonify({'success': False, 'error': 'Ollama not running. Start it with: ollama run mistral'}), 503

        print(f"[search] Searching for: {query}")

        # 1. Search DB using embeddings
        found_dishes = search_db(query, top_k=5)
        
        if not found_dishes:
            print("[search] No matches found in DB, falling back to pure generation.")
            context_str = "No specific existing recipes found. Create something new!"
        else:
            print(f"[search] Found {len(found_dishes)} matches in DB.")
            context_str = "I found these similar dishes in our database:\n"
            for i, dish in enumerate(found_dishes):
                context_str += f"{i+1}. {dish['name']} ({dish['cuisine']}): {dish['description']}\n"

        # 2. Generate Recipes using Mistral
        prompt = f"""You are a creative chef. A user is looking for recipes based on the following query: "{query}".

{context_str}

Based on the user's query and the similar dishes found (if any), generate 5 diverse and interesting recipes.
If the user's query matches one of the found dishes, definitely include a version of that dish.
Feel free to add creative twists or other related recipes.

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
        }, timeout=120)

        if resp.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to generate recipes from AI.'})

        result = resp.json()
        llm_output = result.get('response', '').strip()

        recipes = _parse_mistral_recipe_list(llm_output)

        if not recipes:
            return jsonify({'success': False, 'error': 'Failed to parse AI-generated recipes.'})

        for i, recipe in enumerate(recipes):
            recipe['id'] = f"ai-{i}"
            parsed_steps = []
            for j, instruction in enumerate(recipe.get('instructions', [])):
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

