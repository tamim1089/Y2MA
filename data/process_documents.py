#!/usr/bin/env python3
"""
Process Documents Script
Run this to process all documents and build the FAISS index.

Usage: python data/process_documents.py
"""

import sys
import os
from pathlib import Path

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# Change to project root for correct .env loading
os.chdir(project_root)

import json
import logging
from datetime import datetime

# Now import the modules directly
from document_loader import load_all_documents
from chunker import chunk_all_documents
from embeddings import EmbeddingGenerator, save_chunks_with_embeddings
from vector_store import FAISSVectorStore

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_pipeline():
    """Run the full document ingestion pipeline"""
    
    input_dir = str(project_root / "data" / "raw")
    output_dir = str(project_root / "data" / "embeddings")
    
    print("=" * 60)
    print("🚀 Y2MA Document Ingestion Pipeline")
    print("=" * 60)
    print()
    
    start_time = datetime.now()
    
    # Get config from env
    chunk_size = int(os.getenv('CHUNK_SIZE', 500))
    chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 50))
    embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Load documents
    print(f"📄 Step 1/4: Loading documents from {input_dir}")
    documents = load_all_documents(input_dir)
    print(f"   ✅ Loaded {len(documents)} documents")
    
    if not documents:
        print("❌ No documents found!")
        return
    
    # Step 2: Chunk documents
    print(f"\n✂️  Step 2/4: Chunking documents (size={chunk_size}, overlap={chunk_overlap})")
    chunks = chunk_all_documents(documents, chunk_size, chunk_overlap)
    print(f"   ✅ Created {len(chunks)} chunks")
    
    if not chunks:
        print("❌ No chunks created!")
        return
    
    # Step 3: Generate embeddings
    print(f"\n🧠 Step 3/4: Generating embeddings with {embedding_model}")
    embedding_generator = EmbeddingGenerator(embedding_model)
    chunks = embedding_generator.embed_chunks(chunks, batch_size=32)
    dimension = embedding_generator.get_dimension()
    print(f"   ✅ Generated embeddings (dimension={dimension})")
    
    # Save chunks with embeddings
    chunks_path = output_path / "chunks.pkl"
    save_chunks_with_embeddings(chunks, str(chunks_path))
    
    # Step 4: Build and save FAISS index
    print(f"\n🔍 Step 4/4: Building FAISS index")
    import numpy as np
    
    vector_store = FAISSVectorStore(dimension=dimension)
    embeddings = np.array([chunk['embedding'] for chunk in chunks])
    
    # Remove embeddings from chunks metadata (they're in the index)
    chunks_without_embeddings = []
    for chunk in chunks:
        chunk_copy = chunk.copy()
        del chunk_copy['embedding']
        chunks_without_embeddings.append(chunk_copy)
    
    vector_store.add_embeddings(embeddings, chunks_without_embeddings)
    
    # Save index
    index_path = output_path / "index_v1"
    vector_store.save_index(str(index_path))
    print(f"   ✅ Index saved to {index_path}.faiss")
    
    # Calculate stats
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    stats = {
        'documents_loaded': len(documents),
        'chunks_created': len(chunks),
        'embedding_dimension': dimension,
        'total_vectors': vector_store.index.ntotal,
        'duration_seconds': duration,
        'started_at': start_time.isoformat(),
        'completed_at': end_time.isoformat(),
        'index_path': str(index_path) + '.faiss'
    }
    
    # Save report
    report_path = output_path / "ingestion_report.json"
    with open(report_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print()
    print("=" * 60)
    print("✅ Pipeline Complete!")
    print("=" * 60)
    print(f"   Documents: {stats['documents_loaded']}")
    print(f"   Chunks: {stats['chunks_created']}")
    print(f"   Vectors: {stats['total_vectors']}")
    print(f"   Duration: {duration:.2f}s")
    print(f"   Index: {stats['index_path']}")
    print()


if __name__ == "__main__":
    run_pipeline()
