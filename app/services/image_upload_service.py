from fastapi.responses import HTMLResponse
from datetime import datetime
import shutil
import os

UPLOAD_DIR = "uploads"

async def save_upload_file(file):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"{datetime.now().isoformat()}: Imagen recibida: {file.filename}")
    return {"filename": file.filename, "message": "Imagen recibida correctamente"}

def list_uploaded_images():
    files = os.listdir(UPLOAD_DIR)
    images = [file for file in files if file.lower().endswith((".jpg", ".jpeg", ".png"))]
    html_content = "<html><body><h2>Imágenes subidas:</h2>"
    for image in images:
        html_content += f'<img src="/images/{image}" alt="{image}" width="300" /><br>'
    html_content += "</body></html>"
    return HTMLResponse(content=html_content)