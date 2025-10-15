# test_recommender.py
"""
Test the recommender directly to find the error
"""

import sys
import traceback

print("Testing recommender...")

try:
    print("\n1. Importing RecipeRecommender...")
    from recommender import RecipeRecommender
    print("✓ Import successful")
    
    print("\n2. Loading model...")
    recommender = RecipeRecommender(model_path='models/')
    print(f"✓ Model loaded: {len(recommender.recipes)} recipes")
    
    print("\n3. Testing recommendation...")
    test_ingredients = "chicken garlic tomato onion"
    print(f"   Query: {test_ingredients}")
    
    results = recommender.recommend(test_ingredients, top_n=5)
    print(f"✓ Got {len(results)} results")
    
    print("\n4. Checking result format...")
    if results:
        first = results[0]
        print(f"   Title: {first.get('title', 'N/A')}")
        print(f"   Keys: {list(first.keys())}")
        print(f"   Ingredients type: {type(first.get('ingredients'))}")
        print(f"   Directions type: {type(first.get('directions'))}")
    
    print("\n✓ ALL TESTS PASSED!")
    print("\nRecommendations:")
    for i, rec in enumerate(results[:3], 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Coverage: {rec.get('coverage', 0)*100:.0f}%")
        print(f"   Common ingredients: {len(rec.get('common_ingredients', []))}")

except Exception as e:
    print(f"\n❌ ERROR FOUND:")
    print(f"   Type: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print(f"\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
