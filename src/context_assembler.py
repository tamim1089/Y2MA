"""
Context Assembler Module
Formats retrieved chunks into context for the LLM prompt
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def assemble_context(
    chunks: List[Dict],
    max_tokens: int = 3000,
    include_scores: bool = False
) -> str:
    """
    Assemble retrieved chunks into formatted context for LLM.
    
    Args:
        chunks: List of retrieved chunk dictionaries
        max_tokens: Maximum tokens for context (approximate)
        include_scores: Whether to include relevance scores
    
    Returns:
        Formatted context string
    """
    if not chunks:
        return ""
    
    context_parts = []
    current_tokens = 0
    
    for i, chunk in enumerate(chunks):
        # Get chunk data
        filename = chunk.get('filename', 'unknown')
        text = chunk.get('text', '')
        score = chunk.get('combined_score', chunk.get('score', 0))
        doc_type = chunk.get('metadata', {}).get('document_type', 'general')
        
        # Format the chunk
        if include_scores:
            header = f"[Source: {filename} | Type: {doc_type} | Relevance: {score:.2f}]"
        else:
            header = f"[Source: {filename}]"
        
        formatted_chunk = f"{header}\n{text.strip()}"
        
        # Estimate tokens (rough: 4 chars per token)
        chunk_tokens = len(formatted_chunk) // 4
        
        # Check if we'd exceed the limit
        if current_tokens + chunk_tokens > max_tokens:
            # Add partial if there's room
            remaining_tokens = max_tokens - current_tokens
            if remaining_tokens > 100:  # Only add if meaningful space left
                # Truncate text
                chars_left = remaining_tokens * 4
                truncated = formatted_chunk[:chars_left] + "..."
                context_parts.append(truncated)
            break
        
        context_parts.append(formatted_chunk)
        current_tokens += chunk_tokens
    
    # Join with separators
    context = "\n\n---\n\n".join(context_parts)
    
    logger.info(f"Assembled context: {len(chunks)} chunks, ~{current_tokens} tokens")
    
    return context


def extract_sources(chunks: List[Dict]) -> List[Dict]:
    """
    Extract source information from chunks for citation display.
    
    Args:
        chunks: List of retrieved chunk dictionaries
    
    Returns:
        List of source dictionaries
    """
    sources = []
    
    for chunk in chunks:
        source = {
            'filename': chunk.get('filename', 'unknown'),
            'document_type': chunk.get('metadata', {}).get('document_type', 'general'),
            'text': chunk.get('text', '')[:300],  # Preview only
            'score': chunk.get('combined_score', chunk.get('score', 0))
        }
        sources.append(source)
    
    return sources


def format_sources_markdown(sources: List[Dict]) -> str:
    """
    Format sources as markdown for display.
    
    Args:
        sources: List of source dictionaries
    
    Returns:
        Markdown formatted string
    """
    if not sources:
        return "*No sources found*"
    
    lines = ["### Sources\n"]
    
    for i, source in enumerate(sources, 1):
        lines.append(f"**{i}. {source['filename']}** (relevance: {source['score']:.1%})")
        lines.append(f"> {source['text'][:150]}...")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test the context assembler
    logging.basicConfig(level=logging.INFO)
    
    test_chunks = [
        {
            'chunk_id': 'test_1',
            'filename': 'benefits_guide.txt',
            'text': 'Space42 offers comprehensive health insurance covering medical, dental, and vision. Annual leave is 30 days per year.',
            'combined_score': 0.85,
            'metadata': {'document_type': 'benefits'}
        },
        {
            'chunk_id': 'test_2',
            'filename': 'policies.txt',
            'text': 'Remote work is allowed up to 3 days per week. Core hours are 9 AM to 3 PM UAE time.',
            'combined_score': 0.72,
            'metadata': {'document_type': 'policies'}
        }
    ]
    
    print("Testing Context Assembler...")
    print()
    
    context = assemble_context(test_chunks, include_scores=True)
    print("Assembled Context:")
    print("-" * 40)
    print(context)
    print("-" * 40)
    print()
    
    sources = extract_sources(test_chunks)
    print("Extracted Sources:")
    for s in sources:
        print(f"  - {s['filename']}: {s['score']:.2f}")
    print()
    
    markdown = format_sources_markdown(sources)
    print("Markdown Sources:")
    print(markdown)
    
    print("\n✅ Context assembler test passed!")
