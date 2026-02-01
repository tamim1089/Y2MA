"""
Embedding Generator Module
Uses sentence-transformers to create embeddings for text chunks
"""

import os
import pickle
from typing import List, Union
from pathlib import Path
import logging
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
                       Defaults to all-MiniLM-L6-v2 (384 dimensions)
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        if model_name is None:
            model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        
        self.model_name = model_name
        self.model = None
        self.dimension = None
    
    def _load_model(self):
        """Lazy load the model on first use"""
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading embedding model: {self.model_name}")
            # Force CPU to avoid CUDA compatibility issues
            self.model = SentenceTransformer(self.model_name, device='cpu')
            
            # Determine embedding dimension
            test_embedding = self.model.encode("test")
            self.dimension = len(test_embedding)
            logger.info(f"Model loaded on CPU. Embedding dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
        
        Returns:
            numpy array of shape (dimension,)
        """
        self._load_model()
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar
        
        Returns:
            numpy array of shape (num_texts, dimension)
        """
        self._load_model()
        
        logger.info(f"Embedding {len(texts)} texts in batches of {batch_size}")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
    
    def embed_chunks(
        self,
        chunks: List[dict],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> List[dict]:
        """
        Embed a list of chunk dictionaries and add embeddings to each.
        
        Args:
            chunks: List of chunk dicts (must have 'text' key)
            batch_size: Batch size for embedding
            show_progress: Whether to show progress
        
        Returns:
            Same chunks with 'embedding' key added
        """
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embed_batch(texts, batch_size, show_progress)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding
        
        return chunks
    
    def save_embeddings(
        self,
        embeddings: np.ndarray,
        filepath: str
    ):
        """Save embeddings to disk"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        np.save(str(path), embeddings)
        logger.info(f"Saved embeddings to {filepath}")
    
    def load_embeddings(self, filepath: str) -> np.ndarray:
        """Load embeddings from disk"""
        embeddings = np.load(filepath)
        logger.info(f"Loaded embeddings from {filepath}: shape {embeddings.shape}")
        return embeddings
    
    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        self._load_model()
        return self.dimension


def save_chunks_with_embeddings(chunks: List[dict], filepath: str):
    """Save chunks (including embeddings) to a pickle file"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'wb') as f:
        pickle.dump(chunks, f)
    
    logger.info(f"Saved {len(chunks)} chunks to {filepath}")


def load_chunks_with_embeddings(filepath: str) -> List[dict]:
    """Load chunks (including embeddings) from a pickle file"""
    with open(filepath, 'rb') as f:
        chunks = pickle.load(f)
    
    logger.info(f"Loaded {len(chunks)} chunks from {filepath}")
    return chunks


if __name__ == "__main__":
    # Test the embedding generator
    logging.basicConfig(level=logging.INFO)
    
    print("Testing EmbeddingGenerator...")
    
    generator = EmbeddingGenerator()
    
    # Test single embedding
    test_text = "What is the salary range for AI engineers at Space42?"
    embedding = generator.embed_text(test_text)
    print(f"Single embedding shape: {embedding.shape}")
    print(f"Embedding dimension: {generator.get_dimension()}")
    
    # Test batch embedding
    test_texts = [
        "Space42 is an AI and space technology company.",
        "The interview process consists of 6 steps.",
        "We offer 30 days of annual leave.",
    ]
    
    embeddings = generator.embed_batch(test_texts, show_progress=False)
    print(f"Batch embeddings shape: {embeddings.shape}")
    
    # Test with chunks
    test_chunks = [
        {'chunk_id': 'test_0', 'text': test_texts[0]},
        {'chunk_id': 'test_1', 'text': test_texts[1]},
        {'chunk_id': 'test_2', 'text': test_texts[2]},
    ]
    
    embedded_chunks = generator.embed_chunks(test_chunks, show_progress=False)
    print(f"Embedded {len(embedded_chunks)} chunks")
    print(f"First chunk embedding shape: {embedded_chunks[0]['embedding'].shape}")
    
    print("\n✅ All embedding tests passed!")
