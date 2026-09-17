import chromadb
from langchain_chroma import Chroma

from app.core.embeddings import get_embeddings
from app.config import settings
from app.rag.web_scraper import load_website_documents


# ============================================================
# CONFIGURATION
# ============================================================

COLLECTION_NAME = "settribe_docs"


# ============================================================
# CHROMADB CLIENT
# ============================================================

def get_chroma_client():
    """
    Return the persistent ChromaDB client.
    """
    return chromadb.PersistentClient(
        path=settings.vector_db_url
    )


def get_chroma_collection(name=COLLECTION_NAME):
    """
    Return the existing Chroma collection.
    """
    client = get_chroma_client()

    return client.get_or_create_collection(
        name=name
    )


# ============================================================
# DIRECT CHROMA QUERY HELPER
# ============================================================

def query_collection(
    query_texts,
    n_results=5,
    collection_name=COLLECTION_NAME
):
    """
    Direct ChromaDB query helper.

    This is useful for debugging the database directly.
    """
    client = get_chroma_client()

    collection = client.get_collection(
        name=collection_name
    )

    return collection.query(
        query_texts=query_texts,
        n_results=n_results,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )


# ============================================================
# VECTOR STORE
# ============================================================

def get_vector_store():
    """
    Connect to the existing Chroma vector database.

    IMPORTANT:
    This function ONLY connects to Chroma.

    It does NOT perform similarity_search().
    Retrieval is handled by retriever.py.

    The same local HuggingFace embedding model used during
    indexing must also be used during querying.
    """

    embeddings = get_embeddings()

    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=settings.vector_db_url,
    )

    return db


# ============================================================
# LOAD WEBSITE KNOWLEDGE
# ============================================================

def load_documents():
    """
    Load documents from the official SETTribe and STEP websites.
    """

    print("\n===================================")
    print("LOADING SETTRIBE WEBSITE KNOWLEDGE BASE")
    print("===================================\n")

    documents = load_website_documents()

    if not documents:
        raise ValueError(
            "No website documents were loaded. "
            "Check SETTribe and STEP URLs in your .env file."
        )

    print(
        f"\nSuccessfully loaded "
        f"{len(documents)} website chunks."
    )

    return documents


# ============================================================
# BUILD VECTOR STORE
# ============================================================

def build_vector_store():
    """
    Rebuild the Chroma database from the official websites.
    """

    print("\n==============================")
    print("BUILDING SETTRIBE WEBSITE VECTOR STORE")
    print("==============================\n")

    documents = load_documents()

    if not documents:
        raise ValueError(
            "No website documents available for indexing."
        )

    print(
        f"Documents/chunks ready for indexing: "
        f"{len(documents)}"
    )

    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    embeddings = get_embeddings()

    embedding_model_name = getattr(
        embeddings,
        "model_name",
        getattr(
            embeddings,
            "model",
            type(embeddings).__name__
        )
    )

    print(
        f"Embedding model: "
        f"{embedding_model_name}"
    )

    # --------------------------------------------------------
    # Remove old collection
    # --------------------------------------------------------

    print("\nRemoving old Chroma collection...")

    try:
        client = get_chroma_client()

        existing_collection = client.get_collection(
            name=COLLECTION_NAME
        )

        client.delete_collection(
            name=COLLECTION_NAME
        )

        print("Old collection removed successfully.")

    except Exception as exc:
        print(
            f"No existing collection to remove: {exc}"
        )

    # --------------------------------------------------------
    # Create new Chroma vector store
    # --------------------------------------------------------

    print("\nCreating new Chroma vector database...")

    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=settings.vector_db_url,
    )

    # --------------------------------------------------------
    # Add website chunks
    # --------------------------------------------------------

    print(
        f"Adding {len(documents)} website chunks "
        f"to Chroma collection..."
    )

    db.add_documents(documents)

    # --------------------------------------------------------
    # Count sources
    # --------------------------------------------------------

    source_counts = {}

    for document in documents:
        source = document.metadata.get(
            "source",
            "Unknown"
        )

        source_counts[source] = (
            source_counts.get(source, 0) + 1
        )

    # --------------------------------------------------------
    # Final information
    # --------------------------------------------------------

    print("\n===================================")
    print("VECTOR DATABASE CREATED SUCCESSFULLY")
    print("===================================")

    print(
        f"Website chunks indexed: "
        f"{len(documents)}"
    )

    print(
        f"Embedding model: "
        f"{embedding_model_name}"
    )

    print(
        f"Chroma path: "
        f"{settings.vector_db_url}"
    )

    print(
        f"Collection name: "
        f"{COLLECTION_NAME}"
    )

    print("\nDocuments by website:")

    for source, count in sorted(
        source_counts.items()
    ):
        print(
            f"  {source}: {count}"
        )

    print(
        "\nWebsite knowledge base is ready."
    )

    return db


# ============================================================
# ADD DOCUMENTS
# ============================================================

def add_documents_to_db(docs):
    """
    Add additional already-prepared documents
    to the existing Chroma database.
    """

    if not docs:
        print("No documents provided.")
        return get_vector_store()

    db = get_vector_store()

    db.add_documents(docs)

    print(
        f"Added {len(docs)} documents "
        f"to the vector database."
    )

    return db