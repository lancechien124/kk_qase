"""
File Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FileUploadResponse(BaseModel):
    """File upload response"""
    file_id: str
    file_path: str
    file_name: str
    file_size: int
    content_type: Optional[str] = None


class FileInfoResponse(BaseModel):
    """File information response"""
    file_path: str
    file_name: str
    file_size: int
    last_modified: Optional[datetime] = None


class FileDownloadRequest(BaseModel):
    """File download request"""
    file_path: str


class FileDeleteRequest(BaseModel):
    """File delete request"""
    file_paths: list[str]

