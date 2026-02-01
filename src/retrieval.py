"""
Retrieval Module
Implements hybrid search combining dense vector search and sparse keyword matching
"""

import os
import re
from typing import List, Dict, Optional
from collections import Counter
import logging
import numpy as np

try:
    from .vector_store import FAISSVectorStore
    from .embeddings import EmbeddingGenerator
except ImportError:
    from vector_store import FAISSVectorStore
    from embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid retriever combining dense vector search with keyword matching.
    """
    
    def __init__(
        self,
        index_path: str = None,
        embedding_model: str = None
    ):
        """
        Initialize the retriever.
        
        Args:
            index_path: Path to the FAISS index (without extension)
            embedding_model: Name of the embedding model
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        self.embedding_model = embedding_model or os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        
        # Initialize components
        self.embedding_generator = EmbeddingGenerator(self.embedding_model)
        self.vector_store = FAISSVectorStore()
        
        # Load index if provided
        if index_path:
            self.load_index(index_path)
        
        logger.info("HybridRetriever initialized")
    
    def load_index(self, index_path: str):
        """Load a FAISS index"""
        self.vector_store.load_index(index_path)
        logger.info(f"Loaded index with {self.vector_store.index.ntotal} vectors")
    
    def dense_search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Perform dense vector search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
        
        Returns:
            List of results with scores
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.embed_text(query)
        
        # Search
        results = self.vector_store.search(query_embedding, top_k, threshold)
        
        # Add search type marker
        for r in results:
            r['search_type'] = 'dense'
        
        return results
    
    def sparse_search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Perform sparse keyword search using term frequency.
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of results with keyword scores
        """
        # Tokenize query
        query_terms = self._tokenize(query.lower())
        
        if not query_terms:
            return []
        
        # Score each chunk by keyword overlap
        scored_results = []
        
        for faiss_id, chunk_data in self.vector_store.chunk_mapping.items():
            text = chunk_data.get('text', '').lower()
            chunk_terms = self._tokenize(text)
            
            # Calculate term frequency score
            score = self._calculate_tf_score(query_terms, chunk_terms)
            
            if score > 0:
                scored_results.append({
                    'score': score,
                    'chunk_id': chunk_data.get('chunk_id'),
                    'text': chunk_data.get('text'),
                    'token_count': chunk_data.get('token_count'),
                    'metadata': chunk_data.get('metadata', {}),
                    'filename': chunk_data.get('metadata', {}).get('filename', 'unknown'),
                    'search_type': 'sparse'
                })
        
        # Sort by score and return top-k
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results[:top_k]
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: split on non-alphanumeric chars"""
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Remove very short tokens and common stop words
        stop_words = {'the', 'a', 'an', 'is', 'it', 'of', 'to', 'and', 'in', 'for', 'on', 'with', 'at', 'by', 'from'}
        tokens = [t for t in tokens if len(t) > 2 and t not in stop_words]
        return tokens
    
    def _calculate_tf_score(self, query_terms: List[str], doc_terms: List[str]) -> float:
        """Calculate simple TF-based relevance score"""
        if not query_terms or not doc_terms:
            return 0.0
        
        doc_counter = Counter(doc_terms)
        
        # Count matches
        matches = 0
        for term in query_terms:
            if term in doc_counter:
                matches += 1
        
        # Normalize by query length
        score = matches / len(query_terms)
        
        return score
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Perform hybrid retrieval combining dense and sparse search.
        
        Args:
            query: Search query
            top_k: Number of final results to return
            dense_weight: Weight for dense search scores
            sparse_weight: Weight for sparse search scores
            threshold: Minimum combined score threshold
        
        Returns:
            List of reranked results
        """
        logger.info(f"Retrieving for query: {query[:50]}...")
        
        # Get dense results
        dense_results = self.dense_search(query, top_k=top_k * 2)
        
        # Get sparse results
        sparse_results = self.sparse_search(query, top_k=top_k * 2)
        
        # Combine and rerank
        combined = self._combine_results(
            dense_results,
            sparse_results,
            dense_weight,
            sparse_weight
        )
        
        # Filter by threshold and return top-k
        filtered = [r for r in combined if r['combined_score'] >= threshold]
        
        logger.info(f"Retrieved {len(filtered)} results above threshold {threshold}")
        
        return filtered[:top_k]
    
    def _combine_results(
        self,
        dense_results: List[Dict],
        sparse_results: List[Dict],
        dense_weight: float,
        sparse_weight: float
    ) -> List[Dict]:
        """Combine and rerank results from dense and sparse search"""
        # Create lookup by chunk_id
        results_by_id = {}
        
        # Add dense results
        for r in dense_results:
            chunk_id = r['chunk_id']
            if chunk_id not in results_by_id:
                results_by_id[chunk_id] = {
                    'chunk_id': chunk_id,
                    'text': r['text'],
                    'token_count': r.get('token_count'),
                    'metadata': r.get('metadata', {}),
                    'filename': r['filename'],
                    'dense_score': r['score'],
                    'sparse_score': 0.0
                }
            else:
                results_by_id[chunk_id]['dense_score'] = r['score']
        
        # Add sparse results
        for r in sparse_results:
            chunk_id = r['chunk_id']
            if chunk_id not in results_by_id:
                results_by_id[chunk_id] = {
                    'chunk_id': chunk_id,
                    'text': r['text'],
                    'token_count': r.get('token_count'),
                    'metadata': r.get('metadata', {}),
                    'filename': r['filename'],
                    'dense_score': 0.0,
                    'sparse_score': r['score']
                }
            else:
                results_by_id[chunk_id]['sparse_score'] = r['score']
        
        # Calculate combined scores
        combined = []
        for chunk_id, r in results_by_id.items():
            combined_score = (
                r['dense_score'] * dense_weight +
                r['sparse_score'] * sparse_weight
            )
            r['combined_score'] = combined_score
            combined.append(r)
        
        # Sort by combined score
        combined.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return combined


if __name__ == "__main__":
    # Test the retriever
    import sys
    from pathlib import Path
    
    logging.basicConfig(level=logging.INFO)
    
    # Default index path
    project_root = Path(__file__).parent.parent
    index_path = str(project_root / "data" / "embeddings" / "index_v1")
    
    print("Testing HybridRetriever...")
    
    try:
        retriever = HybridRetriever(index_path=index_path)
        
        # Test queries
        test_queries = [
            "What is the salary for AI engineers?",
            "How does the interview process work?",
            "What benefits does Space42 offer?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            results = retriever.retrieve(query, top_k=3)
            
            for i, r in enumerate(results):
                print(f"  {i+1}. [{r['filename']}] score={r['combined_score']:.3f}")
                print(f"     {r['text'][:100]}...")
        
        print("\n✅ Retriever test passed!")
        
    except FileNotFoundError:
        print("⚠️ Index not found. Run the ingestion pipeline first:")
        print("   python data/generate_sample_docs.py")
        print("   python data/process_documents.py")
