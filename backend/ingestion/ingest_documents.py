import os
import sys

# Add backend directory to path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.rag.loaders import load_documents_from_dir, get_text_splitter
from app.rag.vectorstore import add_documents_to_db

def run_ingestion():
    # Use the absolute path for data folder
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
    
    print(f"Loading documents from {base_dir}...")
    documents = load_documents_from_dir(base_dir)
    
    if not documents:
        print("No documents found to ingest.")
        return
        
    print(f"Loaded {len(documents)} documents.")
    
    splitter = get_text_splitter()
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    
    add_documents_to_db(chunks)
    print("Successfully ingested documents into VectorDB.")

if __name__ == "__main__":
    run_ingestion()
