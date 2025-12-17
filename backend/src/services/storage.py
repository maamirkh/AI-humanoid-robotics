"""
State and history management service
Handles storage and retrieval of conversation sessions and messages using Neon PostgreSQL
"""
from typing import List, Optional, Dict, Any
from ..models.conversation import ConversationSession, GeneratedResponse
from ..models.user_query import UserQuery
from ..core.database import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging

logger = logging.getLogger(__name__)

class StorageService:
    """Service for managing conversation state and history in PostgreSQL"""

    def __init__(self):
        logger.info("Storage service initialized")

    def create_session(self, session: ConversationSession) -> ConversationSession:
        """Create a new conversation session"""
        conn = None
        try:
            conn = next(get_db_connection())
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO conversation_sessions (id, user_id, session_metadata, current_section, section_history, created_at, updated_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, session_metadata, current_section, section_history, created_at, updated_at, is_active
            """, (
                session.id,
                session.user_id,
                json.dumps(session.session_metadata),
                session.current_section,
                session.section_history,
                session.created_at,
                session.updated_at,
                session.is_active
            ))

            result = cursor.fetchone()
            conn.commit()

            created_session = ConversationSession(
                id=result['id'],
                user_id=result['user_id'],
                session_metadata=result['session_metadata'],
                current_section=result['current_section'],
                section_history=result['section_history'],
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                is_active=result['is_active']
            )

            logger.info(f"Created conversation session: {session.id}")
            return created_session

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error creating session: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieve a conversation session by ID"""
        conn = None
        try:
            conn = next(get_db_connection())
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, user_id, session_metadata, current_section, section_history, created_at, updated_at, is_active
                FROM conversation_sessions
                WHERE id = %s
            """, (session_id,))

            result = cursor.fetchone()

            if result:
                return ConversationSession(
                    id=result['id'],
                    user_id=result['user_id'],
                    session_metadata=result['session_metadata'],
                    current_section=result['current_section'],
                    section_history=result['section_history'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    is_active=result['is_active']
                )

            return None

        except Exception as e:
            logger.error(f"Error retrieving session: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()

    def update_session(self, session: ConversationSession) -> ConversationSession:
        """Update an existing conversation session"""
        conn = None
        try:
            conn = next(get_db_connection())
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE conversation_sessions
                SET user_id = %s, session_metadata = %s, current_section = %s, section_history = %s, updated_at = %s, is_active = %s
                WHERE id = %s
                RETURNING id, user_id, session_metadata, current_section, section_history, created_at, updated_at, is_active
            """, (
                session.user_id,
                json.dumps(session.session_metadata),
                session.current_section,
                session.section_history,
                session.updated_at,
                session.is_active,
                session.id
            ))

            result = cursor.fetchone()
            conn.commit()

            updated_session = ConversationSession(
                id=result['id'],
                user_id=result['user_id'],
                session_metadata=result['session_metadata'],
                current_section=result['current_section'],
                section_history=result['section_history'],
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                is_active=result['is_active']
            )

            logger.info(f"Updated conversation session: {session.id}")
            return updated_session

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error updating session: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()

    def save_user_query(self, query: UserQuery) -> UserQuery:
        """Save a user query to the database"""
        conn = None
        try:
            conn = next(get_db_connection())
            cursor = conn.cursor()

            # Convert embedding to string representation if it exists
            embedding_str = json.dumps(query.query_embedding) if query.query_embedding else None

            cursor.execute("""
                INSERT INTO user_queries (id, query_text, user_id, session_id, query_embedding, created_at, processed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, query_text, user_id, session_id, query_embedding, created_at, processed_at
            """, (
                query.id,
                query.query_text,
                query.user_id,
                query.session_id,
                embedding_str,
                query.created_at,
                query.processed_at
            ))

            result = cursor.fetchone()
            conn.commit()

            # Convert embedding back from string if it was stored
            result_embedding = json.loads(result['query_embedding']) if result['query_embedding'] else None

            saved_query = UserQuery(
                id=result['id'],
                query_text=result['query_text'],
                user_id=result['user_id'],
                session_id=result['session_id'],
                query_embedding=result_embedding,
                created_at=result['created_at'],
                processed_at=result['processed_at']
            )

            logger.info(f"Saved user query: {query.id}")
            return saved_query

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error saving user query: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()

    def save_generated_response(self, response: GeneratedResponse) -> GeneratedResponse:
        """Save a generated response to the database"""
        conn = None
        try:
            conn = next(get_db_connection())
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO generated_responses (id, session_id, query_id, response_text, source_context_ids, confidence_score, created_at, response_metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, session_id, query_id, response_text, source_context_ids, confidence_score, created_at, response_metadata
            """, (
                response.id,
                response.session_id,
                response.query_id,
                response.response_text,
                response.source_context_ids,
                response.confidence_score,
                response.created_at,
                json.dumps(response.response_metadata)
            ))

            result = cursor.fetchone()
            conn.commit()

            saved_response = GeneratedResponse(
                id=result['id'],
                session_id=result['session_id'],
                query_id=result['query_id'],
                response_text=result['response_text'],
                source_context_ids=result['source_context_ids'],
                confidence_score=result['confidence_score'],
                created_at=result['created_at'],
                response_metadata=result['response_metadata']
            )

            logger.info(f"Saved generated response: {response.id}")
            return saved_response

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error saving generated response: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get the conversation history for a session"""
        conn = None
        try:
            conn = next(get_db_connection())
            cursor = conn.cursor()

            # Join user queries and generated responses for the session
            cursor.execute("""
                SELECT uq.query_text, gr.response_text, uq.created_at
                FROM user_queries uq
                LEFT JOIN generated_responses gr ON uq.id = gr.query_id
                WHERE uq.session_id = %s
                ORDER BY uq.created_at
            """, (session_id,))

            results = cursor.fetchall()

            history = []
            for row in results:
                history.append({
                    'query': row['query_text'],
                    'response': row['response_text'],
                    'timestamp': row['created_at']
                })

            logger.info(f"Retrieved history for session {session_id} with {len(history)} entries")
            return history

        except Exception as e:
            logger.error(f"Error retrieving session history: {str(e)}")
            raise
        finally:
            if conn:
                cursor.close()

# Global instance
storage_service = StorageService()