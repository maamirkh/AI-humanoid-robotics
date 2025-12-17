"""
Data models for BookContent and ContentChunk entities
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ContentChunk(BaseModel):
    """Represents a chunk of book content that has been processed for vector storage"""
    id: str
    content_id: str
    chunk_text: str
    chunk_index: int
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class BookContent(BaseModel):
    """Represents the textual information from the Physical AI and Humanoid Robotics textbook that is indexed and searchable"""
    id: str
    title: str
    content: str
    source_path: str
    section: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True