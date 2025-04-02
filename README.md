# Tools Collection

A comprehensive collection of productivity and development tools focusing on LLM integration, API management, and document analysis.

## Table of Contents

- [Installation](#installation)
- [API Key Management](#api-key-management)
- [Document Analysis](#document-analysis)
- [Vector Store Creation](#vector-store-creation)
- [LLM Client Factory](#llm-client-factory)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tools.git
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure API keys (see [API Key Management](#api-key-management) for details)

## API Key Management

The `api_key_manager.py` module provides secure access to API keys through environment variables or 1Password integration.

### Usage

```python
from tools.api_key_manager import get_api_key

# Get API key from environment variables or 1Password
openai_key = get_api_key('OPENAI_API_KEY')
```

### Configuration Options

#### Option A: Environment Variables (.env file)
1. Create a `.env` file in the root directory
2. Add your API keys:
   ```
   OPENAI_API_KEY=your_key_here
   LMSTUDIO_API_KEY=your_key_here
   ```

#### Option B: 1Password Integration
1. Install 1Password CLI from https://developer.1password.com/docs/cli/get-started/
2. Configure 1Password CLI with `op signin`
3. Store your API keys in 1Password with the following structure:
   - Item Category: API Credential
   - Fields: OPENAI_API_KEY, LMSTUDIO_API_KEY

## Document Analysis

The `openai_rag/document_analyzer.py` tool helps analyze PDF documents, create vector stores, and perform semantic searches using natural language queries.

### Features

- Extract text from PDF documents
- Create vector stores from document content
- Perform semantic searches using advanced LLM models
- Support for multiple LLM providers (OpenAI, LMStudio)

### Usage

```bash
# Create a vector store
python document_analyzer.py --create-store --store-name "my_documents"

# Query the vector store
python document_analyzer.py --query "What information is in these documents?"

# Test vector DB search with specific model
python document_analyzer.py --test-vectordb --query "Explain the methodology" --model openai
```

### Help Documentation

```
Document Analyzer - PDF Analysis and Vector DB Query Tool
=========================================================

DESCRIPTION
-----------
This tool helps you analyze PDF documents, create vector stores from them, 
and perform semantic searches using natural language queries.

INSTALLATION
------------
1. Clone the repository:
   git clone https://github.com/yourusername/tools.git
   
2. Install required dependencies:
   pip install -r requirements.txt
   
3. Configure API keys:
   - Option A: Create a .env file in the root directory
     Add your API keys in the format:
     OPENAI_API_KEY=your_key_here
     LMSTUDIO_API_KEY=your_key_here
     
   - Option B: 1Password integration
     a. Install 1Password CLI: https://developer.1password.com/docs/cli/get-started/
     b. Configure 1Password CLI with 'op signin'
     c. Store your API keys in 1Password with the following item structure:
        - Item Category: API Credential
        - Add fields with exact names: OPENAI_API_KEY, LMSTUDIO_API_KEY
     d. No .env file needed when using 1Password integration

PREREQUISITES
------------
1. Place your PDF documents in the './data' folder
2. Ensure you have configured your API keys (see tools/api_key_manager.py)

BASIC USAGE
-----------
1. Create a vector store with your documents:
   python document_analyzer.py --create-store --store-name "my_documents"

2. Query the vector store with a question:
   python document_analyzer.py --query "What information is in these documents?"

3. Test vector DB search specifically:
   python document_analyzer.py --test-vectordb --query "Find specific information about X"

4. Specify which model provider to use:
   python document_analyzer.py --model openai --query "My question"
   python document_analyzer.py --model lmstudio --query "My question"

EXAMPLES
--------
Example 1: Create a new vector store named "research_papers"
   python document_analyzer.py --create-store --store-name "research_papers"

Example 2: Query the vector store about a specific topic
   python document_analyzer.py --query "What are the key findings about climate change?"

Example 3: Test vector search with detailed results using OpenAI
   python document_analyzer.py --test-vectordb --query "Explain the methodology" --model openai

ADDITIONAL NOTES
---------------
- Vector store IDs are returned when creating a store and should be saved for future use
- Default query if none provided: "What's Deep Research?"
- When no store ID is provided, a placeholder ID is used (replace in production)
- For 1Password integration issues, run 'op signin' and verify your session is active
```

## Vector Store Creation

The `openai_rag/create_vector_store.py` module provides functionality for creating vector stores from PDF documents.

### Features

- Create named vector stores on OpenAI platform
- Upload PDF files in parallel with progress tracking
- Integrate with existing document analysis workflow

### Usage

```python
from tools.openai_rag.create_vector_store import main as create_vector_store

# Create a vector store with the name "research_papers"
vector_store_details = create_vector_store("research_papers")
```

Or run directly:

```bash
python create_vector_store.py --store-name "research_papers"
```

## LLM Client Factory

The `llm_client_factory.py` module provides a factory pattern for abstracting LLM provider interactions.

### Features

- Unified interface for multiple LLM providers (OpenAI, LMStudio)
- Environment-based provider selection
- Simplified client instantiation with proper API key management

### Usage

```python
from tools.llm_client_factory import get_llm_client

# Get the appropriate LLM client based on environment configuration
client = get_llm_client()

# Use the client with a unified API
response = client.chat_completion("What is the capital of France?")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
