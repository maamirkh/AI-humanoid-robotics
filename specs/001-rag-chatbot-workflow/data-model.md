# Data Model: RAG Chatbot for Docusaurus Book

## Entity: BookContent
**Description**: Represents the textual information from the Physical AI and Humanoid Robotics textbook that is indexed and searchable

**Fields**:
- `id` (string): Unique identifier for the content chunk
- `title` (string): Title or heading of the content section
- `content` (string): The actual text content for semantic search
- `source_path` (string): Path to the original document/file
- `section` (string): Book section or chapter reference
- `embedding` (array): Vector representation for semantic search
- `metadata` (object): Additional content metadata (author, date, etc.)
- `created_at` (datetime): Timestamp of when content was indexed
- `updated_at` (datetime): Timestamp of last update

**Relationships**:
- One-to-many with ContentChunk (content may be chunked into multiple vectors)

**Validation rules**:
- Content must not exceed maximum token length for embedding model
- Source path must be valid and accessible
- Required fields: id, content, source_path

## Entity: UserQuery
**Description**: Represents the natural language questions or statements submitted by readers seeking information

**Fields**:
- `id` (string): Unique identifier for the query
- `query_text` (string): The original user query text
- `user_id` (string): Identifier for the user making the query (optional)
- `session_id` (string): Session identifier for conversation context
- `query_embedding` (array): Vector representation of the query
- `created_at` (datetime): Timestamp when query was submitted
- `processed_at` (datetime): Timestamp when query was processed

**Relationships**:
- Belongs to ConversationSession (queries are part of sessions)
- Many-to-many with RetrievedContext (queries retrieve multiple context chunks)

**Validation rules**:
- Query text must not be empty
- Query text must not exceed maximum token length
- Required fields: id, query_text, session_id

## Entity: RetrievedContext
**Description**: Represents the relevant book passages retrieved to inform the response generation

**Fields**:
- `id` (string): Unique identifier for the retrieved context
- `content_id` (string): Reference to the original BookContent
- `content_text` (string): The actual content text that was retrieved
- `similarity_score` (float): Score indicating relevance to the query
- `source_path` (string): Path to the original document
- `section` (string): Book section or chapter reference
- `retrieved_at` (datetime): Timestamp when context was retrieved

**Relationships**:
- Belongs to UserQuery (context is retrieved for specific queries)
- Belongs to BookContent (context originates from book content)

**Validation rules**:
- Content text must not be empty
- Similarity score must be between 0 and 1
- Required fields: id, content_text, similarity_score, content_id

## Entity: ConversationSession
**Description**: Represents the ongoing dialogue between a user and the chatbot, including history and metadata

**Fields**:
- `id` (string): Unique identifier for the conversation session
- `user_id` (string): Identifier for the user (optional for anonymous sessions)
- `session_metadata` (object): Additional session metadata
- `created_at` (datetime): Timestamp when session started
- `updated_at` (datetime): Timestamp of last activity
- `is_active` (boolean): Whether the session is currently active

**Relationships**:
- One-to-many with UserQuery (sessions contain multiple queries)
- One-to-many with GeneratedResponse (sessions contain multiple responses)

**Validation rules**:
- Required fields: id, created_at
- Session must have at least one query or response to remain active

## Entity: GeneratedResponse
**Description**: Represents the answer provided to the user based on retrieved context and their query

**Fields**:
- `id` (string): Unique identifier for the response
- `session_id` (string): Reference to the conversation session
- `query_id` (string): Reference to the original user query
- `response_text` (string): The generated response text
- `source_context_ids` (array): IDs of context used to generate response
- `confidence_score` (float): Confidence level in the response accuracy
- `created_at` (datetime): Timestamp when response was generated
- `response_metadata` (object): Additional metadata about the response generation

**Relationships**:
- Belongs to ConversationSession (responses are part of sessions)
- Belongs to UserQuery (responses are for specific queries)
- Many-to-many with RetrievedContext (responses may use multiple context chunks)

**Validation rules**:
- Response text must not be empty
- Confidence score must be between 0 and 1
- Required fields: id, session_id, query_id, response_text

## Entity: ContentChunk
**Description**: Represents a chunk of book content that has been processed for vector storage

**Fields**:
- `id` (string): Unique identifier for the content chunk
- `content_id` (string): Reference to the original BookContent
- `chunk_text` (string): The text of this specific chunk
- `chunk_index` (integer): Position of this chunk in the original content
- `embedding` (array): Vector representation for semantic search
- `created_at` (datetime): Timestamp when chunk was created

**Relationships**:
- Belongs to BookContent (chunks originate from book content)

**Validation rules**:
- Chunk text must not be empty
- Chunk index must be non-negative
- Required fields: id, content_id, chunk_text, chunk_index