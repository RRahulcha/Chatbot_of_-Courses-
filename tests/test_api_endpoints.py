from fastapi.testclient import TestClient
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.main import app

client = TestClient(app)

def test_enquiry():
    response = client.post("/api/enquiry/", json={
        "name": "Test User",
        "phone": "9999999999",
        "email": "test@settribe.com",
        "course_interest": "Data Analytics"
    })
    print("Enquiry Response:", response.json())
    assert response.status_code == 200
    
def test_chat():
    response = client.post("/api/chat/", json={
        "session_id": "api_test_123",
        "message": "I need help with admission, talk to a human."
    })
    print("Chat Response:", response.json())
    assert response.status_code == 200

if __name__ == "__main__":
    test_enquiry()
    test_chat()
