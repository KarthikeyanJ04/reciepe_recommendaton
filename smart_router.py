# smart_router.py
"""
Smart query router with typo detection
Enhances TF-IDF with spell correction
"""

from difflib import get_close_matches
import re

class SmartRouter:
    def __init__(self, tfidf_recommender):
        self.tfidf = tfidf_recommender
        
        # Build ingredient vocabulary from TF-IDF
        self.vocab = set(self.tfidf.tfidf.vocabulary_.keys())
        print(f"✓ Loaded {len(self.vocab):,} ingredient vocabulary")
        
    def correct_typos(self, user_input):
        """
        Auto-correct ingredient typos using vocabulary
        'tamoto' → 'tomato'
        'chiken' → 'chicken'
        """
        words = user_input.lower().split()
        corrected = []
        corrections_made = []
        
        for word in words:
            if word in self.vocab:
                # Word is correct
                corrected.append(word)
            else:
                # Try to find close match
                matches = get_close_matches(word, self.vocab, n=1, cutoff=0.8)
                if matches:
                    corrected.append(matches[0])
                    corrections_made.append(f"{word} → {matches[0]}")
                else:
                    # Keep original if no good match
                    corrected.append(word)
        
        corrected_query = ' '.join(corrected)
        
        return {
            'original': user_input,
            'corrected': corrected_query,
            'corrections': corrections_made,
            'had_typos': len(corrections_made) > 0
        }
    
    def recommend(self, user_input, top_n=10):
        """
        Smart recommendation with typo correction
        """
        # Step 1: Check for and fix typos
        result = self.correct_typos(user_input)
        
        print(f"  Original: {result['original']}")
        if result['had_typos']:
            print(f"  Corrected: {result['corrected']}")
            print(f"  Fixed: {', '.join(result['corrections'])}")
        
        # Step 2: Use TF-IDF with corrected query
        recommendations = self.tfidf.recommend(result['corrected'], top_n=top_n)
        
        # Add correction info to results
        for rec in recommendations:
            rec['query_corrected'] = result['had_typos']
            rec['corrections'] = result['corrections']
        
        return recommendations
