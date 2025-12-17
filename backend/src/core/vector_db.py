"""
Vector database utilities for Qdrant
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
import logging
from .config import Config

logger = logging.getLogger(__name__)

class VectorDB:
    """Vector database manager for Qdrant"""

    def __init__(self):
        self.client = QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY,
            prefer_grpc=False  # Using HTTP for simplicity
        )
        self.collection_name = Config.QDRANT_COLLECTION_NAME

    def create_collection(self, vector_size: int = 1024):  # Changed to 1024 to match Cohere embedding size
        """Create a collection for storing book content embeddings"""
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name} with vector size: {vector_size}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            raise

    def add_embeddings(self,
                      content_ids: List[str],
                      embeddings: List[List[float]],
                      payloads: List[Dict[str, Any]]):
        """Add embeddings to the collection"""
        try:
            # Use UUIDs as required by Qdrant, but store original content_id in payload
            points = []
            for i, (content_id, embedding, payload) in enumerate(zip(content_ids, embeddings, payloads)):
                # Qdrant requires numeric IDs or UUIDs, so we'll use numeric IDs and store original ID in payload
                point_id = i  # Using numeric IDs as required by Qdrant
                # Store the original content_id in the payload so we can retrieve it later
                payload_with_original_id = payload.copy()
                payload_with_original_id['original_content_id'] = content_id
                points.append(
                    models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload_with_original_id
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Added {len(content_ids)} embeddings to collection")
        except Exception as e:
            logger.error(f"Failed to add embeddings: {str(e)}")
            raise

    def search_similar(self,
                      query_embedding: List[float],
                      limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content based on embedding"""
        try:
            # Try the query_points method first (newer API)
            from qdrant_client.http import models as qdrant_models
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit
            )

            results = []
            for hit in search_result.points:
                # Use the original content ID from payload if available, otherwise use the point ID
                content_id = hit.payload.get('original_content_id', str(hit.id))
                results.append({
                    "id": content_id,  # Use the original content ID
                    "payload": hit.payload,
                    "score": hit.score
                })

            return results
        except Exception as e:
            # If query_points fails, try the search method
            try:
                search_result = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=limit
                )

                results = []
                for hit in search_result:
                    # Use the original content ID from payload if available, otherwise use the point ID
                    content_id = hit.payload.get('original_content_id', str(hit.id))
                    results.append({
                        "id": content_id,  # Use the original content ID
                        "payload": hit.payload,
                        "score": hit.score
                    })

                return results
            except Exception as e2:
                logger.error(f"Search failed with both methods: {str(e)}, {str(e2)}")
                raise

    def delete_collection(self):
        """Delete the collection (useful for testing)"""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            raise

# Global vector database instance
vector_db = VectorDB()

def get_vector_db():
    """Get vector database instance"""
    return vector_db