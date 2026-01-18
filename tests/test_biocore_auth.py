import sys
import os
sys.path.append(os.getcwd())
from fastapi.testclient import TestClient
from api.triage_api import app

client = TestClient(app)

def test_auth_success():
    response = client.post("/api/auth/biocore", json={"staff_id": "doctor", "bio_hash": "dummy"})
    assert response.status_code == 200
    assert response.json()["authenticated"] == True

def test_auth_failure():
    response = client.post("/api/auth/biocore", json={"staff_id": "x", "bio_hash": "dummy"})
    assert response.status_code == 200
    assert response.json()["authenticated"] == False

if __name__ == "__main__":
    try:
        test_auth_success()
        print("✅ Auth Success Test Passed")
        test_auth_failure()
        print("✅ Auth Failure Test Passed")
    except AssertionError as e:
        print(f"❌ Test Failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
