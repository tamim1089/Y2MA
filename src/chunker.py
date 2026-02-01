"""
Semantic Chunker Module
Splits documents into semantically meaningful chunks for embedding
"""

import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def count_tokens(text: str) -> int:
    """
    Approximate token count using character-based estimation.
    More accurate than word count for most tokenizers.
    Roughly 1 token = 4 characters for English text.
    """
    return len(text) // 4


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences while preserving structure"""
    # Simple sentence splitting - split on sentence-ending punctuation followed by space
    # This is more compatible with Python 3.12
    
    # First split on double newlines (paragraphs)
    paragraphs = re.split(r'\n\n+', text)
    
    sentences = []
    for para in paragraphs:
        if not para.strip():
            continue
        
        # Split sentences: look for . ! ? followed by space or end
        # Simple approach that works with Python 3.12
        parts = re.split(r'([.!?])\s+', para)
        
        # Recombine sentence with its punctuation
        current = ""
        for i, part in enumerate(parts):
            if part in '.!?':
                current += part
                if current.strip():
                    sentences.append(current.strip())
                current = ""
            else:
                current += part
        
        # Don't forget the last part
        if current.strip():
            sentences.append(current.strip())
    
    return sentences


def create_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    metadata: Dict = None
) -> List[Dict]:
    """
    Create overlapping chunks from text.
    Preserves sentence boundaries - doesn't split mid-sentence.
    
    Args:
        text: The document text to chunk
        chunk_size: Target chunk size in tokens
        chunk_overlap: Overlap between chunks in tokens
        metadata: Document metadata to include in each chunk
    
    Returns:
        List of chunk dictionaries with text, metadata, and indices
    """
    if metadata is None:
        metadata = {}
    
    sentences = split_into_sentences(text)
    
    if not sentences:
        logger.warning("No sentences found in text")
        return []
    
    chunks = []
    current_chunk_sentences = []
    current_chunk_tokens = 0
    chunk_index = 0
    
    doc_id = metadata.get('filename', 'unknown').replace('.', '_')
    
    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        sentence_tokens = count_tokens(sentence)
        
        # If single sentence is larger than chunk size, we must include it
        if sentence_tokens > chunk_size:
            # If we have accumulated sentences, save them first
            if current_chunk_sentences:
                chunk_text = ' '.join(current_chunk_sentences)
                chunks.append({
                    'chunk_id': f"{doc_id}_chunk_{chunk_index}",
                    'text': chunk_text,
                    'token_count': count_tokens(chunk_text),
                    'chunk_index': chunk_index,
                    'metadata': metadata.copy()
                })
                chunk_index += 1
                current_chunk_sentences = []
                current_chunk_tokens = 0
            
            # Add the large sentence as its own chunk
            chunks.append({
                'chunk_id': f"{doc_id}_chunk_{chunk_index}",
                'text': sentence,
                'token_count': sentence_tokens,
                'chunk_index': chunk_index,
                'metadata': metadata.copy()
            })
            chunk_index += 1
            i += 1
            continue
        
        # Check if adding this sentence would exceed chunk size
        if current_chunk_tokens + sentence_tokens > chunk_size and current_chunk_sentences:
            # Save current chunk
            chunk_text = ' '.join(current_chunk_sentences)
            chunks.append({
                'chunk_id': f"{doc_id}_chunk_{chunk_index}",
                'text': chunk_text,
                'token_count': count_tokens(chunk_text),
                'chunk_index': chunk_index,
                'metadata': metadata.copy()
            })
            chunk_index += 1
            
            # Calculate overlap - keep sentences from end of current chunk
            overlap_sentences = []
            overlap_tokens = 0
            
            for sent in reversed(current_chunk_sentences):
                sent_tokens = count_tokens(sent)
                if overlap_tokens + sent_tokens <= chunk_overlap:
                    overlap_sentences.insert(0, sent)
                    overlap_tokens += sent_tokens
                else:
                    break
            
            current_chunk_sentences = overlap_sentences
            current_chunk_tokens = overlap_tokens
        
        # Add sentence to current chunk
        current_chunk_sentences.append(sentence)
        current_chunk_tokens += sentence_tokens
        i += 1
    
    # Don't forget the last chunk
    if current_chunk_sentences:
        chunk_text = ' '.join(current_chunk_sentences)
        chunks.append({
            'chunk_id': f"{doc_id}_chunk_{chunk_index}",
            'text': chunk_text,
            'token_count': count_tokens(chunk_text),
            'chunk_index': chunk_index,
            'metadata': metadata.copy()
        })
    
    logger.info(f"Created {len(chunks)} chunks from document")
    return chunks


def chunk_document(document: Dict, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
    """
    Chunk a document (as returned by document_loader).
    
    Args:
        document: Dict with 'text' and 'metadata' keys
        chunk_size: Target chunk size in tokens
        chunk_overlap: Overlap between chunks in tokens
    
    Returns:
        List of chunk dictionaries
    """
    text = document.get('text', '')
    metadata = document.get('metadata', {})
    
    if not text:
        logger.warning(f"Empty text in document: {metadata.get('filename', 'unknown')}")
        return []
    
    return create_chunks(text, chunk_size, chunk_overlap, metadata)


def chunk_all_documents(
    documents: List[Dict],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Dict]:
    """
    Chunk multiple documents.
    
    Args:
        documents: List of document dicts from document_loader
        chunk_size: Target chunk size in tokens
        chunk_overlap: Overlap between chunks in tokens
    
    Returns:
        List of all chunks across all documents
    """
    all_chunks = []
    
    for doc in documents:
        chunks = chunk_document(doc, chunk_size, chunk_overlap)
        all_chunks.extend(chunks)
    
    logger.info(f"Created {len(all_chunks)} total chunks from {len(documents)} documents")
    return all_chunks


if __name__ == "__main__":
    # Test the chunker
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    test_text = """
    This is the first sentence of the document. It contains some important information.
    
    Here is the second paragraph with more details. We want to make sure that chunking
    works correctly and preserves sentence boundaries. This is a longer sentence that
    adds more content to the document.
    
    The third paragraph discusses a different topic. Each paragraph should be handled
    appropriately by the chunker. We need to ensure overlapping works correctly.
    """
    
    test_doc = {
        'text': test_text,
        'metadata': {'filename': 'test.txt', 'document_type': 'general'}
    }
    
    chunks = chunk_document(test_doc, chunk_size=100, chunk_overlap=20)
    
    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  - {chunk['chunk_id']}: {chunk['token_count']} tokens")
        print(f"    Text preview: {chunk['text'][:80]}...")
        print()
