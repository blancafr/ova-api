from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_upload_image():
    # Create a dummy image file in memory
    file_content = b"test image content"
    file_name = "test_image.jpg"
    files = {"file": (file_name, file_content, "image/jpeg")}

    response = client.post("/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == file_name
    assert "message" in data

    # Check that the file was actually saved
    upload_path = os.path.join("uploads", file_name)
    assert os.path.exists(upload_path)

    # Clean up: remove the test image file
    os.remove(upload_path)