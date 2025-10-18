import pandas as pd
import numpy as np
import pickle
import sqlite3
import json
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
    Hybrid recommender with TF-IDF and Semantic Search
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

        # 3. Load embedding model (for encoding queries)
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

        # 5. Build vocabulary for spell check
        self.vocab = set(self.tfidf.vocabulary_.keys())
        print(f"    ✓ {len(self.vocab):,} ingredient vocabulary")

        print(f"\n✓ Recommender ready!")
        print(f"  TF-IDF: ✓  |  Semantic: ✓")

    def _fix_typos(self, user_input):
        """Auto-correct typos using vocabulary"""
        words = user_input.lower().split()
        corrected = []
        corrections = []

        for word in words:
            if word in self.vocab:
                corrected.append(word)
            else:
                matches = get_close_matches(word, self.vocab, n=1, cutoff=0.75)
                if matches:
                    corrected.append(matches[0])
                    corrections.append(f"{word}→{matches[0]}")
                else:
                    corrected.append(word)

        return ' '.join(corrected), corrections

    def _get_recipes(self, indices):
        """Fetch recipes from database"""
        if hasattr(indices, 'tolist'):
            indices = indices.tolist()

        if len(indices) == 0:
            return {}

        max_idx = self.recipe_tfidf.shape[0] - 1
        valid_indices = [int(idx) for idx in indices if 0 <= int(idx) <= max_idx]

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
        """Parse ingredients or directions from various formats"""
        if not field_value or field_value == 'nan' or pd.isna(field_value):
            return []
        
        field_str = str(field_value).strip()
        if not field_str:
            return []
        
        if field_str.startswith('['):
            try:
                field_str_fixed = field_str.replace("'", '"')
                parsed = json.loads(field_str_fixed)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip() and str(item).strip() != 'nan']
            except json.JSONDecodeError:
                try:
                    content = field_str.strip('[]')
                    matches = re.findall(r'["\']([^"\']+)["\']', content)
                    if matches:
                        items = [m.strip() for m in matches if m.strip() and m.strip() != 'nan']
                        if items:
                            return items
                    
                    items = [item.strip().strip('"\'') for item in content.split(',')]
                    items = [i for i in items if i and i != 'nan']
                    if items:
                        return items
                except:
                    pass
        
        if '\n' in field_str:
            lines = [line.strip() for line in field_str.split('\n') 
                    if line.strip() and line.strip() != 'nan']
            if len(lines) > 1:
                return lines
        
        if any(word in field_str.lower() for word in ['bake', 'cook', 'mix', 'pour', 'add', 'place', 'heat']):
            sentences = re.split(r'\.\s+(?=[A-Z])', field_str)
            if len(sentences) > 1:
                steps = []
                for sent in sentences:
                    sent = sent.strip()
                    if sent and len(sent) > 10:
                        if not sent.endswith('.'):
                            sent += '.'
                        steps.append(sent)
                if len(steps) > 1:
                    return steps
        
        return [field_str] if field_str else []

    def _format_results(self, indices, scores, user_input):
        """Format recipe results and sort by coverage"""
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

            description = str(recipe.get('description', '')).strip()
            if description == 'nan' or not description:
                description = ''

            image_url = str(recipe.get('image_url', '')).strip()
            if image_url == 'nan':
                image_url = ''

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

        # Sort by coverage
        results.sort(key=lambda x: x['coverage'], reverse=True)
        
        # Re-assign ranks
        for i, r in enumerate(results, 1):
            r['rank'] = i

        return results

    def search_tfidf(self, user_input, top_n=10):
        """Fast TF-IDF search"""
        corrected, corrections = self._fix_typos(user_input)
        user_tfidf = self.tfidf.transform([corrected])
        similarities = cosine_similarity(user_tfidf, self.recipe_tfidf)[0]
        top_indices = np.argsort(similarities)[-(top_n * 3):][::-1]
        top_scores = similarities[top_indices]
        results = self._format_results(top_indices[:top_n], top_scores[:top_n], corrected)

        return {
            'method': 'TF-IDF',
            'original_query': user_input,
            'corrected_query': corrected,
            'corrections': corrections,
            'results': results
        }

    def search_semantic(self, user_input, top_n=10):
        """Semantic search"""
        query_embedding = self.embedding_model.encode(
            [user_input.lower()],
            convert_to_numpy=True,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            normalize_embeddings=True
        )

        CHUNK_SIZE = 50000
        num_recipes = self.embeddings.shape[0]

        all_scores = []
        for i in range(0, num_recipes, CHUNK_SIZE):
            end_idx = min(i + CHUNK_SIZE, num_recipes)
            chunk = np.array(self.embeddings[i:end_idx])
            chunk_scores = np.dot(chunk, query_embedding.T).flatten()
            all_scores.append(chunk_scores)
            del chunk
            gc.collect()

        scores = np.concatenate(all_scores)
        top_indices = np.argsort(scores)[-(top_n * 2):][::-1]
        top_scores = scores[top_indices]
        results = self._format_results(top_indices[:top_n], top_scores[:top_n], user_input)

        return {
            'method': 'Semantic',
            'query': user_input,
            'results': results
        }

    def search_hybrid(self, user_input, top_n=10, semantic_fallback=True):
        """Hybrid search"""
        tfidf_results = self.search_tfidf(user_input, top_n=top_n)

        has_good_results = (
            tfidf_results['results'] and
            tfidf_results['results'][0]['coverage'] > 0.50
        )

        if has_good_results or not semantic_fallback:
            tfidf_results['method'] = 'Hybrid (TF-IDF only)'
            return tfidf_results

        semantic_results = self.search_semantic(user_input, top_n=top_n)

        seen_titles = set()
        combined = []

        for result in tfidf_results['results']:
            title = result['title']
            if title not in seen_titles:
                seen_titles.add(title)
                combined.append(result)

        for result in semantic_results['results']:
            title = result['title']
            if title not in seen_titles and len(combined) < top_n:
                seen_titles.add(title)
                result['from_semantic'] = True
                combined.append(result)

        for i, r in enumerate(combined[:top_n], 1):
            r['rank'] = i

        return {
            'method': 'Hybrid',
            'original_query': user_input,
            'corrected_query': tfidf_results.get('corrected_query', user_input),
            'corrections': tfidf_results.get('corrections', []),
            'results': combined[:top_n]
        }
