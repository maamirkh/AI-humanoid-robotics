"""
RAG retrieval service
Handles embedding user queries and retrieving relevant context from vector database
"""
from typing import List, Dict, Any
from ..models.user_query import UserQuery, RetrievedContext
from ..models.content import BookContent
from ..core.vector_db import get_vector_db
from ..services.embedding import embedding_service
import logging

logger = logging.getLogger(__name__)

class RetrievalService:
    """Service for retrieving relevant context based on user queries"""

    def __init__(self):
        self.vector_db = get_vector_db()
        logger.info("Retrieval service initialized")

    def retrieve_context(self, query: UserQuery, top_k: int = 5) -> List[RetrievedContext]:
        """Retrieve relevant context for a user query"""
        try:
            # Generate embedding for the query if not already present
            if not query.query_embedding:
                query_embedding = embedding_service.generate_query_embedding(query.query_text)
            else:
                query_embedding = query.query_embedding

            # Search for similar content in vector database
            search_results = self.vector_db.search_similar(query_embedding, limit=top_k)

            retrieved_contexts = []
            for result in search_results:
                payload = result['payload']

                retrieved_context = RetrievedContext(
                    id=result['id'],
                    content_id=payload.get('id', ''),
                    content_text=payload.get('content', ''),
                    similarity_score=result['score'],
                    source_path=payload.get('source_path', ''),
                    section=payload.get('section', ''),
                )
                retrieved_contexts.append(retrieved_context)

            logger.info(f"Retrieved {len(retrieved_contexts)} context items for query: {query.query_text[:50]}...")
            return retrieved_contexts

        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            raise

    def retrieve_context_by_content_ids(self, content_ids: List[str]) -> List[RetrievedContext]:
        """Retrieve specific content by IDs (useful for getting full documents)"""
        try:
            # This would be a more complex implementation that fetches by IDs
            # For now, we'll implement a basic version that could be enhanced
            # In a real implementation, you might need to query the database differently
            logger.info(f"Retrieving context for specific content IDs: {content_ids}")
            # This is a placeholder - in a real system you'd fetch by ID from your vector store
            return []
        except Exception as e:
            logger.error(f"Error retrieving context by content IDs: {str(e)}")
            raise

    def find_related_sections(self, query: UserQuery, current_section: str = None, top_k: int = 3) -> List[RetrievedContext]:
        """Find related book sections based on the current query and context"""
        try:
            # Generate embedding for the query if not already present
            if not query.query_embedding:
                query_embedding = embedding_service.generate_query_embedding(query.query_text)
            else:
                query_embedding = query.query_embedding

            # Search for similar content in vector database
            search_results = self.vector_db.search_similar(query_embedding, limit=top_k*2)  # Get more results to filter

            retrieved_contexts = []
            for result in search_results:
                payload = result['payload']

                # Skip if this is the same section as current (if provided)
                if current_section and payload.get('section', '') == current_section:
                    continue

                retrieved_context = RetrievedContext(
                    id=result['id'],
                    content_id=payload.get('id', ''),
                    content_text=payload.get('content', ''),
                    similarity_score=result['score'],
                    source_path=payload.get('source_path', ''),
                    section=payload.get('section', ''),
                )
                retrieved_contexts.append(retrieved_context)

                # Stop when we have enough related sections
                if len(retrieved_contexts) >= top_k:
                    break

            logger.info(f"Found {len(retrieved_contexts)} related sections for query: {query.query_text[:50]}...")
            return retrieved_contexts

        except Exception as e:
            logger.error(f"Error finding related sections: {str(e)}")
            raise

    def retrieve_context_with_conversation_history(self,
                                                  query: UserQuery,
                                                  conversation_history: List[Dict],
                                                  top_k: int = 5) -> List[RetrievedContext]:
        """Retrieve context considering both the current query and conversation history"""
        try:
            # Combine current query with conversation history for better context
            conversation_context = " ".join([
                f"Q: {item.get('query', '')} A: {item.get('response', '')}"
                for item in conversation_history[-3:]  # Use last 3 exchanges
            ])

            # Create an enhanced query that includes conversation context
            enhanced_query = f"{conversation_context} Current question: {query.query_text}"

            # Generate embedding for the enhanced query
            enhanced_embedding = embedding_service.generate_query_embedding(enhanced_query)

            # Search for similar content in vector database
            search_results = self.vector_db.search_similar(enhanced_embedding, limit=top_k)

            retrieved_contexts = []
            for result in search_results:
                payload = result['payload']

                retrieved_context = RetrievedContext(
                    id=result['id'],
                    content_id=payload.get('id', ''),
                    content_text=payload.get('content', ''),
                    similarity_score=result['score'],
                    source_path=payload.get('source_path', ''),
                    section=payload.get('section', ''),
                )
                retrieved_contexts.append(retrieved_context)

            logger.info(f"Retrieved {len(retrieved_contexts)} context items considering conversation history for query: {query.query_text[:50]}...")
            return retrieved_contexts

        except Exception as e:
            logger.error(f"Error retrieving context with conversation history: {str(e)}")
            # Fallback to regular retrieval
            return self.retrieve_context(query, top_k)

# Global instance
retrieval_service = RetrievalService()