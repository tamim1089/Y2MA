#!/usr/bin/env python3
"""
Y2MA Setup Validation Script
Checks all dependencies, connections, and requirements are met.
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version >= 3.10"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python version {version.major}.{version.minor} is too old. Need >= 3.10")
        return False


def check_dependencies():
    """Check all required packages are installed"""
    required = [
        'streamlit',
        'sentence_transformers',
        'faiss',
        'pypdf',
        'docx',
        'pandas',
        'numpy',
        'requests',
        'dotenv',
        'tiktoken'
    ]
    
    all_installed = True
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT installed")
            all_installed = False
    
    return all_installed


def check_ollama_connection():
    """Check Ollama API is reachable"""
    import requests
    from dotenv import load_dotenv
    
    load_dotenv()
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://38.39.92.215:443')
    
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            print(f"✅ Ollama connected at {base_url}")
            print(f"   Available models: {', '.join(model_names[:5])}{'...' if len(model_names) > 5 else ''}")
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama at {base_url}: {e}")
        return False


def check_embedding_model():
    """Check sentence-transformers model can be loaded"""
    try:
        from sentence_transformers import SentenceTransformer
        print("⏳ Loading embedding model (this may take a moment on first run)...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test embedding
        test_embedding = model.encode("Test sentence")
        print(f"✅ Embedding model loaded (dimension: {len(test_embedding)})")
        return True
    except Exception as e:
        print(f"❌ Cannot load embedding model: {e}")
        return False


def check_directories():
    """Check all required directories exist and are writable"""
    base_path = Path(__file__).parent
    required_dirs = [
        'data/raw',
        'data/processed',
        'data/embeddings',
        'logs',
        'src',
        'prompts'
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            # Check writable
            test_file = dir_path / '.write_test'
            try:
                test_file.touch()
                test_file.unlink()
                print(f"✅ {dir_name}/ exists and writable")
            except Exception:
                print(f"❌ {dir_name}/ exists but NOT writable")
                all_ok = False
        else:
            print(f"❌ {dir_name}/ does NOT exist")
            all_ok = False
    
    return all_ok


def check_env_file():
    """Check .env file exists and has required variables"""
    from dotenv import load_dotenv
    
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    load_dotenv()
    
    required_vars = ['OLLAMA_BASE_URL', 'OLLAMA_MODEL', 'EMBEDDING_MODEL']
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} = {value}")
        else:
            print(f"❌ {var} not set in .env")
            all_present = False
    
    return all_present


def main():
    print("=" * 60)
    print("🚀 Y2MA Setup Validation")
    print("=" * 60)
    print()
    
    results = {}
    
    print("📋 Checking Python version...")
    results['python'] = check_python_version()
    print()
    
    print("📋 Checking environment file...")
    results['env'] = check_env_file()
    print()
    
    print("📋 Checking directories...")
    results['dirs'] = check_directories()
    print()
    
    print("📋 Checking dependencies...")
    results['deps'] = check_dependencies()
    print()
    
    print("📋 Checking Ollama connection...")
    results['ollama'] = check_ollama_connection()
    print()
    
    print("📋 Checking embedding model...")
    results['embeddings'] = check_embedding_model()
    print()
    
    print("=" * 60)
    all_passed = all(results.values())
    
    if all_passed:
        print("✅ ALL CHECKS PASSED - Y2MA is ready to run!")
        print()
        print("Next steps:")
        print("  1. Generate sample documents: python data/generate_sample_docs.py")
        print("  2. Process documents: python data/process_documents.py")
        print("  3. Start the app: streamlit run app.py")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please fix the issues above")
        failed = [k for k, v in results.items() if not v]
        print(f"   Failed checks: {', '.join(failed)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
