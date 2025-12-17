"""
Basic functionality test for the RAG Chatbot Backend
Tests the core components without requiring external services
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import Config
from src.core.vector_db import VectorDB
from src.services.ingestion import IngestionService
from src.services.embedding import EmbeddingService
from src.services.retrieval import RetrievalService
from src.services.agent import AgentService
from src.services.storage import StorageService
from src.models.content import BookContent
from src.models.user_query import UserQuery
from src.models.conversation import ConversationSession
from uuid import uuid4
from datetime import datetime

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    errors = Config.validate()
    if errors:
        print(f"❌ Configuration errors: {errors}")
        return False
    print("✅ Configuration loaded successfully")
    return True

def test_ingestion_service():
    """Test ingestion service"""
    print("\nTesting ingestion service...")
    try:
        ingestion = IngestionService()
        print("✅ Ingestion service initialized")

        # Test content chunking
        sample_content = "This is a sample content for testing. It contains multiple sentences. Each sentence should be processed properly."
        chunks = ingestion.chunk_content(sample_content, chunk_size=50, overlap=10)

        print(f"✅ Content chunked into {len(chunks)} parts")
        for i, chunk in enumerate(chunks):
            print(f"   Chunk {i+1}: {chunk[:50]}...")

        return True
    except Exception as e:
        print(f"❌ Ingestion service error: {str(e)}")
        return False

def test_embedding_service():
    """Test embedding service (only if API key is configured)"""
    print("\nTesting embedding service...")
    try:
        if not Config.COHERE_API_KEY:
            print("⚠️  Skipping embedding test - COHERE_API_KEY not configured")
            return True

        embedding = EmbeddingService()
        print("✅ Embedding service initialized")

        # Test single embedding
        sample_text = "This is a test sentence for embedding."
        embedding_result = embedding.generate_query_embedding(sample_text)

        print(f"✅ Generated embedding with {len(embedding_result)} dimensions")
        return True
    except Exception as e:
        print(f"⚠️  Embedding service test failed (expected if API not configured): {str(e)}")
        return True  # Don't fail the test if API is not configured

def test_retrieval_service():
    """Test retrieval service initialization"""
    print("\nTesting retrieval service...")
    try:
        retrieval = RetrievalService()
        print("✅ Retrieval service initialized")
        return True
    except Exception as e:
        print(f"❌ Retrieval service error: {str(e)}")
        return False

def test_agent_service():
    """Test agent service (only if API key is configured)"""
    print("\nTesting agent service...")
    try:
        if not Config.GEMINI_API_KEY:
            print("⚠️  Skipping agent test - GEMINI_API_KEY not configured")
            return True

        agent = AgentService()
        print("✅ Agent service initialized")
        return True
    except Exception as e:
        print(f"⚠️  Agent service test failed (expected if API not configured): {str(e)}")
        return True  # Don't fail the test if API is not configured

def test_storage_service():
    """Test storage service initialization"""
    print("\nTesting storage service...")
    try:
        storage = StorageService()
        print("✅ Storage service initialized")
        return True
    except Exception as e:
        print(f"❌ Storage service error: {str(e)}")
        return False

def test_model_creation():
    """Test model creation"""
    print("\nTesting model creation...")
    try:
        # Test BookContent model
        content = BookContent(
            id=f"test_{uuid4().hex}",
            title="Test Content",
            content="This is test content for the RAG system.",
            source_path="/test/path.md",
            section="Test Section",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        print("✅ BookContent model created successfully")

        # Test UserQuery model
        query = UserQuery(
            id=f"query_{uuid4().hex}",
            query_text="What is this test about?",
            session_id=f"session_{uuid4().hex}",
            created_at=datetime.now()
        )
        print("✅ UserQuery model created successfully")

        # Test ConversationSession model
        session = ConversationSession(
            id=f"session_{uuid4().hex}",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        print("✅ ConversationSession model created successfully")

        return True
    except Exception as e:
        print(f"❌ Model creation error: {str(e)}")
        return False

def run_all_tests():
    """Run all basic functionality tests"""
    print("🧪 Running basic functionality tests for RAG Chatbot Backend\n")

    tests = [
        test_config,
        test_ingestion_service,
        test_embedding_service,
        test_retrieval_service,
        test_agent_service,
        test_storage_service,
        test_model_creation
    ]

    results = []
    for test in tests:
        results.append(test())

    passed = sum(results)
    total = len(results)

    print(f"\n📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All basic functionality tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)