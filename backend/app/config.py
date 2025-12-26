"""
Configuration management for the UHC Insurance Chatbot API
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "UHC Insurance Policy Chatbot API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        str(Path(__file__).parent.parent.parent / "chroma_data")
    )
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "insurance_policies")

    # LiteLLM Proxy (from llmops_lite)
    LITELLM_PROXY_BASE_URL: str = os.getenv("LITELLM_PROXY_BASE_URL", "")
    LITELLM_PROXY_SECRET_KEY: str = os.getenv("LITELLM_PROXY_SECRET_KEY", "")

    # LLM Settings
    DEFAULT_MODEL: str = "azure-gpt-5-mini"  # Using Azure GPT model from LiteLLM proxy
    DEFAULT_TEMPERATURE: float = 1.0  # GPT-5 and O-series models only support temperature=1
    MAX_TOKENS: int = 500

    # Vector Search
    TOP_K_RESULTS: int = 5  # Number of policy chunks to retrieve
    SIMILARITY_THRESHOLD: float = 0.7

    # Input Validation
    MAX_QUESTION_LENGTH: int = 500
    MIN_QUESTION_LENGTH: int = 5

    # Confidence Thresholds
    LOW_CONFIDENCE_THRESHOLD: float = 0.5

    # Cache Settings
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 86400  # 24 hours

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env that aren't defined here

# Create settings instance
settings = Settings()

# Validate critical settings
if not settings.LITELLM_PROXY_BASE_URL or not settings.LITELLM_PROXY_SECRET_KEY:
    print("⚠️  Warning: LiteLLM proxy credentials not configured")
    print("   Set LITELLM_PROXY_BASE_URL and LITELLM_PROXY_SECRET_KEY in .env")
