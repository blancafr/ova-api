import logging

# Configure logging (do this once)
logging.basicConfig(
    filename="upload_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

from fastapi import FastAPI, File
from fastapi.staticfiles import StaticFiles
from app.routers import patient, registries
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

app.include_router(registries.router, tags=["Image Upload"])
app.include_router(patient.router, tags=["Patient"])