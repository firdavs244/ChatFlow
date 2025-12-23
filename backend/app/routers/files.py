"""
ChatFlow - File Upload Router
"""

import uuid
from datetime import datetime
from typing import Annotated

import aioboto3
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter()


def get_s3_client():
    """Get S3/MinIO client session."""
    session = aioboto3.Session()
    return session.client(
        "s3",
        endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
        aws_access_key_id=settings.MINIO_ROOT_USER,
        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
    )


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a file to storage."""
    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB",
        )
    
    # Validate file type
    content_type = file.content_type or "application/octet-stream"
    if content_type not in settings.ALLOWED_FILE_TYPES_LIST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed: {content_type}",
        )
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
    
    # Organize by date and user
    date_path = datetime.utcnow().strftime("%Y/%m/%d")
    object_key = f"uploads/{date_path}/{current_user.id}/{unique_filename}"
    
    try:
        async with get_s3_client() as s3:
            await s3.put_object(
                Bucket=settings.MINIO_BUCKET_NAME,
                Key=object_key,
                Body=file_content,
                ContentType=content_type,
            )
        
        # Build file URL
        file_url = f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{object_key}"
        
        return {
            "file_name": file.filename,
            "file_url": file_url,
            "file_type": content_type,
            "file_size": file_size,
            "object_key": object_key,
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )


@router.post("/upload/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload user avatar."""
    # Validate image type
    allowed_image_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    content_type = file.content_type or ""
    
    if content_type not in allowed_image_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar must be an image (JPEG, PNG, GIF, or WebP)",
        )
    
    # Read file
    file_content = await file.read()
    file_size = len(file_content)
    
    # Limit avatar size to 5MB
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar file too large. Maximum size is 5MB",
        )
    
    # Generate filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    object_key = f"avatars/{current_user.id}/{unique_filename}"
    
    try:
        async with get_s3_client() as s3:
            await s3.put_object(
                Bucket=settings.MINIO_BUCKET_NAME,
                Key=object_key,
                Body=file_content,
                ContentType=content_type,
            )
        
        file_url = f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{object_key}"
        
        return {
            "avatar_url": file_url,
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}",
        )


@router.delete("/{object_key:path}")
async def delete_file(
    object_key: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a file from storage."""
    # Verify ownership (file should be in user's folder)
    if f"/{current_user.id}/" not in object_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own files",
        )
    
    try:
        async with get_s3_client() as s3:
            await s3.delete_object(
                Bucket=settings.MINIO_BUCKET_NAME,
                Key=object_key,
            )
        
        return {"message": "File deleted successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}",
        )

