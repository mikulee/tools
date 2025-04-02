import os
import argparse
import PyPDF2
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Import our custom libraries
from tools.llm_client_factory import get_llm_client
from tools.api_key_manager import get_api_key
from tools.openai_rag.create_vector_store import main as create_vector_store_main

# Constants
DIR_PDFS = 'data'  # Directory containing PDF files

def print_help():
    """Display detailed usage instructions and examples"""
    help_text = """
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
"""
    print(help_text)

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file"""
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def generate_questions(pdf_path):
    """Generate questions based on PDF content using LLM"""
    text = extract_text_from_pdf(pdf_path)
    client = get_llm_client()  # Use factory to get appropriate client

    prompt = (
        "Can you generate a question that can only be answered from this document?:\n"
        f"{text}\n\n"
    )

    response = client.chat_completion(prompt)
    return response

def test_vector_db_query(query, vector_store_details):
    """Test vector DB search with a given query"""
    client = get_llm_client()  # Use factory to get appropriate client
    
    try:
        search_results = client.vector_search(
            vector_store_id=vector_store_details['id'],
            query=query
        )

        print("\nVector DB Search Results:")
        for result in search_results.data:
            print(f"{len(result.content[0].text)} characters of content from {result.filename} with relevance score {result.score}")
        
        # Also test the response creation
        response = client.rag_response(
            query=query,
            vector_store_id=vector_store_details['id']
        )
        
        print("\nAI Response:")
        print(f"Files used: {client.get_reference_files(response)}")
        print("Response:")
        print(client.get_response_text(response))
        
    except Exception as e:
        print(f"Error testing vector DB: {str(e)}")

def get_default_response(query="What's Deep Research?", vector_store_details=None):
    """Get default response using llm_client_factory"""
    if not vector_store_details:
        print("Error: Vector store details not provided")
        return
        
    client = get_llm_client()
    response = client.rag_response(
        query=query,
        vector_store_id=vector_store_details['id']
    )

    # Get reference files and response text using client methods
    retrieved_files = client.get_reference_files(response)

    print(f'Files used: {retrieved_files}')
    print('Response:')
    print(client.get_response_text(response))

def main():
    """Main function to handle command line arguments and execute appropriate functionality"""
    parser = argparse.ArgumentParser(description="PDF Document Analysis and Vector DB Query Tool")
    parser.add_argument("--test-vectordb", action="store_true", help="Test vector DB search")
    parser.add_argument("--query", type=str, help="Query string for vector DB search")
    parser.add_argument("--create-store", action="store_true", help="Create a new vector store")
    parser.add_argument("--store-name", type=str, help="Name for the vector store")
    parser.add_argument("--model", type=str, help="Model to use (openai or lmstudio)")
    parser.add_argument("--help-extended", action="store_true", help="Show extended help with examples")
    
    args = parser.parse_args()
    
    # Show extended help if requested
    if args.help_extended:
        print_help()
        return
    
    # Set model preference if specified
    if args.model:
        os.environ["LLM_PROVIDER"] = args.model
    
    # Create vector store if requested
    vector_store_details = None
    if args.create_store:
        vector_store_details = create_vector_store_main(args.store_name)
    else:
        # This is a placeholder. In a production application, you would
        # fetch or retrieve the existing vector store details
        # For now, assuming it's created and using default name
        vector_store_details = {"id": "your_vector_store_id"}  # Replace with actual ID
    
    # Process query operations
    if args.test_vectordb:
        if not args.query:
            args.query = "What's Deep Research?"  # Default query
        test_vector_db_query(args.query, vector_store_details)
    else:
        get_default_response(args.query if args.query else None, vector_store_details)

if __name__ == "__main__":
    main()