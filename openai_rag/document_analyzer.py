from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import concurrent
import PyPDF2
import os
import pandas as pd
import base64
from tools.api_key_manager import get_api_key
import argparse
from tools.llm_client_factory import get_llm_client
from tools.openai_rag.create_vector_store import *  # Import all functions

client = OpenAI(api_key=get_api_key('OPENAI_API_KEY'))
dir_pdfs = 'data' # have those PDFs stored locally here
pdf_files = [os.path.join(dir_pdfs, f) for f in os.listdir(dir_pdfs)]

def test_vector_db_query(query):
    """Test vector DB search with a given query"""
    try:
        search_results = client.vector_stores.search(
            vector_store_id=vector_store_details['id'],
            query=query
        )

        print("\nVector DB Search Results:")
        for result in search_results.data:
            print(f"{len(result.content[0].text)} characters of content from {result.filename} with relevance score {result.score}")
        
        # Also test the response creation
        response = client.responses.create(
            input=query,
            model="gpt-4o-mini",
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_details['id']],
            }]
        )
        
        print("\nAI Response:")
        print(f"Files used: {set([r.filename for r in response.output[1].content[0].annotations])}")
        print("Response:")
        print(response.output[1].content[0].text)
        
    except Exception as e:
        print(f"Error testing vector DB: {str(e)}")

def get_default_response(query="What's Deep Research?"):
    """Get default response using llm_client_factory"""
    
    client = get_llm_client()
    response = client.responses.create(
        input=query,
        tools=[{
            "type": "file_search", 
            "vector_store_ids": [vector_store_details['id']],
        }]
    )

    # Extract annotations from the response
    annotations = response.output[1].content[0].annotations
        
    # Get top-k retrieved filenames
    retrieved_files = set([result.filename for result in annotations])

    print(f'Files used: {retrieved_files}')
    print('Response:')
    print(response.output[1].content[0].text)




def extract_text_from_pdf(pdf_path):
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
    text = extract_text_from_pdf(pdf_path)

    prompt = (
        "Can you generate a question that can only be answered from this document?:\n"
        f"{text}\n\n"
    )

    response = client.responses.create(
        input=prompt,
        model="gpt-4o",
    )

    question = response.output[0].content[0].text

    return question


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-vectordb", action="store_true", help="Test vector DB search")
    parser.add_argument("--query", type=str, help="Query string for vector DB search")
    args = parser.parse_args()
    
    if args.test_vectordb:
        if not args.query:
            args.query = "What's Deep Research?"  # Default query
        test_vector_db_query(args.query)
    else:
        get_default_response(args.query if args.query else None)