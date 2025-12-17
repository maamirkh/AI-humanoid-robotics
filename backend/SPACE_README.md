# RAG Chatbot Backend for Physical AI and Humanoid Robotics Textbook (Hugging Face Deployment)

This Hugging Face Space hosts the backend for a Retrieval-Augmented Generation (RAG) chatbot system for the Physical AI and Humanoid Robotics textbook. It handles content ingestion, vector storage, semantic search, and AI-powered response generation.

## About this Space

This is a FastAPI application that provides:
- Semantic search capabilities using Qdrant vector database
- Question answering using Google Gemini API
- Content ingestion endpoints for textbook materials
- Conversation management and history

## Environment Variables Setup

For this Space to work correctly, you need to set the following secrets in your Hugging Face Space settings:

- `COHERE_API_KEY`: Cohere API key for embeddings (or use Google embeddings)
- `QDRANT_API_KEY`: Qdrant Cloud API key
- `QDRANT_URL`: Qdrant Cloud URL
- `DATABASE_URL`: PostgreSQL database URL (Neon)
- `GEMINI_API_KEY`: Google Gemini API key

## API Endpoints

Once deployed, the following endpoints will be available:

- `/` - Root endpoint with basic info
- `/api/v1/docs` - Interactive API documentation
- `/api/v1/redoc` - Alternative API documentation
- `/api/v1/chat` - Chat and Q&A endpoints
- `/api/v1/ingest` - Content ingestion endpoints
- `/api/v1/health` - Health check endpoints

## Architecture

The backend uses:
- FastAPI for the web framework
- Qdrant for vector database storage
- Google Gemini API for question answering
- PostgreSQL for metadata storage
- Cohere for embeddings (can be configured to use Google embeddings)

## Deployment Notes

This Space uses Docker to run the FastAPI application. The Dockerfile and requirements.txt are included in this repository.