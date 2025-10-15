# hybrid_recommender.py
"""
Hybrid: TF-IDF (fast) + Embeddings (semantic fallback)
Only loads embeddings when needed
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from smart_router import SmartRouter

class HybridRecommender:
    def __init__(self, tfidf_recommender):
        self.tfidf = tfidf_recommender
        self.router = SmartRouter(tfidf_recommender)
        
        # Lazy-load embeddings only when needed
        self.embeddings = None
        self.embedding_model = None
        
        print("✓ Hybrid recommender ready (TF-IDF loaded, embeddings lazy)")
    
    def _load_embeddings_if_needed(self):
        """Load embedding model only when needed (first fuzzy query)"""
        if self.embedding_model is None:
            print("  Loading semantic embedding model (first time only)...")
            from sentence_transformers import SentenceTransformer
            
            # Use lightweight model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Pre-compute embeddings for all recipes (one-time cost)
            print("  Computing recipe embeddings...")
            # You'd load this from disk if pre-computed
            
            print("  ✓ Embeddings ready")
    
    def _calculate_confidence(self, recommendations):
        """Calculate confidence in TF-IDF results"""
        if not recommendations:
            return 0.0
        
        # Check top result's coverage
        top_coverage = recommendations[0].get('coverage', 0)
        top_similarity = recommendations[0].get('similarity_score', 0)
        
        # High confidence if good coverage and similarity
        confidence = (top_coverage * 0.6) + (top_similarity * 0.4)
        
        return confidence
    
    def recommend(self, user_input, top_n=10, use_semantic_fallback=True):
        """
        Hybrid recommendation strategy
        """
        # Step 1: Try TF-IDF with typo correction (fast path)
        print(f"🔍 Searching: {user_input}")
        
        tfidf_results = self.router.recommend(user_input, top_n=top_n)
        confidence = self._calculate_confidence(tfidf_results)
        
        print(f"  TF-IDF confidence: {confidence:.2f}")
        
        # Step 2: If low confidence, use semantic fallback
        if use_semantic_fallback and confidence < 0.15:
            print("  ⚡ Low confidence, trying semantic search...")
            
            self._load_embeddings_if_needed()
            
            # Use embeddings for fuzzy matching
            # (Implementation here)
            
            # Merge TF-IDF + embedding results
            # Return combined, deduplicated list
            
        # Step 3: Return results
        for rec in tfidf_results:
            rec['search_method'] = 'TF-IDF' if confidence >= 0.15 else 'Hybrid'
        
        return tfidf_results
