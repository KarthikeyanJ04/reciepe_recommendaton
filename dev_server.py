"""Lightweight dev server that avoids heavy ML imports.

Use this for local testing of DB reads, normalization, and the UI without loading
SentenceTransformer/scikit-learn/torch. It provides a `/search` endpoint that
performs a simple SQL LIKE match and returns normalized recipes.
"""
from flask import Flask, request, jsonify, render_template
import sqlite3
import re
import json
import os

app = Flask(__name__)
DB_FILE = 'recipes.db'


def _normalize_instruction(step):
    if not isinstance(step, str):
        return step
    s = step.strip()

    # If looks like JSON array
    if s.startswith('[') and s.endswith(']'):
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                text = ' '.join([str(t).strip() for t in parsed if t])
                text = re.sub(r"\s+([.,;:!?])", r"\1", text)
                s = text
        except Exception:
            pass

    try:
        if '\\u' in s or '\\n' in s:
            s = s.encode('utf-8').decode('unicode_escape')
    except Exception:
        pass

    s = s.replace('â', '')
    s = s.replace('\u00b0', '')
    s = s.replace('Â', '')
    s = re.sub(r'[\x00-\x1f\x7f]', '', s)
    s = s.replace('|', '\n')
    s = s.strip()
    return s


def get_recipe_by_id(recipe_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT id, name, image_url, description, cuisine, course, diet, prep_time, ingredients, instructions, category FROM recipes WHERE id = ?', (recipe_id,))
    row = cur.fetchone()
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


@app.route('/')
def index():
    # If templates/index.html exists in this folder, use it; otherwise return simple message
    if os.path.exists('templates/index.html'):
        return render_template('index.html')
    return "Dev server running. Use POST /search to query."


@app.route('/search', methods=['POST'])
def search():
    data = request.json or {}
    query = (data.get('query') or '').strip()
    category = data.get('category', 'all')
    if not query:
        return jsonify({'success': False, 'error': 'No query provided'})

    # Simple SQL LIKE search across name and ingredients
    q = f"%{query}%"
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if category and category != 'all':
        cur.execute("SELECT id FROM recipes WHERE (name LIKE ? OR ingredients LIKE ?) AND category = ? LIMIT 20", (q, q, category))
    else:
        cur.execute("SELECT id FROM recipes WHERE name LIKE ? OR ingredients LIKE ? LIMIT 20", (q, q))
    rows = cur.fetchall()
    conn.close()

    recipes = []
    for r in rows:
        recipe = get_recipe_by_id(r[0])
        if recipe:
            recipes.append(recipe)

    return jsonify({'success': True, 'recipes': recipes})


if __name__ == '__main__':
    print('Starting lightweight dev server on http://127.0.0.1:5001')
    app.run(host='127.0.0.1', port=5001, debug=True)
