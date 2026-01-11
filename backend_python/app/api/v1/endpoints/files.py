"""
File Management Endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse, Response
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.file_service import FileService
from app.schemas.file import FileUploadResponse, FileInfoResponse

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "system",
    project_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    allowed_types: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload file"""
    file_service = FileService()
    
    result = await file_service.upload_file(
        file=file,
        folder=folder,
        project_id=project_id,
        organization_id=organization_id,
        allowed_types=allowed_types,
    )
    
    return FileUploadResponse(**result)


@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download file"""
    file_service = FileService()
    
    file_data, file_name, content_type = await file_service.download_file(file_path)
    
    return Response(
        content=file_data,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{file_name}"',
        }
    )


@router.get("/info/{file_path:path}", response_model=FileInfoResponse)
async def get_file_info(
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get file information"""
    file_service = FileService()
    
    info = await file_service.get_file_info(file_path)
    return FileInfoResponse(**info)


@router.delete("/delete/{file_path:path}")
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete file"""
    file_service = FileService()
    
    await file_service.delete_file(file_path)
    return {"message": "File deleted successfully"}


@router.get("/presigned-url/{file_path:path}")
async def get_presigned_url(
    file_path: str,
    expires: int = 3600,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get presigned URL for file access"""
    file_service = FileService()
    
    url = await file_service.get_presigned_url(file_path, expires)
    return {"url": url, "expires": expires}

