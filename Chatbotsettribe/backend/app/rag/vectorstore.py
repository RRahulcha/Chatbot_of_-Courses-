from pathlib import Path
from langchain_chroma import Chroma
from chromadb.errors import InvalidArgumentError
from app.core.embeddings import get_embeddings
from app.config import PROJECT_ROOT, settings

COURSES_DIR = PROJECT_ROOT / "data" 

def _recreate_collection(db, embeddings):
    try:
        db.delete_collection()
    except Exception:
        pass
    return Chroma(
        collection_name="settribe_docs",
        embedding_function=embeddings,
        persist_directory=settings.vector_db_url,
    )


def get_vector_store():
    embeddings = get_embeddings()
    collection_name = "settribe_docs"

    db = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=settings.vector_db_url,
    )

    try:
        db.similarity_search("probe", k=1)
        return db
    except (InvalidArgumentError, ValueError, RuntimeError):
        print("WARNING: Chroma collection is stale or incompatible with the active embedding model. Rebuilding the collection.")
        db = _recreate_collection(db, embeddings)
        return db


def add_documents_to_db(docs):
    db = get_vector_store()
    db.add_documents(docs)
    db.persist()



from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.embeddings import get_embeddings
from app.config import settings, PROJECT_ROOT

# ============================================================ 
# CONFIGURATION 
# ============================================================
COLLECTION_NAME = "settribe_docs" 
# Root knowledge-base directory 
DATA_DIR = PROJECT_ROOT / "data"

# ============================================================ 
# VECTOR STORE 
# ============================================================
def get_vector_store():
    """
    Connect to the existing Chroma vector database.
    """
    embeddings = get_embeddings()

    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=settings.vector_db_url,
    )

    try:
        db.similarity_search("SETTribe", k=1)
        return db

    except (InvalidArgumentError, ValueError, RuntimeError):
        print("WARNING: Chroma collection is stale or incompatible.")
        print("Recreating Chroma collection...")

        try:
            db.delete_collection()
            print("Old Chroma collection removed.")

        except Exception as exc:
            print(f"Could not remove old collection: {exc}")

        return Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=settings.vector_db_url,
        )

# ============================================================ 
# LOAD ALL KNOWLEDGE-BASE DOCUMENTS 
# ============================================================
def load_documents():
    """
    Load every .txt file from data/courses.
    Recursively load every .txt file from the entire data directory. 
    Example: 
    data/ 
    ├── courses/ 
    │ ├── data_analytics.txt 
    │ ├── data_science.txt 
    │ └── devops.txt 
    │ ├── company/ 
    │ ├── company_overview.txt 
    │ └── company_projects.txt 
    │ ├── internships/ 
    │ ├── internship_overview.txt 
    │ └── internship_details.txt 
    │ ├── faq/ 
    │ ├── faq_general.txt 
    │ └── faq_courses_internships.txt 
    │ ├── policies/ 
    │ ├── policies_overview.txt 
    │ └── policies_details.txt 
    │ └── other/ 
    └── ... All .txt files inside these folders are loaded automatically. 
    """ 
    print("\n===================================") 
    print("LOADING SETTRIBE KNOWLEDGE BASE") 
    print("===================================\n") 

    print(f"Knowledge base directory:") 
    print(DATA_DIR)


    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Course directory not found: {DATA_DIR}"
        )

    documents = []

    txt_files = list(DATA_DIR.glob("*.txt"))

    if not txt_files:
        raise ValueError(
            f"No .txt files found in: {DATA_DIR}"
        )

    print(f"\nFound {len(txt_files)} TXT files.\n")
    # -------------------------------------------------------- 
    # Read every TXT file 
    # --------------------------------------------------------

    for file_path in txt_files:

        print(f"Loading: {file_path.name}")
        try:
            text = file_path.read_text(
                encoding="utf-8"
           )

        except Exception as exc:
            print(f"Error reading {file_path.name}: {exc}")
            continue

        # skip empty files
        if not text.strip():
            print(f"Skipping empty file: {file_path.relative_to(DATA_DIR)}")
            continue

        # ---------------------------------------------------- 
        # Relative path inside data/ 
        # ---------------------------------------------------- 
        relative_path = file_path.relative_to(DATA_DIR) 
        # Example: 
        # courses/data_analytics.txt 
        # company/company_overview.txt 
        # policies/policies_details.txt 
         
        relative_path_string = str( 
            relative_path 
        ).replace("\\", "/")


        #----------------------------------------------------
        #Determine category 
        # ---------------------------------------------------- 
        if len(relative_path.parts) > 1: 
            category = relative_path.parts[0] 
        else: 
            category = "other" 

        # ---------------------------------------------------- 
        # Create LangChain Document 
        # ----------------------------------------------------

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": relative_path.string,
                    "file_name": file_path.name,
                    "file_type":"txt",
                    "category": category,
                },
            )
        )

    print(
        f"Loaded [{category}]"
        f"{relative_path_string}"
    )

    print(f"\nSuccessfully loaded "
          f"{len(documents)} documents."
    )

    return documents


def build_vector_store():
    """
    Build the Chroma database from all course TXT files.
    """

    print("\n==============================")
    print("BUILDING SETTRIBE VECTOR STORE")
    print("==============================\n")

    # 1. Load TXT files
    documents = load_documents()

    if not documents:
        raise ValueError(
            "No course documents were loaded."
        )

    print(
        f"\nTotal documents loaded: {len(documents)}"
    )

    # 2. Split documents into chunks
    print("\nSplitting documents into chunks...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    # 3. Create embeddings
    print("\nCreating embeddings...")

    embeddings = get_embeddings()

    # 4. Delete old Chroma collection
    print("\nRemoving old Chroma collection...")

    try:
        old_db = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=settings.vector_db_url,
        )

        old_db.delete_collection()

        print("Old collection removed.")

    except Exception as exc:
        print(f"No old collection to remove: {exc}")

    # 5. Create fresh Chroma database
    print("\nCreating new Chroma vector database...")

    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=settings.vector_db_url,
    )

    # 6. Add all chunks
    print("Adding course chunks to Chroma...")

    db.add_documents(chunks)

    # -------------------------------------------------------- 
    # 7. Display category statistics 
    # -------------------------------------------------------- 
    category_counts = {} 
    for document in documents: 
        category = document.metadata.get( "category", "other" ) 
        category_counts[category] = ( 
            category_counts.get(category, 0) + 1 )

    print("\n===================================")
    print("VECTOR DATABASE CREATED SUCCESSFULLY")
    print("===================================")

    print(f"Course files: {len(documents)}")
    print(f"Chunks: {len(chunks)}")
    print("\nDocuments by category:") 
    for category, count in sorted( 
        category_counts.items() 
    ): 
        print( 
            f" {category}: {count}" 
        )

    print(f"Database: {settings.vector_db_url}")

    return db

# ============================================================ 
# ADD DOCUMENTS TO EXISTING DATABASE 
# ============================================================

def add_documents_to_db(docs):
    """
    Add additional documents to the existing vector database.
    """

    if not docs: 
        print( 
            "No documents provided." 
        ) 

        return get_vector_store()

    db = get_vector_store()

    db.add_documents(docs)

    print( 
        f"Added {len(docs)} documents " 
        f"to the vector database." 

    )

    return db