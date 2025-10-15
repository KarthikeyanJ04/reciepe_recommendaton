from flask import Flask, request, jsonify, render_template
from recommender import HybridRecipeRecommender
import traceback

app = Flask(__name__)

print("Loading hybrid recommender...")
recommender = HybridRecipeRecommender()
print("Hybrid recommender loaded successfully!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        ingredients = data.get('ingredients', '').strip()
        top_n = int(data.get('top_n', 50))
        search_mode = data.get('search_mode', 'hybrid')

        if not ingredients:
            return jsonify({'error': 'Please enter some ingredients'}), 400

        # Select search method based on mode
        if search_mode == 'tfidf':
            results = recommender.search_tfidf(ingredients, top_n=top_n)
        elif search_mode == 'semantic':
            results = recommender.search_semantic(ingredients, top_n=top_n)
        elif search_mode == 'llm':  # NEW
            results = recommender.search_llm(ingredients, top_n=1)
        else:  # hybrid (default)
            results = recommender.search_hybrid(ingredients, top_n=top_n)

        return jsonify({
            'success': True,
            'query': ingredients,
            'method': results['method'],
            'corrections': results.get('corrections', []),
            'recommendations': results['results'],
            'total_found': len(results['results'])
        })

    except Exception as e:
        print(f"ERROR in /api/recommend: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Server error occurred. Please try again.'}), 500


@app.route('/api/stats')
def stats():
    """Get system statistics"""
    try:
        return jsonify({
            'total_recipes': recommender.recipe_tfidf.shape[0],
            'vocabulary_size': len(recommender.vocab),
            'embedding_dimensions': recommender.embeddings.shape[1],
            'datasets': {
                'recipenlg': 'RecipeNLG',
                'archanas': 'Archana\'s Kitchen'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NEW: Health check endpoint
@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'recommender': 'loaded',
        'models': {
            'tfidf': True,
            'embeddings': True
        }
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Flask Recipe Recommender Server")
    print("="*60)
    print(f"📊 Total recipes: {recommender.recipe_tfidf.shape[0]:,}")
    print(f"📚 Vocabulary size: {len(recommender.vocab):,}")
    print(f"🧠 Embedding dimensions: {recommender.embeddings.shape[1]}")
    print("="*60)
    print("\n🌐 Server starting at http://localhost:5000")
    print("Press CTRL+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
