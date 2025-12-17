"""
Chat API endpoints
Handles user queries and returns contextual responses
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from ...models.user_query import UserQuery
from ...models.conversation import ConversationSession
from ...services.ingestion import ingestion_service
from ...services.embedding import embedding_service
from ...services.retrieval import retrieval_service
from ...services.agent import agent_service
from ...services.storage import storage_service
from ..dependencies import (
    get_retrieval_service,
    get_agent_service,
    get_storage_service
)

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str
    session_id: str = None
    user_id: str = None

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    session_id: str
    query_id: str
    source_context: list = []
    suggested_sections: list = []
    confidence_score: float = None

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    retrieval_svc = Depends(get_retrieval_service),
    agent_svc = Depends(get_agent_service),
    storage_svc = Depends(get_storage_service)
):
    """
    Process a user query and return a contextual response
    """
    try:
        # Generate a session ID if not provided
        session_id = request.session_id or f"session_{uuid4().hex}"

        # Create or get existing session
        session = storage_svc.get_session(session_id)
        if not session:
            session = ConversationSession(
                id=session_id,
                user_id=request.user_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_active=True
            )
            session = storage_svc.create_session(session)

        # Create a query object
        query_id = f"query_{uuid4().hex}"
        user_query = UserQuery(
            id=query_id,
            query_text=request.query,
            user_id=request.user_id,
            session_id=session_id,
            created_at=datetime.now()
        )

        # Save the user query
        user_query = storage_svc.save_user_query(user_query)

        # Get conversation history to maintain context across sections
        conversation_history = storage_svc.get_session_history(session_id)

        # Retrieve relevant context considering conversation history
        retrieved_contexts = retrieval_service.retrieve_context_with_conversation_history(
            user_query, conversation_history
        )

        # Find related sections for content suggestions
        related_sections = retrieval_service.find_related_sections(user_query)

        # Generate response using the agent (with related sections and conversation context)
        generated_response = agent_service.generate_response(
            user_query,
            retrieved_contexts,
            related_sections,
            f"Previous conversation: {str(conversation_history[-2:])}" if conversation_history else None
        )

        # Save the generated response
        saved_response = storage_svc.save_generated_response(generated_response)

        # Update session timestamp and section history
        # Update current section based on the retrieved context
        if retrieved_contexts:
            current_section = retrieved_contexts[0].section
            if current_section not in session.section_history:
                session.section_history.append(current_section)
            session.current_section = current_section

        session.updated_at = datetime.now()
        storage_svc.update_session(session)

        # Prepare the response
        response = ChatResponse(
            response=saved_response.response_text,
            session_id=session_id,
            query_id=user_query.id,
            source_context=[
                {
                    "id": ctx.id,
                    "source_path": ctx.source_path,
                    "section": ctx.section,
                    "similarity_score": ctx.similarity_score
                }
                for ctx in retrieved_contexts
            ],
            suggested_sections=[
                {
                    "id": ctx.id,
                    "source_path": ctx.source_path,
                    "section": ctx.section,
                    "similarity_score": ctx.similarity_score
                }
                for ctx in related_sections
            ],
            confidence_score=saved_response.confidence_score
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/session/{session_id}")
async def get_session_history(session_id: str, storage_svc = Depends(get_storage_service)):
    """
    Get the conversation history for a specific session
    """
    try:
        history = storage_svc.get_session_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session history: {str(e)}"
        )

@router.post("/session/new")
async def create_new_session(user_id: str = None, storage_svc = Depends(get_storage_service)):
    """
    Create a new conversation session
    """
    try:
        session_id = f"session_{uuid4().hex}"
        session = ConversationSession(
            id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )
        created_session = storage_svc.create_session(session)
        return {"session_id": created_session.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}"
        )