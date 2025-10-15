# ============================================================================
# RETRAIN TF-IDF VECTORIZER WITH BIG VOCABULARY
# ============================================================================

import pandas as pd
import numpy as np
import sqlite3
import pickle
import time
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import save_npz

print("="*80)
print("RETRAINING TF-IDF VECTORIZER (BIG VOCABULARY)")
print("="*80)

# ============================================================================
# LOAD RECIPES FROM DATABASE
# ============================================================================

print("\n" + "="*80)
print("LOADING RECIPES FROM DATABASE")
print("="*80)

conn = sqlite3.connect('models/recipes.db')

print("\nLoading all recipes...")
start = time.time()

df = pd.read_sql_query("SELECT idx, name, cleaned_ingredients FROM recipes", conn)
conn.close()

print(f"✓ Loaded {len(df):,} recipes in {time.time()-start:.1f}s")

# ============================================================================
# PREPARE CLEANED INGREDIENTS
# ============================================================================

print("\n" + "="*80)
print("PREPARING INGREDIENT TEXT")
print("="*80)

print("\nProcessing cleaned ingredients...")
start = time.time()

def clean_ingredient_text(text):
    """Clean ingredient text for TF-IDF"""
    if pd.isna(text) or not text:
        return ''
    
    text = str(text).lower().strip()
    
    # Remove JSON brackets and quotes if present
    text = text.strip('[]').replace('"', '').replace("'", '')
    
    # Remove commas
    text = text.replace(',', ' ')
    
    return text

df['cleaned_text'] = df['cleaned_ingredients'].apply(clean_ingredient_text)

# Filter out empty ingredients
df = df[df['cleaned_text'].str.len() > 5]
df = df.reset_index(drop=True)

print(f"✓ Processed {len(df):,} recipes in {time.time()-start:.1f}s")

print("\nExample ingredient texts:")
for i in range(3):
    print(f"\n{i+1}. {df['name'].iloc[i]}")
    print(f"   Ingredients: {df['cleaned_text'].iloc[i][:100]}...")

# ============================================================================
# TRAIN TF-IDF VECTORIZER (BIG VOCABULARY)
# ============================================================================

print("\n" + "="*80)
print("TRAINING TF-IDF VECTORIZER (BIG VOCABULARY)")
print("="*80)

print("\nInitializing TF-IDF vectorizer with BIG vocabulary...")
print("Settings:")
print("  - max_features: None (NO LIMIT - capture ALL ingredients!)")
print("  - min_df: 2 (ingredient must appear in at least 2 recipes)")
print("  - max_df: 0.95 (ignore only super-common words in >95% of recipes)")
print("  - ngram_range: (1,3) (1-word, 2-word, and 3-word ingredient phrases)")

vectorizer = TfidfVectorizer(
    max_features=None,           # NO LIMIT!
    min_df=2,                     
    max_df=0.95,                  
    ngram_range=(1, 3),           
    lowercase=True,
    token_pattern=r'\b[a-z]{2,}\b'
)

print(f"\nFitting vectorizer on {len(df):,} recipes...")
print("This will create a LARGE vocabulary to match rare/specific ingredients...")
start = time.time()

tfidf_matrix = vectorizer.fit_transform(df['cleaned_text'])

elapsed = time.time() - start
print(f"\n✓ TF-IDF training complete in {elapsed:.1f}s")

print(f"\nTF-IDF Matrix Statistics:")
print(f"  Shape: {tfidf_matrix.shape} (recipes × ingredients)")
print(f"  Non-zero entries: {tfidf_matrix.nnz:,}")
print(f"  Density: {tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1]) * 100:.4f}%")
print(f"  Vocabulary size: {len(vectorizer.vocabulary_):,} unique ingredients/phrases")
print(f"  Memory size: ~{tfidf_matrix.data.nbytes / 1024**2:.1f} MB")

# Show top single-word and multi-word ingredients
print("\nTop 20 most common single-word ingredients:")
feature_names = vectorizer.get_feature_names_out()
doc_frequencies = (tfidf_matrix > 0).sum(axis=0).A1

