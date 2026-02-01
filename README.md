# Y2MA - Space42 AI Career Assistant

🚀 **Y2MA** is a 100% free, locally-running RAG-based AI assistant designed for Space42's candidate experience and onboarding.

## Features

- **RAG-Powered Q&A**: Retrieval-Augmented Generation for accurate, sourced answers
- **Hybrid Search**: Combines dense vector search with keyword matching
- **Security First**: Input validation, prompt injection detection, rate limiting
- **Source Citations**: Every answer includes verifiable source citations
- **Chat Interface**: Modern Streamlit UI with conversation history
- **100% Local**: No API keys, no cloud services, fully self-contained

## Quick Start

```bash
# One-command setup
chmod +x setup.sh
./setup.sh

# Start the application
source venv/bin/activate
streamlit run app.py
```

## Requirements

- Python 3.10+
- Access to Ollama endpoint (configured in `.env`)
- 4GB+ RAM for embeddings model

## Project Structure

```
Y2MA/
├── app.py                  # Main Streamlit application
├── setup.sh                # One-command setup script
├── setup_check.py          # Environment validation
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (Ollama, etc.)
├── data/
│   ├── raw/               # Source documents
│   ├── embeddings/        # FAISS index & chunks
│   ├── generate_sample_docs.py
│   └── process_documents.py
├── src/
│   ├── document_loader.py  # Load PDF, DOCX, TXT
│   ├── chunker.py          # Semantic chunking
│   ├── embeddings.py       # Sentence transformers
│   ├── vector_store.py     # FAISS index
│   ├── ingestion_pipeline.py
│   ├── retrieval.py        # Hybrid search
│   ├── context_assembler.py
│   ├── llm_provider.py     # Ollama integration
│   ├── security.py         # Input validation
│   ├── rag_engine.py       # Core orchestrator
│   └── monitoring.py       # Logging & metrics
├── prompts/
│   └── system_prompt.txt   # Y2MA persona
└── logs/                   # Application logs
```

## Configuration

Edit `.env` to configure:

```bash
OLLAMA_BASE_URL=http://38.39.92.215:443
OLLAMA_MODEL=llama3.1:8b-instruct-fp16
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

## What Y2MA Can Do

- **Job Information**: Roles, requirements, salary ranges
- **Interview Process**: Steps, tips, preparation guides
- **Benefits & Compensation**: Health, PTO, perks
- **Onboarding**: First day, equipment, training
- **Company Culture**: Values, mission, work environment
- **HR Policies**: Remote work, leave, guidelines

## Security Features

- Prompt injection detection (regex patterns)
- Rate limiting (10 requests/minute)
- PII detection and redaction
- Input sanitization
- Off-topic query filtering

## License

Internal use only - Space42

## Support

Contact HR at hr@space42.ai
