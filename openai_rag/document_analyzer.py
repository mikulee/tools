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
    
    args = parser.parse_args()
    
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