# Filter single words
single_words = [(i, name) for i, name in enumerate(feature_names) if ' ' not in name]
single_word_indices = [i for i, _ in single_words[:]]
single_word_freqs = doc_frequencies[single_word_indices]
top_single = single_word_freqs.argsort()[-20:][::-1]

for rank, idx in enumerate(top_single, 1):
    ingredient = feature_names[single_word_indices[idx]]
    count = single_word_freqs[idx]
    print(f"  {rank:2d}. {ingredient:20s} ({count:,} recipes)")

print("\nTop 20 most common multi-word ingredient phrases:")
multi_words = [(i, name) for i, name in enumerate(feature_names) if ' ' in name]
multi_word_indices = [i for i, _ in multi_words[:]]
multi_word_freqs = doc_frequencies[multi_word_indices]

if len(multi_word_freqs) > 0:
    top_multi = multi_word_freqs.argsort()[-20:][::-1]
    
    for rank, idx in enumerate(top_multi, 1):
        ingredient = feature_names[multi_word_indices[idx]]
        count = multi_word_freqs[idx]
        print(f"  {rank:2d}. {ingredient:30s} ({count:,} recipes)")

# ============================================================================
# BACKUP OLD FILES AND SAVE NEW ONES
# ============================================================================

print("\n" + "="*80)
print("SAVING TF-IDF MODEL")
print("="*80)

vectorizer_file = 'models/recipe_tfidf_vectorizer.pkl'
matrix_file = 'models/recipe_tfidf_matrix.npz'

if os.path.exists(vectorizer_file):
    print("\nBacking up old TF-IDF files...")
    os.rename(vectorizer_file, 'models/recipe_tfidf_vectorizer_old_backup.pkl')
    os.rename(matrix_file, 'models/recipe_tfidf_matrix_old_backup.npz')
    print("✓ Old files backed up")

print("\nSaving new TF-IDF model...")

with open(vectorizer_file, 'wb') as f:
    pickle.dump(vectorizer, f)

vectorizer_size = os.path.getsize(vectorizer_file) / 1024**2
print(f"✓ Vectorizer saved: {vectorizer_size:.2f} MB")

save_npz(matrix_file, tfidf_matrix)

matrix_size = os.path.getsize(matrix_file) / 1024**2
print(f"✓ TF-IDF matrix saved: {matrix_size:.2f} MB")

# ============================================================================
# TEST TF-IDF SEARCH
# ============================================================================

print("\n" + "="*80)
print("TESTING TF-IDF SEARCH")
print("="*80)

test_queries = [
    "tomato onion potato curry leaves",
    "chicken ginger garlic garam masala",
    "paneer butter cream tomato"
]

from sklearn.metrics.pairwise import cosine_similarity

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"Test query: '{query}'")
    print('='*60)
    
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, tfidf_matrix)[0]
    
    top_indices = similarities.argsort()[-5:][::-1]
    top_scores = similarities[top_indices]
    
    print("\nTop 5 TF-IDF matches:")
    for rank, (idx, score) in enumerate(zip(top_indices, top_scores), 1):
        recipe_name = df['name'].iloc[idx]
        ingredients = df['cleaned_text'].iloc[idx][:60]
        print(f"  {rank}. {recipe_name}")
        print(f"     Score: {score:.3f} | Ingredients: {ingredients}...")

# ============================================================================
# DONE
# ============================================================================

print("\n" + "="*80)
print("✅ TF-IDF RETRAINING COMPLETE!")
print("="*80)

print(f"""
Successfully retrained TF-IDF vectorizer with BIG vocabulary!

📊 Summary:
   - Total recipes: {len(df):,}
   - Vocabulary size: {len(vectorizer.vocabulary_):,} unique terms
   - TF-IDF matrix: {tfidf_matrix.shape[0]:,} × {tfidf_matrix.shape[1]:,}
   - Matrix size: {matrix_size:.2f} MB
   - Training time: {elapsed:.1f} seconds

✅ Big vocabulary benefits:
   - Captures rare ingredients (kaffir lime, asafoetida, etc.)
   - Multi-word phrases (curry leaves, garam masala powder)
   - Better matching for diverse cuisines
   - More precise ingredient matching

📥 Next step:
   python retrain_embeddings_final.py

Your TF-IDF now has MAXIMUM matching power! 🚀
""")
