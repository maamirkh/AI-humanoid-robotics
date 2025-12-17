"""
API dependency management
Provides shared dependencies for API endpoints
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from ..core.config import Config
from ..core.database import get_db_connection
from ..core.vector_db import get_vector_db
from ..services.ingestion import ingestion_service
from ..services.embedding import embedding_service
from ..services.retrieval import retrieval_service
from ..services.agent import agent_service
from ..services.storage import storage_service
import logging

logger = logging.getLogger(__name__)

# Dependency functions
def get_ingestion_service():
    """Get the ingestion service instance"""
    return ingestion_service

def get_embedding_service():
    """Get the embedding service instance"""
    return embedding_service

def get_retrieval_service():
    """Get the retrieval service instance"""
    return retrieval_service

def get_agent_service():
    """Get the agent service instance"""
    return agent_service

def get_storage_service():
    """Get the storage service instance"""
    return storage_service

def get_vector_db_instance():
    """Get the vector database instance"""
    return get_vector_db()

def validate_api_key(api_key: str = None):
    """Validate API key if required"""
    if Config.DEBUG:
        # In debug mode, allow access without API key
        return True

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required"
        )

    # In a real application, you would validate the API key against a database
    # For now, we'll just check if it matches a placeholder
    return True