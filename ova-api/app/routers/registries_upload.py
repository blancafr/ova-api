from fastapi import APIRouter, File, UploadFile, Depends
from app.services.registries_service import process_upload_file, save_upload_file
from sqlalchemy.orm import Session
from app.db.registry_database import get_db
from app.main import logger
import os


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

