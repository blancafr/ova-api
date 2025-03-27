from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models.paciente import PacienteCreate
from db.config import get_db
from db.db import insertar_paciente
import shutil
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"{datetime.now().isoformat()}: Imagen recibida: {file.filename}")
    return {"filename": file.filename, "message": "Imagen recibida correctamente"}

@app.get("/files")
async def list_files():
    # Listar todos los archivos en el directorio de subida
    files = os.listdir(UPLOAD_DIR)
    
    # Filtrar solo imágenes (por ejemplo, .jpg y .png)
    images = [file for file in files if file.lower().endswith((".jpg", ".jpeg", ".png"))]
    
    # Generar el HTML con las imágenes
    html_content = "<html><body><h2>Imágenes subidas:</h2>"
    for image in images:
        html_content += f'<img src="/images/{image}" alt="{image}" width="300" /><br>'
    
    html_content += "</body></html>"
    
    return HTMLResponse(content=html_content)

@app.post("/paciente/")
async def create_paciente(p: PacienteCreate):
    db = next(get_db())
    try:
        insertar_paciente(db, p)  # Usar la sesión correctamente
        db.commit()
        return {"message": "Paciente almacenado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()