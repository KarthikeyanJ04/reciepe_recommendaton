import pandas as pd
import numpy as np
import pickle
import sqlite3
import json
import time
import gc
import os
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import load_npz
from difflib import get_close_matches
from sentence_transformers import SentenceTransformer
import torch
import re

print("\n" + "="*80)
print("CREATING HYBRID RECOMMENDER")
print("="*80)

class HybridRecipeRecommender:
    """
    Hybrid recommender with TF-IDF, Semantic, and optional LLM (KhaanaGPT)
    """

    def __init__(self, model_path='models/'):
        print("\nInitializing hybrid recommender...")

        # 1. Load TF-IDF
        print("  Loading TF-IDF...")
        with open(f'{model_path}recipe_tfidf_vectorizer.pkl', 'rb') as f:
            self.tfidf = pickle.load(f)
        self.recipe_tfidf = load_npz(f'{model_path}recipe_tfidf_matrix.npz')
        print(f"    ✓ {self.recipe_tfidf.shape[0]:,} recipes indexed")
        print(f"    ✓ Vocabulary size: {len(self.tfidf.vocabulary_):,} ingredients")

        # 2. Load embeddings (MEMORY MAPPED)
        print("  Loading embeddings (memory-mapped)...")
        self.embeddings = np.load(f'{model_path}recipe_embeddings.npy', mmap_mode='r')
        print(f"    ✓ {self.embeddings.shape[0]:,} embeddings × {self.embeddings.shape[1]} dims")
        print(f"    ✓ Using memory-mapping (low RAM usage)")

        # 3. Load sentence transformer
        print("  Loading sentence transformer...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        if torch.cuda.is_available():
            self.embedding_model = self.embedding_model.to('cuda')
            print(f"    ✓ Model on GPU")
        else:
            print(f"    ✓ Model on CPU")

        # 4. Connect to database
        print("  Connecting to recipe database...")
        self.db_conn = sqlite3.connect(f'{model_path}recipes.db', check_same_thread=False)
        self.db_conn.row_factory = sqlite3.Row

        cursor = self.db_conn.execute("SELECT COUNT(*) FROM recipes")
        recipe_count = cursor.fetchone()[0]
        print(f"    ✓ {recipe_count:,} recipes in database")

        # 5. Build vocabulary for typo correction
        self.vocab = set(self.tfidf.vocabulary_.keys())
        print(f"    ✓ {len(self.vocab):,} ingredient vocabulary")

        # 6. Load LLM (KhaanaGPT)
        self.llm_pipeline = None
        self.llm_enabled = False
        try:
            print("  Loading LLM for recipe generation...")
            from transformers import pipeline
            
            model_path_llm = 'models/khaanaGPT'
            if os.path.exists(model_path_llm):
                self.llm_pipeline = pipeline(
                    task='text-generation',
                    model=model_path_llm,
                    device=0 if torch.cuda.is_available() else -1
                )
                self.llm_enabled = True
                print("    ✓ LLM loaded successfully (KhaanaGPT)")
            else:
                print(f"    ⚠ Model not found at {model_path_llm}")
        except Exception as e:
            print(f"    ⚠ LLM not available: {e}")

        print(f"\n✓ Recommender ready!")
        print(f"  TF-IDF: ✓  |  Semantic: ✓  |  LLM: {'✓' if self.llm_enabled else '✗'}")

    # ---------------------------------------------------------------------
    # Helper Functions
    # ---------------------------------------------------------------------

    def _fix_typos(self, user_input):
        words = user_input.lower().split()
        corrected, corrections = [], []
        for word in words:
            if word in self.vocab:
                corrected.append(word)
            else:
                match = get_close_matches(word, self.vocab, n=1, cutoff=0.75)
                if match:
                    corrected.append(match[0])
                    corrections.append(f"{word}→{match[0]}")
                else:
                    corrected.append(word)
        return ' '.join(corrected), corrections

    def _get_recipes(self, indices):
        if hasattr(indices, 'tolist'):
            indices = indices.tolist()
        if len(indices) == 0:
            return {}
        max_idx = self.recipe_tfidf.shape[0] - 1
        valid_indices = [int(i) for i in indices if 0 <= int(i) <= max_idx]
        if len(valid_indices) == 0:
            return {}

        placeholders = ','.join(['?'] * len(valid_indices))
        query = f"SELECT * FROM recipes WHERE idx IN ({placeholders})"
        try:
            cursor = self.db_conn.execute(query, valid_indices)
            return {row['idx']: dict(row) for row in cursor.fetchall()}
        except Exception as e:
            print(f"  ⚠ Database error: {e}")
            return {}

    def _parse_list_field(self, field_value):
        if not field_value or field_value == 'nan' or pd.isna(field_value):
            return []
        s = str(field_value).strip()
        if not s:
            return []

        # JSON-style
        if s.startswith('['):
            try:
                parsed = json.loads(s.replace("'", '"'))
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if x and str(x).strip() != 'nan']
            except Exception:
                pass

        # newline split
        if '\n' in s:
            return [x.strip() for x in s.split('\n') if x.strip() and x.strip() != 'nan']

        # sentence split
        if any(w in s.lower() for w in ['bake', 'cook', 'mix', 'heat', 'add']):
            sentences = re.split(r'\.\s+(?=[A-Z])', s)
            steps = []
            for st in sentences:
                st = st.strip()
                if st and len(st) > 10:
                    if not st.endswith('.'):
                        st += '.'
                    steps.append(st)
            if steps:
                return steps
        return [s] if s else []

    def _format_results(self, indices, scores, user_input):
        recipes_dict = self._get_recipes(indices)
        user_set = set(user_input.lower().split())
        results = []

        for rank, (idx, score) in enumerate(zip(indices, scores), 1):
            if idx not in recipes_dict:
                continue
            recipe = recipes_dict[idx]
            recipe_ing_str = str(recipe.get('cleaned_ingredients', '')).lower()
            recipe_ing_str = recipe_ing_str.strip('[]').replace('"', '').replace("'", '')
            recipe_ing = set(recipe_ing_str.split()) if recipe_ing_str else set()
            matching = user_set.intersection(recipe_ing)
            missing = recipe_ing.difference(user_set)
            coverage = len(matching) / len(recipe_ing) if recipe_ing else 0

            ingredients_raw = recipe.get('ingredients_raw') or recipe.get('ingredients', '')
            ingredients_list = self._parse_list_field(ingredients_raw)
            directions_raw = recipe.get('instructions') or recipe.get('directions', '')
            directions_list = self._parse_list_field(directions_raw)

            description = recipe.get('description', '') or ''
            image_url = recipe.get('image_url', '') or ''

            results.append({
                'rank': rank,
                'title': str(recipe.get('name', 'Unknown Recipe')),
                'description': description,
                'cuisine': str(recipe.get('cuisine', '')),
                'course': str(recipe.get('course', '')),
                'diet': str(recipe.get('diet', '')),
                'dataset': str(recipe.get('dataset', '')),
                'score': float(score),
                'coverage': float(coverage),
                'coverage_percent': round(coverage * 100, 1),
                'link': str(recipe.get('link', '') or image_url),
                'image_url': image_url,
                'ingredients': ingredients_list,
                'directions': directions_list,
                'matching_ingredients': sorted(list(matching)),
                'missing_ingredients': sorted(list(missing))[:5],
                'num_missing': len(missing)
            })

        results.sort(key=lambda x: x['coverage'], reverse=True)
        for i, r in enumerate(results, 1):
            r['rank'] = i
        return results

    # ---------------------------------------------------------------------
    # Search Methods
    # ---------------------------------------------------------------------

    def search_tfidf(self, user_input, top_n=10):
        corrected, corrections = self._fix_typos(user_input)
        user_tfidf = self.tfidf.transform([corrected])
        sims = cosine_similarity(user_tfidf, self.recipe_tfidf)[0]
        top_idx = np.argsort(sims)[-(top_n * 3):][::-1]
        results = self._format_results(top_idx[:top_n], sims[top_idx[:top_n]], corrected)
        return {
            'method': 'TF-IDF',
            'original_query': user_input,
            'corrected_query': corrected,
            'corrections': corrections,
            'results': results
        }

    def search_semantic(self, user_input, top_n=10):
        query_emb = self.embedding_model.encode(
            [user_input.lower()],
            convert_to_numpy=True,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            normalize_embeddings=True
        )
        CHUNK_SIZE = 50000
        all_scores = []
        for i in range(0, self.embeddings.shape[0], CHUNK_SIZE):
            chunk = np.array(self.embeddings[i:i+CHUNK_SIZE])
            chunk_scores = np.dot(chunk, query_emb.T).flatten()
            all_scores.append(chunk_scores)
            del chunk
            gc.collect()

        scores = np.concatenate(all_scores)
        top_idx = np.argsort(scores)[-(top_n * 2):][::-1]
        results = self._format_results(top_idx[:top_n], scores[top_idx[:top_n]], user_input)
        return {'method': 'Semantic', 'query': user_input, 'results': results}

    # ---------------------------------------------------------------------
    # Fixed LLM Section
    # ---------------------------------------------------------------------

    def search_llm(self, user_input, top_n=1):
        """Generate recipe using KhaanaGPT with proper ingredients/instructions split."""
        if not self.llm_enabled:
            return {
                'method': 'LLM',
                'query': user_input,
                'error': 'LLM model not loaded',
                'results': []
            }

        print(f"  Generating recipe with KhaanaGPT for: {user_input}")

        def create_prompt(ingredients):
            ingredients = ','.join([x.strip().lower() for x in ingredients.split(',')])
            ingredients = ingredients.strip().replace(',', '\n')
            return f"<|startoftext|>Ingredients:\n{ingredients}\n"

        prompt = create_prompt(user_input)
        print(prompt)

        try:
            output = self.llm_pipeline(
                prompt,
                max_new_tokens=512,
                penalty_alpha=0.6,
                top_k=4,
                pad_token_id=50259
            )[0]['generated_text']

            # Remove the prompt from output if present
            generated_text = output.replace(prompt, '', 1).strip() if prompt in output else output.strip()

            # -----------------------
            # Split ingredients & directions by headers
            # -----------------------
            ingredients_list = []
            directions_list = []

            split_match = re.split(r'(?i)ingredients:|instructions:', generated_text)
            if len(split_match) == 3:
                # split_match[1] = ingredients, split_match[2] = instructions
                ingredients_list = [l.strip() for l in split_match[1].split('\n') if l.strip()]
                directions_list = [l.strip() for l in split_match[2].split('\n') if l.strip()]
            elif len(split_match) == 2:
                ingredients_list = [l.strip() for l in split_match[1].split('\n') if l.strip()]
            else:
                # fallback heuristic
                lines = [l.strip() for l in generated_text.split('\n') if l.strip()]
                found_directions = False
                for line in lines:
                    if not found_directions:
                        if line.endswith('.') or any(verb in line.lower() for verb in [
                            'heat', 'add', 'mix', 'cook', 'stir', 'boil', 'fry', 'pour', 'serve', 'allow'
                        ]):
                            found_directions = True
                            directions_list.append(line)
                        else:
                            ingredients_list.append(line)
                    else:
                        directions_list.append(line)

            result = {
                'rank': 1,
                'title': "AI Generated Recipe",
                'description': f'AI-generated recipe using: {user_input}',
                'cuisine': 'Indian',
                'course': 'Main Course',
                'diet': 'Vegetarian',
                'dataset': 'KhaanaGPT',
                'score': 1.0,
                'coverage': 100.0,
                'coverage_percent': 100.0,
                'link': '',
                'image_url': '',
                'ingredients': ingredients_list,
                'directions': directions_list,
                'matching_ingredients': [],
                'missing_ingredients': [],
                'num_missing': 0
            }

            return {
                'method': 'LLM (KhaanaGPT)',
                'query': user_input,
                'results': [result]
            }

        except Exception as e:
            print(f"  ⚠ Generation error: {e}")
            return {'method': 'LLM', 'query': user_input, 'error': str(e), 'results': []}

    # ---------------------------------------------------------------------
    # Hybrid combination
    # ---------------------------------------------------------------------

    def search_hybrid(self, user_input, top_n=10, semantic_fallback=True):
        tfidf_results = self.search_tfidf(user_input, top_n=top_n)
        has_good_results = (
            tfidf_results['results'] and
            tfidf_results['results'][0]['coverage'] > 0.50
        )

        if has_good_results or not semantic_fallback:
            tfidf_results['method'] = 'Hybrid (TF-IDF only)'
            return tfidf_results

        semantic_results = self.search_semantic(user_input, top_n=top_n)
        seen_titles, combined = set(), []

        for r in tfidf_results['results']:
            if r['title'] not in seen_titles:
                seen_titles.add(r['title'])
                combined.append(r)

        for r in semantic_results['results']:
            if r['title'] not in seen_titles and len(combined) < top_n:
                r['from_semantic'] = True
                seen_titles.add(r['title'])
                combined.append(r)

        for i, r in enumerate(combined[:top_n], 1):
            r['rank'] = i

        return {
            'method': 'Hybrid',
            'original_query': user_input,
            'corrected_query': tfidf_results.get('corrected_query', user_input),
            'corrections': tfidf_results.get('corrections', []),
            'results': combined[:top_n]
        }


# ---------------------------------------------------------------------
# Standalone test runner
# ---------------------------------------------------------------------
if __name__ == "__main__":
    recommender = HybridRecipeRecommender(model_path='models/')

    test_ingredients = [
        'paneer, cream, tomato, onion',
        'chicken, tomatoes, aloo, jeera, curry powder',
        'rice, potatoes, spinach'
    ]

    for ing in test_ingredients:
        print("="*70)
        print(f"INPUT: {ing}")
        print("="*70)

        if recommender.llm_enabled:
            result = recommender.search_llm(ing)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("⚠ KhaanaGPT model not loaded.")
