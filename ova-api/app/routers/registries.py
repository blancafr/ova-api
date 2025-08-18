from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from app.services.registries_service import process_upload_file, list_uploaded_images, save_upload_file
from sqlalchemy.orm import Session
from app.db.registry_database import get_db
from app.main import logger
import os

from sqlalchemy.exc import IntegrityError
from app.db.registry_database import SessionLocal

UPLOAD_DIR = "uploads"
CONTROL_FILE = os.path.join(UPLOAD_DIR, ".processed_flag") 

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    save_upload_file(file)
    try:
        process_upload_file(file, db)
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {e}")
    return {
        "filename": file.filename,
        "message": "Imagen recibida correctamente",
    }

@router.get("/files")
async def list_files():
    return list_uploaded_images()

@router.post("/admin/process-existing")
async def process_existing_uploads(
    db: Session = Depends(get_db)
):

    if os.path.exists(CONTROL_FILE):
        raise HTTPException(status_code=400, detail="Este proceso ya se ejecutó antes")
    
    with open(CONTROL_FILE, "w") as f:
        f.write("processed")
    
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    files_sorted = sorted(files)

    processed_files = []
    errors = []

    for filename in files_sorted:
        file_path = os.path.join(UPLOAD_DIR, filename)

        class MockUploadFile:
            def __init__(self, path):
                self.filename = os.path.basename(path)
                self.path = path
            async def read(self):
                with open(self.path, "rb") as f:
                    return f.read()

        mock_file = MockUploadFile(file_path)

        try:
            process_upload_file(mock_file, db)
            processed_files.append(filename)
        except Exception as e:
            errors.append({"file": filename, "error": str(e)})

    return {"processed_files": processed_files, "errors": errors}
