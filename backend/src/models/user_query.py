"""
Data models for UserQuery and RetrievedContext entities
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserQuery(BaseModel):
    """Represents the natural language questions or statements submitted by readers seeking information"""
    id: str
    query_text: str
    user_id: Optional[str] = None
    session_id: str
    query_embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RetrievedContext(BaseModel):
    """Represents the relevant book passages retrieved to inform the response generation"""
    id: str
    content_id: str
    content_text: str
    similarity_score: float
    source_path: str
    section: str
    retrieved_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True