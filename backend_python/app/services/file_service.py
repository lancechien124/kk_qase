"""
File Service for file upload, download, and management
"""
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
import uuid
import os
from pathlib import Path

from app.core.minio import minio_client
from app.core.config import settings
from app.core.logging import logger


class FileService:
    """File service for handling file operations"""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        # Images
        'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'],
        # Documents
        'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'],
        # Archives
        'archive': ['zip', 'rar', '7z', 'tar', 'gz'],
        # Code/Config
        'code': ['json', 'xml', 'yaml', 'yml', 'properties', 'conf', 'ini'],
        # Test files
        'test': ['jmx', 'har', 'xmind'],
    }
    
    # Max file sizes (in bytes)
    MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE  # 1GB default
    
    def __init__(self):
        self.minio = minio_client
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    def _is_allowed_file(self, filename: str, allowed_types: Optional[list] = None) -> bool:
        """Check if file type is allowed"""
        ext = self._get_file_extension(filename)
        if not ext:
            return False
        
        if allowed_types:
            return ext in allowed_types
        
        # Check all allowed extensions
        for category in self.ALLOWED_EXTENSIONS.values():
            if ext in category:
                return True
        
        return False
    
    def _validate_file_size(self, file_size: int) -> None:
        """Validate file size"""
        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024)}MB"
            )
    
    def _validate_file_type(self, filename: str, allowed_types: Optional[list] = None) -> None:
        """Validate file type"""
        if not self._is_allowed_file(filename, allowed_types):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed: {self._get_file_extension(filename)}"
            )
    
    async def upload_file(
        self,
        file: UploadFile,
        folder: str,
        project_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        allowed_types: Optional[list] = None,
    ) -> dict:
        """
        Upload file to MinIO
        
        Args:
            file: UploadFile object
            folder: Folder path (e.g., "project", "organization", "system")
            project_id: Optional project ID
            organization_id: Optional organization ID
            allowed_types: Optional list of allowed file extensions
        
        Returns:
            dict with file_id, file_path, file_name, file_size
        """
        # Validate file type
        self._validate_file_type(file.filename, allowed_types)
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        self._validate_file_size(file_size)
        
        # Generate file ID and path
        file_id = str(uuid.uuid4())
        file_extension = self._get_file_extension(file.filename)
        file_name = f"{file_id}.{file_extension}" if file_extension else file_id
        
        # Build file path
        if folder == "project" and project_id:
            file_path = f"project/{project_id}/{file_name}"
        elif folder == "organization" and organization_id:
            file_path = f"organization/{organization_id}/{file_name}"
        elif folder == "system":
            file_path = f"system/{file_name}"
        else:
            file_path = f"{folder}/{file_name}"
        
        # Upload to MinIO
        try:
            minio_client.upload_file(
                file_path=file_path,
                file_data=content,
                content_type=file.content_type,
            )
            
            logger.info(f"File uploaded: {file_path}, size: {file_size}")
            
            return {
                "file_id": file_id,
                "file_path": file_path,
                "file_name": file.filename,
                "file_size": file_size,
                "content_type": file.content_type,
            }
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def download_file(self, file_path: str) -> Tuple[bytes, str, str]:
        """
        Download file from MinIO
        
        Args:
            file_path: File path in MinIO
        
        Returns:
            Tuple of (file_content, file_name, content_type)
        """
        try:
            file_data = minio_client.download_file(file_path)
            
            # Extract file name from path
            file_name = os.path.basename(file_path)
            
            # Determine content type from extension
            ext = self._get_file_extension(file_name)
            content_type = self._get_content_type(ext)
            
            return (file_data, file_name, content_type)
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_path}"
            )
    
    async def delete_file(self, file_path: str) -> None:
        """Delete file from MinIO"""
        try:
            minio_client.delete_file(file_path)
            logger.info(f"File deleted: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    async def get_file_info(self, file_path: str) -> dict:
        """Get file information"""
        try:
            files = minio_client.list_files(file_path, recursive=False)
            if files:
                file_info = files[0]
                return {
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "file_size": file_info.get("size", 0),
                    "last_modified": file_info.get("last_modified"),
                }
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get file info: {str(e)}"
            )
    
    def _get_content_type(self, extension: str) -> str:
        """Get content type from file extension"""
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'json': 'application/json',
            'xml': 'application/xml',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel',
            'xmind': 'application/x-xmind',
            'jmx': 'application/xml',
            'har': 'application/json',
        }
        return content_types.get(extension.lower(), 'application/octet-stream')
    
    async def get_presigned_url(self, file_path: str, expires_seconds: int = 3600) -> str:
        """Get presigned URL for file access"""
        try:
            from datetime import timedelta
            url = minio_client.get_presigned_url(
                file_path,
                expires=timedelta(seconds=expires_seconds)
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate presigned URL: {str(e)}"
            )

