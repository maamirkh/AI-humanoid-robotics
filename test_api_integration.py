# Test script to verify backend API endpoints
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_status_endpoint():
    """Test the status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/status")
        print(f"Status check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Status check failed: {e}")
        return False

def test_session_creation():
    """Test creating a new session"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/chat/session/new", json={})
        print(f"Session creation: {response.status_code} - {response.json()}")
        if response.status_code == 200:
            return response.json().get("session_id")
        return None
    except Exception as e:
        print(f"Session creation failed: {e}")
        return None

def test_chat_endpoint(session_id):
    """Test the chat endpoint"""
    try:
        payload = {
            "query": "What is Physical AI?",
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/v1/chat/", json=payload)
        print(f"Chat endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'No response field')[:100]}...")
            return result.get('session_id')
        else:
            print(f"Error: {response.text}")
        return None
    except Exception as e:
        print(f"Chat endpoint failed: {e}")
        return None

def main():
    print("Testing RAG Chatbot Backend API endpoints...")
    print("="*50)

    # Test basic endpoints
    health_ok = test_health_endpoint()
    if not health_ok:
        print("❌ Health check failed. Is the backend running?")
        return

    status_ok = test_status_endpoint()
    if not status_ok:
        print("❌ Status check failed.")
        return

    print("\nTesting chat functionality...")
    print("-" * 30)

    # Test session creation
    session_id = test_session_creation()
    if not session_id:
        print("❌ Session creation failed.")
        return

    print(f"Created session: {session_id[:10]}...")

    # Test chat endpoint
    updated_session_id = test_chat_endpoint(session_id)
    if not updated_session_id:
        print("❌ Chat endpoint failed.")
        return

    print(f"\n✅ All tests passed! Session ID: {updated_session_id[:10]}...")
    print("Backend API is working correctly and ready for Docusaurus integration.")

if __name__ == "__main__":
    main()