#!/bin/bash
# Y2MA One-Command Setup Script
# This script sets up the entire Y2MA environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          🚀 Y2MA Setup - Space42 AI Assistant             ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Store the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}📁 Project root: ${PROJECT_ROOT}${NC}"
echo ""

# Function to check if command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is required but not installed.${NC}"
        exit 1
    fi
}

# Step 1: Check Python version
echo -e "${BLUE}[1/7]${NC} Checking Python version..."
check_command python3

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}❌ Python 3.10+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Step 2: Create virtual environment
echo ""
echo -e "${BLUE}[2/7]${NC} Setting up virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Step 3: Install dependencies
echo ""
echo -e "${BLUE}[3/7]${NC} Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 4: Verify directories exist
echo ""
echo -e "${BLUE}[4/7]${NC} Verifying directory structure..."

mkdir -p data/raw
mkdir -p data/embeddings
mkdir -p logs
mkdir -p prompts

echo -e "${GREEN}✅ Directories verified${NC}"

# Step 5: Generate sample documents
echo ""
echo -e "${BLUE}[5/7]${NC} Generating sample documents..."

python data/generate_sample_docs.py

# Check if raw documents exist
RAW_FILES=$(ls -1 data/raw/*.txt 2>/dev/null | wc -l)
if [ "$RAW_FILES" -gt 0 ]; then
    echo -e "${GREEN}✅ Generated $RAW_FILES documents${NC}"
else
    echo -e "${RED}❌ No documents generated${NC}"
    exit 1
fi

# Step 6: Process documents and build index
echo ""
echo -e "${BLUE}[6/7]${NC} Processing documents and building vector index..."

python data/process_documents.py

# Check if index was created
if [ -f "data/embeddings/index_v1.faiss" ]; then
    echo -e "${GREEN}✅ Vector index built${NC}"
else
    echo -e "${RED}❌ Index creation failed${NC}"
    exit 1
fi

# Step 7: Initialize database
echo ""
echo -e "${BLUE}[7/7]${NC} Initializing database..."

python src/init_db.py

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  🎉 Setup Complete!                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "To start Y2MA, run:"
echo ""
echo -e "  ${BLUE}source venv/bin/activate${NC}"
echo -e "  ${BLUE}streamlit run app.py${NC}"
echo ""
echo -e "Or run both commands at once:"
echo ""
echo -e "  ${BLUE}source venv/bin/activate && streamlit run app.py${NC}"
echo ""
echo -e "${YELLOW}📌 Note: Make sure Ollama is accessible at the configured endpoint.${NC}"
echo ""
