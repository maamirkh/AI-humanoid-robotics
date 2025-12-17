# RAG Chatbot Backend for Physical AI and Humanoid Robotics Textbook

This backend provides a Retrieval-Augmented Generation (RAG) chatbot system for the Physical AI and Humanoid Robotics textbook. It handles content ingestion, vector storage, semantic search, and AI-powered response generation.

## Architecture Overview

The system follows a microservice architecture with clear separation of concerns:

- **Ingestion Service**: Handles content processing from Docusaurus documentation
- **Embedding Service**: Generates vector embeddings using Cohere
- **Vector Database**: Stores content embeddings in Qdrant for semantic search
- **Retrieval Service**: Finds relevant context based on user queries
- **Agent Service**: Generates contextual responses using Gemini API
- **Storage Service**: Manages conversation history in PostgreSQL
- **API Layer**: FastAPI endpoints for chat and ingestion operations

## Environment Variables

Create a `.env` file in the backend root with the following variables:

```bash
COHERE_API_KEY=your_cohere_api_key
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=your_qdrant_cloud_url
DATABASE_URL=your_neon_postgres_connection_string
GEMINI_API_KEY=your_gemini_api_key
```

## Setup and Installation

1. **Prerequisites**:
   - Python 3.11+
   - UV package manager
   - Access to Qdrant Cloud (free tier)
   - Neon PostgreSQL database
   - Cohere API key
   - Google Gemini API key

2. **Installation**:
   ```bash
   # Navigate to the backend directory
   cd backend

   # Install dependencies using UV
   uv sync

   # Initialize the database schema
   uv run python init_db.py
   ```

3. **Run the application**:
   ```bash
   # Start the backend server
   uv run python -m src.main
   ```

## API Endpoints

### Chat Endpoints
- `POST /api/v1/chat/` - Process user queries and return contextual responses
- `GET /api/v1/chat/session/{session_id}` - Get conversation history
- `POST /api/v1/chat/session/new` - Create a new conversation session

### Ingestion Endpoints
- `POST /api/v1/ingest/` - Ingest single content item
- `POST /api/v1/ingest/bulk` - Bulk ingest content from directory
- `GET /api/v1/ingest/status` - Get ingestion service status

### Health Endpoints
- `GET /api/v1/health/` - Overall system health
- `GET /api/v1/health/ready` - Readiness check
- `GET /api/v1/health/live` - Liveness check

## Docusaurus Integration

The chatbot UI can be embedded in Docusaurus pages using the provided JavaScript widget:

```html
<!-- Include the chat widget in your Docusaurus pages -->
<script src="path/to/chat_widget.js"></script>
<script>
  // Initialize the chatbot with your backend URL
  const chatbot = new RAGChatbot({
    backendUrl: 'http://localhost:8000',
    containerId: 'rag-chatbot-container',
    theme: 'default'
  });
</script>
```

## Key Features

1. **Semantic Search**: Uses vector embeddings to find relevant content
2. **Conversation Context**: Maintains context across different book sections
3. **Content Suggestions**: Recommends related sections based on user queries
4. **Session Management**: Tracks conversation history for continuity
5. **Secure Architecture**: All sensitive data handled via environment variables

## Development

### Running Tests
```bash
# Run basic functionality tests
uv run python test_basic_functionality.py

# Run end-to-end validation
uv run python validate_e2e.py
```

### Project Structure
```
backend/
├── src/
│   ├── models/          # Data models
│   ├── services/        # Business logic services
│   ├── api/            # API endpoints
│   ├── core/           # Core utilities (config, db, vector_db)
│   └── main.py         # FastAPI application entry point
├── .env               # Environment variables
├── pyproject.toml     # Project dependencies
├── README.md          # This file
├── test_basic_functionality.py
├── validate_e2e.py
└── init_db.py         # Database initialization script
```

## Configuration

The system is configured entirely through environment variables. No hardcoded values are used anywhere in the system.

## Security

- All API keys and secrets are loaded from environment variables
- No sensitive information is stored in source code
- PostgreSQL connection uses secure connection strings
- Qdrant connection uses API keys for authentication

## Error Handling

The system implements comprehensive error handling at all levels:
- Service level: Each service handles its own errors gracefully
- API level: Proper HTTP status codes and error messages
- Database level: Connection pooling and retry logic
- External API level: Fallback mechanisms for API failures