# Quickstart Guide: RAG Chatbot Backend

## Overview
This guide provides a high-level understanding of how to work with the RAG chatbot backend system for the Physical AI & Humanoid Robotics textbook.

## System Components

### 1. Content Ingestion Pipeline
- Reads Docusaurus book content
- Normalizes and chunks content for semantic retrieval
- Generates embeddings using Cohere
- Stores vector representations in Qdrant
- Maintains relational metadata in Neon PostgreSQL

### 2. Query Processing
- Accepts user queries via API endpoints
- Generates embeddings for incoming queries
- Performs semantic search in Qdrant
- Retrieves relevant book content
- Passes context to agent for response generation

### 3. Response Generation
- Agent reasons over retrieved context
- Generates contextual responses based on book content
- Maintains conversation history in PostgreSQL
- Provides source attribution for transparency

## API Usage Examples

### Starting a Chat Session
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the principles of humanoid locomotion",
    "session_id": "session-123"
  }'
```

### Ingesting New Content
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Humanoid locomotion involves...",
    "title": "Locomotion Principles",
    "source_path": "/docs/locomotion.md",
    "section": "Module 3 - NVIDIA Isaac AI Brain"
  }'
```

## Architecture Flow

1. **Content Ingestion**: Book content flows from Docusaurus → Backend ingestion service → Vector chunking → Cohere embeddings → Qdrant storage
2. **Query Processing**: User query → Embedding generation → Qdrant semantic search → Context retrieval → Agent reasoning → Response generation
3. **Session Management**: Conversation state maintained in PostgreSQL → Session history tracking → Context continuity across queries

## Key Design Principles

- **Separation of Concerns**: Vector data in Qdrant, relational data in PostgreSQL
- **Backend-First**: All RAG logic handled server-side for security and performance
- **Scalable Architecture**: Component-based design supports concurrent user sessions
- **Transparent Responses**: Generated answers include source attribution from book content