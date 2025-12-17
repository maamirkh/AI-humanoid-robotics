"""
Database schema for the RAG Chatbot Backend
This file contains the SQL schema for the PostgreSQL database tables
"""
# Note: In a real application, you would use an ORM like SQLAlchemy or Alembic for migrations
# For this implementation, we'll define the schema as SQL statements

SCHEMA_SQL = """
-- Conversation Sessions Table
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    session_metadata JSONB,
    current_section VARCHAR(255),
    section_history TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- User Queries Table
CREATE TABLE IF NOT EXISTS user_queries (
    id VARCHAR(255) PRIMARY KEY,
    query_text TEXT NOT NULL,
    user_id VARCHAR(255),
    session_id VARCHAR(255) REFERENCES conversation_sessions(id),
    query_embedding JSONB,  -- Store as JSON array
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Generated Responses Table
CREATE TABLE IF NOT EXISTS generated_responses (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES conversation_sessions(id),
    query_id VARCHAR(255) REFERENCES user_queries(id),
    response_text TEXT NOT NULL,
    source_context_ids TEXT[],  -- Array of context IDs
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    response_metadata JSONB
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_queries_session_id ON user_queries(session_id);
CREATE INDEX IF NOT EXISTS idx_generated_responses_session_id ON generated_responses(session_id);
CREATE INDEX IF NOT EXISTS idx_generated_responses_query_id ON generated_responses(query_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user_id ON conversation_sessions(user_id);
"""