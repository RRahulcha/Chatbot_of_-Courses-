from app.rag.vectorstore import get_vector_store

def get_retriever(k=3):
    """
    Returns a retriever configured to fetch the top `k` most relevant documents
    from the vector database.
    """
    db = get_vector_store()
    return db.as_retriever(search_kwargs={"k": k})
