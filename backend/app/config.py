
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]

# Load backend/.env
load_dotenv(BACKEND_ROOT / ".env")


class Settings(BaseSettings):
    # ---------------------------------------------------------
    # Groq / LLM
    # ---------------------------------------------------------
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    llama_api_key: str = ""
    llm_api_key: str = ""

    # ---------------------------------------------------------
    # Embeddings
    # ---------------------------------------------------------
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    groq_embedding_model: str = "text-embedding-3-small"

    # ---------------------------------------------------------
    # Vector database
    # ---------------------------------------------------------
    vector_db_url: str = str(
        PROJECT_ROOT / "backend" / "chroma_db"
    )

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    database_url: str = (
        f"sqlite:///{PROJECT_ROOT / 'settribe.db'}"
    )

    # ---------------------------------------------------------
    # Website scraper
    # ---------------------------------------------------------
    settribe_website_url: str = "https://settribe.com/"
    step_website_url: str = "https://stepsettribe.com/"

    web_request_timeout: int = 15
    web_max_pages: int = 20

    # ---------------------------------------------------------
    # API
    # ---------------------------------------------------------
    rate_limit: str = "100/minute"
    allowed_origins: str = "*"

    # ---------------------------------------------------------
    # Pydantic settings configuration
    # ---------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


# -------------------------------------------------------------
# Clean placeholder handling
# -------------------------------------------------------------
if settings.groq_api_key.strip() in {
    "",
    "your_groq_api_key_here",
    "YOUR_GROQ_API_KEY",
}:
    settings.groq_api_key = ""

if settings.llama_api_key.strip() in {
    "",
    "your_llama_api_key_here",
    "YOUR_LLAMA_API_KEY",
}:
    settings.llama_api_key = ""

# Use Groq key as the general LLM key when available.
settings.llm_api_key = (
    settings.groq_api_key
    or settings.llama_api_key
)

