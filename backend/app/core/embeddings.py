from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings():
    """
    Return the local HuggingFace embedding model.

    IMPORTANT:
    Groq is used only for the LLM.
    Chroma uses the same local embedding model
    for both indexing and querying.
    """

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )