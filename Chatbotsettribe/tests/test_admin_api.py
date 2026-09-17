from fastapi.testclient import TestClient
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.main import app

client = TestClient(app)

def test_admin_analytics():
    response = client.get("/api/admin/analytics")
    print("Analytics Response:", response.json())
    assert response.status_code == 200

def test_enquiry_list():
    response = client.get("/api/enquiry/")
    print("Enquiries Response:", response.json())
    assert response.status_code == 200

if __name__ == "__main__":
    test_admin_analytics()
    test_enquiry_list()
