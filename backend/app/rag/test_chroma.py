import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.rag.vectorstore import query_collection, COLLECTION_NAME
from app.config import settings

def run_test():
    print("==========================================")
    print("CHROMADB INDEPENDENT RETRIEVAL TEST")
    print("==========================================")
    print(f"Chroma DB Path: {settings.vector_db_url}")
    print(f"Collection Name: {COLLECTION_NAME}")

    test_queries = [
        "What is the SETTribe phone number and email address?",
        "Tell me about the Data Analyst course."
    ]

    for query in test_queries:
        print("\n" + "=" * 60)
        print(f"QUERY: '{query}'")
        print("=" * 60)

        # Query collection with n_results=5
        res = query_collection([query], n_results=5)

        docs = res.get("documents", [[]])[0]
        metadatas = res.get("metadatas", [[]])[0]
        distances = res.get("distances", [[]])[0]

        if not docs:
            print("No documents retrieved from Chroma collection!")
            continue

        for i, (doc, meta, dist) in enumerate(zip(docs, metadatas, distances), 1):
            source = meta.get("source", "Unknown") if meta else "Unknown"
            category = meta.get("category", "Unknown") if meta else "Unknown"
            print(f"\n[Rank {i}]")
            print(f"  Source: {source}")
            print(f"  Category: {category}")
            print(f"  Similarity Distance: {dist:.4f}")
            print(f"  Content snippet: {doc[:160].strip().replace('\n', ' ')}...")

if __name__ == "__main__":
    run_test()
