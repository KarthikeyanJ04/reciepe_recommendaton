# debug_ingredients.py
"""
Check what's happening with ingredient cleaning
"""

from recommender import RecipeRecommender
import sqlite3

print("Debugging ingredient matching...\n")

# Test what your input becomes
user_input = "tomato chicken onion potato spices"
print(f"Your input: {user_input}")

# Load recommender
recommender = RecipeRecommender()

# Transform and see what happens
user_tfidf = recommender.tfidf.transform([user_input.lower()])
print(f"\nVocabulary check:")

# Check if your words are in vocabulary
for word in user_input.lower().split():
    if word in recommender.tfidf.vocabulary_:
        print(f"  ✓ '{word}' is in vocabulary")
    else:
        print(f"  ✗ '{word}' NOT in vocabulary")

# Show some actual recipe ingredients from database
print(f"\nSample recipes in database:")
conn = sqlite3.connect('models/recipes.db')
conn.row_factory = sqlite3.Row
cursor = conn.execute("SELECT name, ingredients, cleaned_ingredients FROM recipes LIMIT 5")

for row in cursor.fetchall():
    print(f"\n- {row['name']}")
    print(f"  Original: {str(row['ingredients'])[:100]}...")
    print(f"  Cleaned: {str(row['cleaned_ingredients'])[:80]}...")

conn.close()

# Try a direct search
print(f"\n{'='*80}")
print("Testing recommendation...")
results = recommender.recommend(user_input, top_n=10, min_coverage=0.1)
print(f"Found {len(results)} results")

for r in results[:3]:
    print(f"\n{r['rank']}. {r['title']}")
    print(f"   Coverage: {r['coverage']*100:.0f}%")
    print(f"   Matching: {r['common_ingredients']}")
    print(f"   Missing: {r['missing_ingredients'][:3]}")
