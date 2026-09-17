import os
from pathlib import Path
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT / "data" / "courses"


def _valid_key(value: str | None, placeholder: str = "your_llm_api_key_here") -> str:
    if value is None:
        return ""
    value = value.strip()
    if not value or value == placeholder:
        return ""
    return value


class Settings(BaseSettings):
    groq_api_key: str = _valid_key(os.getenv("GROQ_API_KEY")) or _valid_key(os.getenv("GOUQ_API_KEY"))
    openai_api_key: str = _valid_key(os.getenv("OPENAI_API_KEY"))

    # Prefer a real Groq key, otherwise a real OpenAI key; ignore placeholder values
    llm_api_key: str = (
        _valid_key(os.getenv("LLM_API_KEY"))
        or groq_api_key
        or openai_api_key
    )
    vector_db_url: str = os.getenv("VECTOR_DB_URL", str(PROJECT_ROOT / "chroma_db"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    groq_embedding_model: str = os.getenv("GROQ_EMBEDDING_MODEL", "text-embedding-3-small")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'settribe.db'}")

    # Additional optional settings
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    rate_limit: str = os.getenv("RATE_LIMIT", "100/minute")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")

    class Config:
        env_file = PROJECT_ROOT / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
