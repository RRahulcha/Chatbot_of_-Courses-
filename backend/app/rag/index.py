import sys
from pathlib import Path

# Ensure backend directory is in sys.path when run directly
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.rag.vectorstore import build_vector_store

def main():
    print("Starting SETTribe Knowledge Base Ingestion...")
    build_vector_store()
    print("Ingestion complete!")

if __name__ == "__main__":
    main()
