"""
FAISS Vector Store Module
Manages the FAISS index for similarity search
"""

import os
import pickle
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
import numpy as np

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """
    Vector store using FAISS for efficient similarity search.
    Uses IndexFlatIP (Inner Product) for cosine similarity.
    """
    
    def __init__(self, dimension: int = 384):
        """
        Initialize the vector store.
        
        Args:
            dimension: Dimension of embeddings (384 for all-MiniLM-L6-v2)
        """
        import faiss
        
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product = cosine sim for normalized vectors
        self.chunk_mapping = {}  # faiss_id -> chunk data
        self.current_id = 0
        
        logger.info(f"Initialized FAISS index with dimension {dimension}")
    
    def add_embeddings(
        self,
        embeddings: np.ndarray,
        chunks: List[Dict]
    ):
        """
        Add embeddings to the index with corresponding chunk data.
        
        Args:
            embeddings: numpy array of shape (n, dimension)
            chunks: List of chunk dictionaries to associate with embeddings
        """
        if len(embeddings) != len(chunks):
            raise ValueError(f"Embeddings ({len(embeddings)}) and chunks ({len(chunks)}) must have same length")
        
        # Normalize embeddings for cosine similarity
        faiss = __import__('faiss')
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Map FAISS IDs to chunk data
        for i, chunk in enumerate(chunks):
            faiss_id = self.current_id + i
            self.chunk_mapping[faiss_id] = {
                'chunk_id': chunk.get('chunk_id'),
                'text': chunk.get('text'),
                'token_count': chunk.get('token_count'),
                'metadata': chunk.get('metadata', {})
            }
        
        self.current_id += len(chunks)
        logger.info(f"Added {len(chunks)} embeddings to index. Total: {self.index.ntotal}")
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query vector of shape (dimension,)
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)
        
        Returns:
            List of dicts with chunk data and similarity scores
        """
        if self.index.ntotal == 0:
            logger.warning("Index is empty, no results to return")
            return []
        
        # Ensure query is 2D and normalized
        faiss = __import__('faiss')
        query = query_embedding.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query)
        
        # Limit k to available vectors
        k = min(top_k, self.index.ntotal)
        
        # Search
        scores, indices = self.index.search(query, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for not found
                continue
            if score < threshold:
                continue
            
            chunk_data = self.chunk_mapping.get(idx, {})
            results.append({
                'score': float(score),
                'chunk_id': chunk_data.get('chunk_id'),
                'text': chunk_data.get('text'),
                'token_count': chunk_data.get('token_count'),
                'metadata': chunk_data.get('metadata', {}),
                'filename': chunk_data.get('metadata', {}).get('filename', 'unknown')
            })
        
        return results
    
    def save_index(self, filepath: str):
        """
        Save the FAISS index and metadata to disk.
        
        Args:
            filepath: Path to save (without extension)
        """
        import faiss
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = str(path) + '.faiss'
        faiss.write_index(self.index, index_path)
        logger.info(f"Saved FAISS index to {index_path}")
        
        # Save metadata
        metadata_path = str(path) + '.pkl'
        metadata = {
            'dimension': self.dimension,
            'chunk_mapping': self.chunk_mapping,
            'current_id': self.current_id
        }
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        logger.info(f"Saved index metadata to {metadata_path}")
    
    def load_index(self, filepath: str):
        """
        Load the FAISS index and metadata from disk.
        
        Args:
            filepath: Path to load (without extension, or with .faiss)
        """
        import faiss
        
        # Handle paths with or without extension
        path = str(filepath)
        if path.endswith('.faiss'):
            path = path[:-6]
        
        index_path = path + '.faiss'
        metadata_path = path + '.pkl'
        
        # Load FAISS index
        if not Path(index_path).exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        self.index = faiss.read_index(index_path)
        logger.info(f"Loaded FAISS index from {index_path} ({self.index.ntotal} vectors)")
        
        # Load metadata
        if Path(metadata_path).exists():
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            self.dimension = metadata['dimension']
            self.chunk_mapping = metadata['chunk_mapping']
            self.current_id = metadata['current_id']
            logger.info(f"Loaded index metadata ({len(self.chunk_mapping)} chunks)")
        else:
            logger.warning(f"Metadata file not found: {metadata_path}")
    
    def get_stats(self) -> Dict:
        """Get statistics about the index"""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dimension,
            'total_chunks': len(self.chunk_mapping)
        }
    
    def clear(self):
        """Clear the index"""
        import faiss
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunk_mapping = {}
        self.current_id = 0
        logger.info("Cleared index")


if __name__ == "__main__":
    # Test the vector store
    logging.basicConfig(level=logging.INFO)
    
    print("Testing FAISSVectorStore...")
    
    # Create store
    store = FAISSVectorStore(dimension=384)
    
    # Create dummy embeddings and chunks
    np.random.seed(42)
    num_chunks = 10
    embeddings = np.random.randn(num_chunks, 384).astype(np.float32)
    
    chunks = [
        {
            'chunk_id': f'test_chunk_{i}',
            'text': f'This is test chunk number {i}',
            'token_count': 10,
            'metadata': {'filename': f'test_{i}.txt', 'document_type': 'test'}
        }
        for i in range(num_chunks)
    ]
    
    # Add to index
    store.add_embeddings(embeddings, chunks)
    print(f"Index stats: {store.get_stats()}")
    
    # Search
    query = embeddings[0]  # Search for first embedding
    results = store.search(query, top_k=5)
    
    print(f"\nSearch results for chunk 0:")
    for r in results:
        print(f"  - {r['chunk_id']}: score={r['score']:.4f}")
    
    # Save and reload
    store.save_index('/tmp/test_index')
    
    store2 = FAISSVectorStore()
    store2.load_index('/tmp/test_index')
    print(f"\nReloaded index stats: {store2.get_stats()}")
    
    # Search again
    results2 = store2.search(query, top_k=3)
    print(f"\nSearch after reload:")
    for r in results2:
        print(f"  - {r['chunk_id']}: score={r['score']:.4f}")
    
    print("\n✅ All vector store tests passed!")
