import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

class MockChatbotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/v1/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "healthy",
                "checks": {
                    "configuration": {"status": "ok", "errors": []},
                    "vector_database": {"status": "ok"},
                    "relational_database": {"status": "ok"}
                },
                "timestamp": "2025-12-16T19:04:06.753462"
            }
            self.wfile.write(json.dumps(response).encode())

        elif parsed_path.path == '/api/v1/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "app_name": "RAG Chatbot Backend",
                "version": "0.1.0",
                "debug": False,
                "vector_db_collection": "book_content",
                "api_prefix": "/api/v1",
                "timestamp": "2025-12-16T19:04:06.846461"
            }
            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        if parsed_path.path == '/api/v1/chat/session/new':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"session_id": f"session_{int(time.time())}"}
            self.wfile.write(json.dumps(response).encode())

        elif parsed_path.path == '/api/v1/chat/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            # Parse the request data
            request_data = json.loads(post_data.decode('utf-8'))
            query = request_data.get('query', 'default query')

            response = {
                "response": f"I understand you're asking about '{query}'. Based on the Physical AI and Humanoid Robotics textbook content, this topic covers important concepts related to embodied intelligence and motor control systems.",
                "session_id": request_data.get('session_id', 'session_mock'),
                "query_id": f"query_{int(time.time())}",
                "source_context": [],
                "suggested_sections": [],
                "confidence_score": 0.85
            }
            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.end_headers()

def start_mock_server(port=8000):
    server = HTTPServer(('localhost', port), MockChatbotHandler)
    print(f"Mock server running on http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    start_mock_server()