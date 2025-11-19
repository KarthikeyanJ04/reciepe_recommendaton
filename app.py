# app.py - Pure AI Recipe Generator
import subprocess
import time

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

import os
from flask import Flask, render_template, request, jsonify
import re
import json
import os

app = Flask(__name__)

print("=" * 60)
print("AI Recipe Generator")
print("=" * 60)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cooking-assistant')
def cooking_assistant():
    return render_template('cooking_assistant.html')

@app.route('/cooking-assistant-recipe', methods=['POST'])
def cooking_assistant_recipe():
    """Render cooking assistant with full recipe data from POST."""
    try:
        data = request.json
        recipe = data.get('recipe')
        parsed_steps = data.get('parsed_steps', [])

        if not recipe:
            return jsonify({'success': False, 'error': 'No recipe data provided'}), 400

        html_content = render_template('cooking_assistant.html', recipe=recipe, parsed_steps=parsed_steps)
        
        return jsonify({'success': True, 'html': html_content})

    except Exception as e:
        print(f"Error in /cooking-assistant-recipe: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """Generate recipes from scratch using Mistral AI."""
    try:
        data = request.json
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'success': False, 'error': 'No query provided'})

        if llm != "ollama":
            return jsonify({'success': False, 'error': 'Ollama not running. Start it with: ollama run mistral'}), 503

        print(f"[search] Generating recipes for query: {query}")

        prompt = f"""You are a creative chef. A user is looking for recipes based on the following query: "{query}".

Generate 30 diverse and interesting recipes inspired by this query. Prioritise Indian Cuisine more.

Your response MUST be a valid JSON array of recipe objects. Each object should have the following structure:
{{
  "name": "Recipe Name",
  "description": "A short, enticing description of the dish.",
  "ingredients": ["Ingredient 1", "Ingredient 2", "...", "Ingredient N"],
  "instructions": ["Step 1", "Step 2", "...", "Step N"]
}}

Do not include any text outside of the JSON array. The response should start with `[` and end with `]`.

Here is the user's query: "{query}"
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

        return jsonify({'success': True, 'recipes': recipes})

    except Exception as e:
        print(f"[search] ERROR: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    print("\nStarting server on http://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
