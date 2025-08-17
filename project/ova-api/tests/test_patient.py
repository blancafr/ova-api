from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_patient_success():
    payload = {
        "gender": "male",
        "age": "30",
        "disease": "flu",
        "comment": "No allergies",
        "date": "2023-01-01"
    }
    response = client.post("/paciente/", json=payload)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["gender"] == payload["gender"]

def test_create_patient_error():
    # Missing required field 'gender'
    payload = {
        # "gender": "male",
        "age": "30",
        "disease": "flu",
        "comment": "No allergies",
        "date": "2023-01-01"
    }
    response = client.post("/paciente/", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (validation error)
    data = response.json()
    assert data["detail"]