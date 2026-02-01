"""
Document Ingestion Pipeline
Orchestrates the full document processing flow: load -> chunk -> embed -> index
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

from .document_loader import load_all_documents
from .chunker import chunk_all_documents
from .embeddings import EmbeddingGenerator, save_chunks_with_embeddings
from .vector_store import FAISSVectorStore

logger = logging.getLogger(__name__)


class DocumentIngestionPipeline:
    """
    End-to-end document ingestion pipeline.
    Processes documents from raw files to searchable vector index.
    """
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        embedding_model: str = None
    ):
        """
        Initialize the pipeline.
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            embedding_model: Name of the embedding model
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        self.chunk_size = chunk_size or int(os.getenv('CHUNK_SIZE', 500))
        self.chunk_overlap = chunk_overlap or int(os.getenv('CHUNK_OVERLAP', 50))
        self.embedding_model = embedding_model or os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        
        self.embedding_generator = None
        self.vector_store = None
        
        logger.info(f"Pipeline initialized: chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    def process_directory(
        self,
        input_dir: str,
        output_dir: str,
        index_name: str = "index_v1"
    ) -> Dict:
        """
        Process all documents in a directory.
        
        Args:
            input_dir: Directory containing raw documents
            output_dir: Directory to save processed data
            index_name: Name for the FAISS index
        
        Returns:
            Dict with processing statistics
        """
        start_time = datetime.now()
        stats = {
            'input_dir': input_dir,
            'output_dir': output_dir,
            'started_at': start_time.isoformat()
        }
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Load documents
        logger.info(f"Step 1/4: Loading documents from {input_dir}")
        documents = load_all_documents(input_dir)
        stats['documents_loaded'] = len(documents)
        
        if not documents:
            logger.error("No documents found!")
            return stats
        
        logger.info(f"  Loaded {len(documents)} documents")
        
        # Step 2: Chunk documents
        logger.info(f"Step 2/4: Chunking documents (size={self.chunk_size}, overlap={self.chunk_overlap})")
        chunks = chunk_all_documents(documents, self.chunk_size, self.chunk_overlap)
        stats['chunks_created'] = len(chunks)
        
        if not chunks:
            logger.error("No chunks created!")
            return stats
        
        logger.info(f"  Created {len(chunks)} chunks")
        
        # Step 3: Generate embeddings
        logger.info(f"Step 3/4: Generating embeddings with {self.embedding_model}")
        self.embedding_generator = EmbeddingGenerator(self.embedding_model)
        chunks = self.embedding_generator.embed_chunks(chunks, batch_size=32)
        
        dimension = self.embedding_generator.get_dimension()
        stats['embedding_dimension'] = dimension
        logger.info(f"  Generated embeddings (dimension={dimension})")
        
        # Save chunks with embeddings
        chunks_path = output_path / "chunks.pkl"
        save_chunks_with_embeddings(chunks, str(chunks_path))
        
        # Step 4: Build and save FAISS index
        logger.info("Step 4/4: Building FAISS index")
        self.vector_store = FAISSVectorStore(dimension=dimension)
        
        # Extract embeddings into numpy array
        import numpy as np
        embeddings = np.array([chunk['embedding'] for chunk in chunks])
        
        # Remove embeddings from chunks to save in metadata (they're in the index)
        chunks_without_embeddings = []
        for chunk in chunks:
            chunk_copy = chunk.copy()
            del chunk_copy['embedding']
            chunks_without_embeddings.append(chunk_copy)
        
        self.vector_store.add_embeddings(embeddings, chunks_without_embeddings)
        
        # Save index
        index_path = output_path / index_name
        self.vector_store.save_index(str(index_path))
        stats['index_path'] = str(index_path) + '.faiss'
        
        # Calculate stats
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        stats.update({
            'completed_at': end_time.isoformat(),
            'duration_seconds': duration,
            'total_vectors': self.vector_store.index.ntotal
        })
        
        # Save processing report
        report_path = output_path / "ingestion_report.json"
        with open(report_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Pipeline complete in {duration:.2f}s")
        logger.info(f"  Documents: {stats['documents_loaded']}")
        logger.info(f"  Chunks: {stats['chunks_created']}")
        logger.info(f"  Index: {stats['index_path']}")
        
        return stats
    
    def get_vector_store(self) -> Optional[FAISSVectorStore]:
        """Get the vector store (after processing)"""
        return self.vector_store
    
    def get_embedding_generator(self) -> Optional[EmbeddingGenerator]:
        """Get the embedding generator"""
        return self.embedding_generator


def run_pipeline(input_dir: str = None, output_dir: str = None):
    """
    Run the ingestion pipeline with default paths.
    
    Args:
        input_dir: Override default input directory
        output_dir: Override default output directory
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Default paths relative to project root
    base_path = Path(__file__).parent.parent
    
    if input_dir is None:
        input_dir = str(base_path / "data" / "raw")
    
    if output_dir is None:
        output_dir = str(base_path / "data" / "embeddings")
    
    print("=" * 60)
    print("🚀 Y2MA Document Ingestion Pipeline")
    print("=" * 60)
    print()
    
    pipeline = DocumentIngestionPipeline()
    stats = pipeline.process_directory(input_dir, output_dir)
    
    print()
    print("=" * 60)
    print("✅ Pipeline Complete")
    print("=" * 60)
    print(f"   Documents loaded: {stats.get('documents_loaded', 0)}")
    print(f"   Chunks created: {stats.get('chunks_created', 0)}")
    print(f"   Index saved to: {stats.get('index_path', 'N/A')}")
    print(f"   Duration: {stats.get('duration_seconds', 0):.2f}s")
    print()
    
    return stats


if __name__ == "__main__":
    import sys
    
    input_dir = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    run_pipeline(input_dir, output_dir)
