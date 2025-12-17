"""
Health check API endpoints
Provides system health status
"""
from fastapi import APIRouter
from typing import Dict
from ...core.config import Config
from ...core.vector_db import get_vector_db
from ...core.database import db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """
    Basic health check endpoint
    """
    # Test configuration
    config_errors = Config.validate()
    config_ok = len(config_errors) == 0

    # Test vector database connection
    try:
        vector_db = get_vector_db()
        # Just try to get collections to test connection
        collections = vector_db.client.get_collections()
        vector_db_ok = True
    except Exception:
        vector_db_ok = False

    # Test database connection
    try:
        conn = db.get_connection()
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "healthy" if (config_ok and vector_db_ok and db_ok) else "unhealthy",
        "checks": {
            "configuration": {
                "status": "ok" if config_ok else "error",
                "errors": config_errors if not config_ok else []
            },
            "vector_database": {
                "status": "ok" if vector_db_ok else "error"
            },
            "relational_database": {
                "status": "ok" if db_ok else "error"
            }
        },
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

@router.get("/ready")
async def readiness_check():
    """
    Readiness check - confirms the service is ready to accept traffic
    """
    # For readiness, we check if all required services are available
    config_errors = Config.validate()
    config_ok = len(config_errors) == 0

    return {
        "ready": config_ok,
        "message": "Service is ready" if config_ok else f"Service not ready: {', '.join(config_errors)}",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

@router.get("/live")
async def liveness_check():
    """
    Liveness check - confirms the service is running
    """
    return {
        "alive": True,
        "message": "Service is running",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }