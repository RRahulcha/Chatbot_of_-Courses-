import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.config import settings

try:
    from langchain_groq import ChatGroq
except ImportError:  # pragma: no cover
    ChatGroq = None


def get_llm():
    if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
        print("WARNING: Using dummy LLM because no API key is configured.")
        from langchain_community.llms import FakeListLLM
        return FakeListLLM(responses=["This is a mock response from the SETTribe assistant since no API key is set."])

    if settings.groq_api_key and settings.groq_api_key != "your_groq_api_key_here":
        if ChatGroq is None:
            raise RuntimeError("langchain-groq is not installed. Install it to use the Groq API key.")
        return ChatGroq(
            groq_api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=0.0,
        )

    if not settings.groq_api_key:
        raise RuntimeError("No valid LLM API key is configured. Add GROQ_API_KEY or OPENAI_API_KEY to backend/.env")

    return ChatGroq(
        groq_api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.0,
    )
