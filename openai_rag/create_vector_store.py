import os
import concurrent.futures
from tqdm import tqdm
import argparse
from openai import OpenAI
from tools.api_key_manager import get_api_key

client = OpenAI(api_key=get_api_key('OPENAI_API_KEY'))
dir_pdfs = 'data'  # have those PDFs stored locally here

def upload_single_pdf(file_path: str, vector_store_id: str):
    file_name = os.path.basename(file_path)
    try:
        file_response = client.files.create(file=open(file_path, 'rb'), purpose="assistants")
        attach_response = client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_response.id
        )
        return {"file": file_name, "status": "success"}
    except Exception as e:
        print(f"Error with {file_name}: {str(e)}")
        return {"file": file_name, "status": "failed", "error": str(e)}

def upload_pdf_files_to_vector_store(vector_store_id: str):
    pdf_files = [os.path.join(dir_pdfs, f) for f in os.listdir(dir_pdfs)]
    stats = {"total_files": len(pdf_files), "successful_uploads": 0, "failed_uploads": 0, "errors": []}
    
    print(f"{len(pdf_files)} PDF files to process. Uploading in parallel...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(upload_single_pdf, file_path, vector_store_id): file_path for file_path in pdf_files}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(pdf_files)):
            result = future.result()
            if result["status"] == "success":
                stats["successful_uploads"] += 1
            else:
                stats["failed_uploads"] += 1
                stats["errors"].append(result)

    return stats

def create_vector_store(store_name: str) -> dict:
    try:
        vector_store = client.vector_stores.create(name=store_name)
        details = {
            "id": vector_store.id,
            "name": vector_store.name,
            "created_at": vector_store.created_at,
            "file_count": vector_store.file_counts.completed
        }
        print("Vector store created:", details)
        return details
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return {}

def main(store_name=None):
    if not store_name:
        store_name = input("Enter name for the vector store (default: pdf_document_store): ").strip()
        if not store_name:
            store_name = "pdf_document_store"
    
    print(f"Creating vector store with name: {store_name}")
    vector_store_details = create_vector_store(store_name)
    
    if vector_store_details:
        upload_pdf_files_to_vector_store(vector_store_details["id"])
    return vector_store_details

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create and populate a vector store with PDF files")
    parser.add_argument("--store-name", type=str, help="Name for the vector store")
    args = parser.parse_args()
    
    vector_store_details = main(args.store_name)