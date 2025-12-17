"""
Data models for ConversationSession and GeneratedResponse entities
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ConversationSession(BaseModel):
    """Represents the ongoing dialogue between a user and the chatbot, including history and metadata"""
    id: str
    user_id: Optional[str] = None
    session_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    current_section: Optional[str] = None  # Track current book section
    section_history: List[str] = Field(default_factory=list)  # Track sections visited in conversation
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    class Config:
        from_attributes = True


class GeneratedResponse(BaseModel):
    """Represents the answer provided to the user based on retrieved context and their query"""
    id: str
    session_id: str
    query_id: str
    response_text: str
    source_context_ids: List[str] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    response_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        from_attributes = True