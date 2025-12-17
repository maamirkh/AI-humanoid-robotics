"""
Main FastAPI application for the RAG Chatbot Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import chat, ingest, health
from .core.config import Config
from .core.vector_db import vector_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=Config.APP_NAME,
    description="RAG Chatbot Backend for Physical AI and Humanoid Robotics Textbook",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(ingest.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Initializing RAG Chatbot Backend...")

    # Validate configuration
    errors = Config.validate()
    if errors:
        logger.error(f"Configuration validation failed: {', '.join(errors)}")
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

    # Initialize vector database collection
    try:
        vector_db.create_collection()
        logger.info("Vector database collection created/verified")
    except Exception as e:
        logger.error(f"Failed to initialize vector database: {str(e)}")
        raise

    logger.info("RAG Chatbot Backend initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down RAG Chatbot Backend...")
    # Add any cleanup logic here if needed
    from .core.database import db
    db.close()
    logger.info("RAG Chatbot Backend shutdown complete")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Chatbot Backend for Physical AI and Humanoid Robotics Textbook",
        "version": "0.1.0",
        "status": "running",
        "api_docs": "/api/v1/docs"
    }

# Additional utility endpoints can be added here
@app.get("/api/v1/status")
async def status():
    """Detailed status endpoint"""
    return {
        "app_name": Config.APP_NAME,
        "version": "0.1.0",
        "debug": Config.DEBUG,
        "vector_db_collection": Config.QDRANT_COLLECTION_NAME,
        "api_prefix": Config.API_V1_STR,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )