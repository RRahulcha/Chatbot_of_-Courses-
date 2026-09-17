import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.config import settings
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:  # pragma: no cover
    HuggingFaceEmbeddings = None

try:
    from langchain_community.embeddings import FakeEmbeddings
except ImportError:  # pragma: no cover
    FakeEmbeddings = None


def get_embeddings():
    """Return a suitable embeddings instance.

    Preference order:
    1. Groq embeddings when a valid Groq key is configured.
    2. OpenAI embeddings when a valid OpenAI key is configured.
    3. Local HuggingFace embeddings if the dependency is installed.
    4. Fake embeddings as a safe offline fallback.
    """
    if settings.groq_api_key:
        return OpenAIEmbeddings(
            api_key=settings.groq_api_key,
            model=settings.groq_embedding_model,
            base_url="https://api.groq.com/openai/v1",
        )

    if settings.openai_api_key and settings.openai_api_key != "your_llm_api_key_here":
        return OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
        )

    if HuggingFaceEmbeddings is not None:
        try:
            return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        except Exception as exc:
            print(f"WARNING: HuggingFaceEmbeddings failed: {exc}")

    if FakeEmbeddings is not None:
        print("WARNING: No local embedding dependency is available; using FakeEmbeddings.")
        return FakeEmbeddings(size=1536)

    raise RuntimeError("No embedding backend is available. Install sentence-transformers or configure GROQ/OpenAI keys.")


from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
