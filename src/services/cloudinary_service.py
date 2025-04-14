# src/services/cloudinary_service.py
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from io import BytesIO
from src.conf.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

async def upload_avatar(file: UploadFile) -> str:
    contents = await file.read()
    result = cloudinary.uploader.upload(BytesIO(contents), folder="avatars")
    return result.get("secure_url")