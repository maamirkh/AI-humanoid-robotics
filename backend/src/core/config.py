"""
Configuration management for the RAG Chatbot Backend
Handles loading and validation of environment variables from .env file
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class to manage environment variables"""

    # API Keys and Secrets
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Database URLs
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "RAG Chatbot Backend")
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Vector Database Settings
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "book_content")

    # Validation
    @classmethod
    def validate(cls) -> list[str]:
        """Validate that required environment variables are set"""
        errors = []
        required_vars = [
            "COHERE_API_KEY",
            "QDRANT_API_KEY",
            "QDRANT_URL",
            "DATABASE_URL",
            "GEMINI_API_KEY"
        ]

        for var in required_vars:
            value = getattr(cls, var)
            if not value:
                errors.append(f"Missing required environment variable: {var}")

        return errors

# Validate configuration at startup
validation_errors = Config.validate()
if validation_errors:
    raise ValueError(f"Configuration validation failed: {', '.join(validation_errors)}")

print("Configuration loaded and validated successfully")