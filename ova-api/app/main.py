import logging

# Configure logging (do this once)
logging.basicConfig(
    filename="upload_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from app.routers import patient, registries_upload, user, registries_stats
import os
from app.db.user_database import init_db, get_db
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

app.include_router(registries_upload.router, tags=["Image Upload"])
app.include_router(patient.router, tags=["Patient"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(registries_stats.router, prefix="/stats", tags=["Stats"])