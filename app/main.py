from fastapi import FastAPI, File
from fastapi.staticfiles import StaticFiles
from app.routers import image_upload, patient
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

app.include_router(image_upload.router, tags=["Image Upload"])
app.include_router(patient.router, tags=["Patient"])