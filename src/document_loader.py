"""
Document Loader Module
Handles loading documents from various formats (txt, pdf, docx)
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


def load_txt(filepath: str) -> str:
    """Load text from a .txt file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def load_pdf(filepath: str) -> str:
    """Load text from a PDF file using pypdf"""
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(filepath)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return '\n\n'.join(text_parts)
    except Exception as e:
        logger.error(f"Error loading PDF {filepath}: {e}")
        return ""


def load_docx(filepath: str) -> str:
    """Load text from a .docx file using python-docx"""
    try:
        from docx import Document
        
        doc = Document(filepath)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        return '\n\n'.join(text_parts)
    except Exception as e:
        logger.error(f"Error loading DOCX {filepath}: {e}")
        return ""


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Normalize unicode
    import unicodedata
    text = unicodedata.normalize('NFKC', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\t+', ' ', text)
    
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove any remaining leading/trailing whitespace
    text = text.strip()
    
    return text


def compute_checksum(text: str) -> str:
    """Compute MD5 checksum of text content"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def extract_metadata(filepath: str) -> Dict:
    """Extract metadata from a file"""
    path = Path(filepath)
    stat = path.stat()
    
    # Determine document type from filename
    filename_lower = path.stem.lower()
    if 'job_description' in filename_lower or 'jd_' in filename_lower:
        doc_type = 'job_description'
    elif 'overview' in filename_lower or 'about' in filename_lower:
        doc_type = 'overview'
    elif 'interview' in filename_lower:
        doc_type = 'interview_process'
    elif 'onboarding' in filename_lower:
        doc_type = 'onboarding'
    elif 'benefit' in filename_lower:
        doc_type = 'benefits'
    elif 'culture' in filename_lower or 'value' in filename_lower:
        doc_type = 'culture'
    elif 'faq' in filename_lower:
        doc_type = 'faq'
    elif 'polic' in filename_lower:
        doc_type = 'policies'
    elif 'career' in filename_lower:
        doc_type = 'career'
    else:
        doc_type = 'general'
    
    return {
        'filename': path.name,
        'filepath': str(path.absolute()),
        'extension': path.suffix.lower(),
        'file_size': stat.st_size,
        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'document_type': doc_type
    }


def load_document(filepath: str) -> Optional[Dict]:
    """Load a single document and return text with metadata"""
    path = Path(filepath)
    
    if not path.exists():
        logger.error(f"File not found: {filepath}")
        return None
    
    extension = path.suffix.lower()
    
    # Load based on file type
    if extension == '.txt':
        text = load_txt(filepath)
    elif extension == '.pdf':
        text = load_pdf(filepath)
    elif extension in ['.docx', '.doc']:
        text = load_docx(filepath)
    else:
        logger.warning(f"Unsupported file type: {extension}")
        return None
    
    if not text:
        logger.warning(f"No text extracted from: {filepath}")
        return None
    
    # Clean the text
    text = clean_text(text)
    
    # Get metadata
    metadata = extract_metadata(filepath)
    metadata['checksum'] = compute_checksum(text)
    metadata['char_count'] = len(text)
    metadata['estimated_tokens'] = len(text) // 4
    
    return {
        'text': text,
        'metadata': metadata
    }


def load_all_documents(directory: str, extensions: List[str] = None) -> List[Dict]:
    """Load all documents from a directory"""
    if extensions is None:
        extensions = ['.txt', '.pdf', '.docx']
    
    dir_path = Path(directory)
    
    if not dir_path.exists():
        logger.error(f"Directory not found: {directory}")
        return []
    
    documents = []
    
    # Find all matching files
    for ext in extensions:
        for filepath in dir_path.glob(f'*{ext}'):
            if filepath.name.startswith('.'):
                continue
            if filepath.name == 'metadata.json':
                continue
                
            logger.info(f"Loading: {filepath.name}")
            doc = load_document(str(filepath))
            
            if doc:
                documents.append(doc)
    
    logger.info(f"Loaded {len(documents)} documents from {directory}")
    return documents


if __name__ == "__main__":
    # Test the document loader
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        test_dir = sys.argv[1]
    else:
        test_dir = "data/raw"
    
    print(f"Testing document loader on: {test_dir}")
    docs = load_all_documents(test_dir)
    
    for doc in docs:
        meta = doc['metadata']
        print(f"  - {meta['filename']}: {meta['char_count']:,} chars ({meta['document_type']})")
