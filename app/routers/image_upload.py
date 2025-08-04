from fastapi import APIRouter, File, UploadFile
from app.services.image_upload_service import save_upload_file, list_uploaded_images

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return await save_upload_file(file)

@router.get("/files")
async def list_files():
    return list_uploaded_images()