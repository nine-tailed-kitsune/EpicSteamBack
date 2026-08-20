import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.models.user import User
from app.auth import get_current_user

router = APIRouter(prefix="/uploads", tags=["uploads"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 300 * 1024 * 1024

async def save_upload(file: UploadFile, allowed_types: set[str], max_size: int) -> str:
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")

    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="Файл слишком большой")

    extension = os.path.splitext(file.filename or "")[1]
    filename = f"{uuid.uuid4().hex}{extension}"
    path = UPLOAD_DIR / filename

    with open(path, "wb") as f:
        f.write(content)

    return f"/media/{filename}"

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    url = await save_upload(file, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
    return {"url": url}

@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    url = await save_upload(file, ALLOWED_VIDEO_TYPES, MAX_VIDEO_SIZE)
    return {"url": url}
