# API Contracts: RAG Chatbot for Docusaurus Book

## Contract: Chat API
**Endpoint**: `POST /api/v1/chat`
**Purpose**: Process user queries and return contextual responses based on book content

**Request**:
```
{
  "query": "string (required) - The user's question or statement",
  "session_id": "string (optional) - Conversation session identifier",
  "selected_text": "string (optional) - Text selected by user for context-specific queries",
  "user_id": "string (optional) - User identifier for personalized responses"
}
```

**Response**:
```
{
  "response_id": "string - Unique identifier for this response",
  "answer": "string - The generated answer based on retrieved context",
  "sources": [
    {
      "content_id": "string - ID of the source content",
      "title": "string - Title of the source section",
      "source_path": "string - Path to the original document",
      "similarity_score": "float - Relevance score of this source"
    }
  ],
  "session_id": "string - Updated session identifier",
  "confidence": "float - Confidence score in the response accuracy"
}
```

**Error Responses**:
- `400`: Invalid request format or missing required fields
- `429`: Rate limit exceeded
- `500`: Internal server error during processing

---

## Contract: Content Ingestion API
**Endpoint**: `POST /api/v1/ingest`
**Purpose**: Index book content for semantic search capabilities

**Request**:
```
{
  "content": "string (required) - The book content to be indexed",
  "title": "string (required) - Title of the content section",
  "source_path": "string (required) - Path to the original document",
  "section": "string (required) - Book section or chapter reference",
  "metadata": "object (optional) - Additional content metadata"
}
```

**Response**:
```
{
  "content_id": "string - Unique identifier for the indexed content",
  "chunks_created": "integer - Number of content chunks created",
  "status": "string - Processing status (success, pending, error)",
  "message": "string - Additional status information"
}
```

**Error Responses**:
- `400`: Invalid content format or missing required fields
- `500`: Error during content processing or indexing

---

## Contract: Batch Content Ingestion API
**Endpoint**: `POST /api/v1/ingest/batch`
**Purpose**: Index multiple book content sections at once

**Request**:
```
{
  "contents": [
    {
      "content": "string (required) - The book content to be indexed",
      "title": "string (required) - Title of the content section",
      "source_path": "string (required) - Path to the original document",
      "section": "string (required) - Book section or chapter reference",
      "metadata": "object (optional) - Additional content metadata"
    }
  ]
}
```

**Response**:
```
{
  "processed_count": "integer - Number of contents successfully processed",
  "failed_count": "integer - Number of contents that failed to process",
  "results": [
    {
      "content_id": "string - Unique identifier for the indexed content",
      "source_path": "string - Path to the original document",
      "status": "string - Processing status for this item",
      "error": "string (optional) - Error message if processing failed"
    }
  ]
}
```

**Error Responses**:
- `400`: Invalid batch format or missing required fields
- `500`: Error during batch processing

---

## Contract: Conversation History API
**Endpoint**: `GET /api/v1/conversations/{session_id}`
**Purpose**: Retrieve conversation history for a specific session

**Path Parameters**:
- `session_id`: string (required) - The conversation session identifier

**Response**:
```
{
  "session_id": "string - The conversation session identifier",
  "created_at": "datetime - When the session was created",
  "updated_at": "datetime - When the session was last updated",
  "is_active": "boolean - Whether the session is currently active",
  "messages": [
    {
      "id": "string - Message identifier",
      "type": "string - Message type (query/response)",
      "content": "string - The message content",
      "timestamp": "datetime - When the message was created",
      "sources": [
        {
          "content_id": "string - ID of source content",
          "title": "string - Title of source section"
        }
      ]
    }
  ]
}
```

**Error Responses**:
- `404`: Session not found
- `500`: Error retrieving conversation history

---

## Contract: Health Check API
**Endpoint**: `GET /api/v1/health`
**Purpose**: Check the health status of the RAG chatbot service

**Response**:
```
{
  "status": "string - Overall service status (healthy, degraded, error)",
  "timestamp": "datetime - When the check was performed",
  "services": {
    "vector_db": "string - Status of vector database connection",
    "relational_db": "string - Status of relational database connection",
    "embedding_service": "string - Status of embedding service",
    "agent_service": "string - Status of agent reasoning service"
  }
}
```

**Error Responses**:
- `503`: Service unavailable