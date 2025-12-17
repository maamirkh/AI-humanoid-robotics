"""
Embedding generation and management service
Uses Cohere to generate embeddings for content and queries
"""
import cohere
from typing import List, Dict, Any
import logging
from ..core.config import Config
from ..models.content import BookContent

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using Cohere"""

    def __init__(self):
        self.client = cohere.Client(Config.COHERE_API_KEY)
        self.model = "embed-multilingual-v3.0"  # Using multilingual model for broader language support
        logger.info("Embedding service initialized with Cohere client")

    def generate_embeddings(self, texts: List[str], input_type: str = "search_document") -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type=input_type
            )
            return [embedding for embedding in response.embeddings]
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def generate_content_embeddings(self, contents: List[BookContent]) -> List[Dict[str, Any]]:
        """Generate embeddings for book content items"""
        texts = [content.content for content in contents]
        embeddings = self.generate_embeddings(texts, "search_document")

        result = []
        for content, embedding in zip(contents, embeddings):
            result.append({
                'id': content.id,
                'content': content,
                'embedding': embedding
            })

        logger.info(f"Generated embeddings for {len(contents)} content items")
        return result

    def generate_query_embedding(self, query_text: str) -> List[float]:
        """Generate embedding for a single query"""
        try:
            response = self.client.embed(
                texts=[query_text],
                model=self.model,
                input_type="search_query"
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        """Generate embeddings in batches to handle large inputs"""
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.generate_embeddings(batch, "search_document")
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

# Global instance
embedding_service = EmbeddingService()