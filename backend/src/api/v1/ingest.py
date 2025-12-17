"""
Content ingestion API endpoints
Handles ingestion of new content into the RAG system
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from ...models.content import BookContent
from ...services.ingestion import ingestion_service
from ...services.embedding import embedding_service
from ...core.vector_db import get_vector_db
from ..dependencies import get_ingestion_service, get_embedding_service

router = APIRouter(prefix="/ingest", tags=["ingestion"])

class IngestRequest(BaseModel):
    """Request model for content ingestion"""
    content: str
    title: str
    source_path: str
    section: str = "General"

class IngestResponse(BaseModel):
    """Response model for content ingestion"""
    message: str
    content_id: str
    chunks_processed: int

class BulkIngestRequest(BaseModel):
    """Request model for bulk content ingestion"""
    docs_path: str

@router.post("/", response_model=IngestResponse)
async def ingest_content(
    request: IngestRequest,
    ingestion_svc = Depends(get_ingestion_service),
    embedding_svc = Depends(get_embedding_service)
):
    """
    Ingest a single piece of content into the RAG system
    """
    try:
        # Create a BookContent object
        content_id = f"content_{uuid4().hex}"
        book_content = BookContent(
            id=content_id,
            title=request.title,
            content=request.content,
            source_path=request.source_path,
            section=request.section,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Chunk the content
        chunks = ingestion_service.chunk_content(book_content.content)

        # Create BookContent objects for each chunk
        chunk_contents = []
        for idx, chunk_text in enumerate(chunks):
            chunk_id = f"{content_id}_chunk_{idx}"
            chunk_content = BookContent(
                id=chunk_id,
                title=f"{request.title} - Part {idx + 1}",
                content=chunk_text,
                source_path=request.source_path,
                section=request.section,
                metadata={
                    'original_id': content_id,
                    'chunk_index': idx,
                    'total_chunks': len(chunks)
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            chunk_contents.append(chunk_content)

        # Generate embeddings for all chunks
        embedded_contents = embedding_service.generate_content_embeddings(chunk_contents)

        # Store in vector database
        vector_db = get_vector_db()
        content_ids = [item['id'] for item in embedded_contents]
        embeddings = [item['embedding'] for item in embedded_contents]
        payloads = [
            {
                'id': item['content'].id,
                'title': item['content'].title,
                'content': item['content'].content,
                'source_path': item['content'].source_path,
                'section': item['content'].section,
                'metadata': item['content'].metadata
            }
            for item in embedded_contents
        ]

        vector_db.add_embeddings(content_ids, embeddings, payloads)

        response = IngestResponse(
            message=f"Successfully ingested content with {len(chunks)} chunks",
            content_id=content_id,
            chunks_processed=len(chunks)
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting content: {str(e)}"
        )

@router.post("/bulk", response_model=IngestResponse)
async def bulk_ingest_content(
    request: BulkIngestRequest,
    ingestion_svc = Depends(get_ingestion_service),
    embedding_svc = Depends(get_embedding_service)
):
    """
    Bulk ingest content from a directory (e.g., Docusaurus docs)
    """
    try:
        # Process the directory content
        book_contents = ingestion_service.process_docusaurus_docs(request.docs_path)

        if not book_contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content found in the specified directory"
            )

        # Generate embeddings for all content
        embedded_contents = embedding_service.generate_content_embeddings(book_contents)

        # Store in vector database
        vector_db = get_vector_db()
        content_ids = [item['id'] for item in embedded_contents]
        embeddings = [item['embedding'] for item in embedded_contents]
        payloads = [
            {
                'id': item['content'].id,
                'title': item['content'].title,
                'content': item['content'].content,
                'source_path': item['content'].source_path,
                'section': item['content'].section,
                'metadata': item['content'].metadata
            }
            for item in embedded_contents
        ]

        vector_db.add_embeddings(content_ids, embeddings, payloads)

        response = IngestResponse(
            message=f"Successfully ingested bulk content with {len(book_contents)} chunks",
            content_id="bulk_ingest",
            chunks_processed=len(book_contents)
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk ingestion: {str(e)}"
        )

@router.get("/status")
async def ingestion_status():
    """
    Get the status of the ingestion service
    """
    return {
        "status": "ready",
        "supported_formats": [".md", ".mdx"],
        "message": "Ingestion service is operational"
    }