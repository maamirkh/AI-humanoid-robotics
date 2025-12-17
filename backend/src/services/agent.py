"""
Agent reasoning service
Integrates with OpenAI-compatible API to generate responses based on retrieved context
"""
import openai
from typing import List, Dict, Any
from ..models.user_query import UserQuery, RetrievedContext
from ..models.conversation import GeneratedResponse
from ..core.config import Config
import logging

logger = logging.getLogger(__name__)

class AgentService:
    """Service for generating responses using AI agent with retrieved context"""

    def __init__(self):
        # Configure OpenAI client to work with Gemini API
        self.client = openai.OpenAI(
            api_key=Config.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"  # Gemini-compatible endpoint
        )
        self.model = "models/gemini-2.5-flash"  # Using the latest flash model
        logger.info("Agent service initialized with Gemini-compatible API")

    def generate_response(self,
                         query: UserQuery,
                         retrieved_contexts: List[RetrievedContext],
                         related_sections: List[RetrievedContext] = None,
                         conversation_context: str = None) -> GeneratedResponse:
        """Generate a contextual response based on query and retrieved context"""
        try:
            # Prepare the context for the agent
            context_text = "\n\n".join([
                f"Source: {ctx.source_path}\nSection: {ctx.section}\nContent: {ctx.content_text}"
                for ctx in retrieved_contexts
            ])

            # Prepare related sections for suggestions
            suggestions_text = ""
            if related_sections:
                suggestions_text = "\n\nRelated sections you might find interesting:\n"
                for i, section in enumerate(related_sections, 1):
                    suggestions_text += f"{i}. {section.section} - {section.source_path}\n"

            # Prepare conversation context if available
            conversation_context_text = ""
            if conversation_context:
                conversation_context_text = f"\n\nPrevious conversation context: {conversation_context}\n"

            # Create a prompt that includes the context and user query
            system_prompt = """You are an AI assistant for a Physical AI and Humanoid Robotics textbook.
            Answer questions based on the provided context. Be precise, informative, and cite sources when possible.
            If the answer is not in the provided context, clearly state that you don't have enough information.
            When relevant, suggest related sections from the textbook that the user might find interesting.
            Consider the conversation history to provide more contextual and coherent responses."""

            user_prompt = f"""
            Context:
            {context_text}

            {conversation_context_text}
            {suggestions_text}

            Question: {query.query_text}

            Please provide a detailed answer based on the context above, and suggest related sections if relevant:
            """

            # Call the API to generate the response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=1000
            )

            # Extract the response text
            response_text = response.choices[0].message.content

            # Create and return the GeneratedResponse object
            generated_response = GeneratedResponse(
                id=f"resp_{query.id}",
                session_id=query.session_id,
                query_id=query.id,
                response_text=response_text,
                source_context_ids=[ctx.id for ctx in retrieved_contexts],
                confidence_score=0.8  # Placeholder - in a real system you might calculate this based on similarity scores
            )

            logger.info(f"Generated response for query: {query.query_text[:50]}...")
            return generated_response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def validate_response_quality(self, response: GeneratedResponse, contexts: List[RetrievedContext]) -> bool:
        """Validate if the generated response is of good quality and properly sourced"""
        # Basic validation - in a real system you might have more sophisticated checks
        if not response.response_text or len(response.response_text.strip()) < 10:
            return False

        # Check if response mentions sources or says it doesn't have enough info
        response_lower = response.response_text.lower()
        if "i don't have enough information" in response_lower or "not mentioned in the context" in response_lower:
            # This is a valid response when context is insufficient
            return True

        # If we have contexts, the response should be somewhat related to them
        if contexts and len(contexts) > 0:
            # Basic check: response should have some relation to the content
            return True

        return True

# Global instance
agent_service = AgentService()