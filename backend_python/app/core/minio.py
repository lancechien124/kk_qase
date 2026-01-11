"""
MinIO Client for File Storage
"""
from minio import Minio
from minio.error import S3Error
from typing import Optional, BinaryIO, List
import io
from datetime import timedelta

from app.core.config import settings
from app.core.logging import logger


class MinIOClient:
    """MinIO client wrapper"""
    
    def __init__(self):
        self._client: Optional[Minio] = None
        self.bucket = settings.MINIO_BUCKET
    
    def get_client(self) -> Minio:
        """Get or create MinIO client"""
        if self._client is None:
            self._client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            # Ensure bucket exists
            self._ensure_bucket()
        return self._client
    
    def _ensure_bucket(self):
        """Ensure bucket exists, create if not"""
        try:
            client = self.get_client()
            if not client.bucket_exists(self.bucket):
                client.make_bucket(self.bucket)
                logger.info(f"Created MinIO bucket: {self.bucket}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def upload_file(
        self,
        file_path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """Upload file to MinIO
        
        Args:
            file_path: Path in bucket (e.g., "project/123/file.txt")
            file_data: File content as bytes
            content_type: MIME type (e.g., "application/json")
            metadata: Optional metadata dict
        
        Returns:
            File path in bucket
        """
        try:
            client = self.get_client()
            file_stream = io.BytesIO(file_data)
            file_size = len(file_data)
            
            client.put_object(
                bucket_name=self.bucket,
                object_name=file_path,
                data=file_stream,
                length=file_size,
                content_type=content_type or "application/octet-stream",
                metadata=metadata
            )
            logger.info(f"Uploaded file to MinIO: {file_path}")
            return file_path
        except S3Error as e:
            logger.error(f"Error uploading file to MinIO: {e}")
            raise
    
    def download_file(self, file_path: str) -> bytes:
        """Download file from MinIO
        
        Args:
            file_path: Path in bucket
        
        Returns:
            File content as bytes
        """
        try:
            client = self.get_client()
            response = client.get_object(self.bucket, file_path)
            file_data = response.read()
            response.close()
            response.release_conn()
            logger.info(f"Downloaded file from MinIO: {file_path}")
            return file_data
        except S3Error as e:
            logger.error(f"Error downloading file from MinIO: {e}")
            raise
    
    def delete_file(self, file_path: str):
        """Delete file from MinIO
        
        Args:
            file_path: Path in bucket
        """
        try:
            client = self.get_client()
            client.remove_object(self.bucket, file_path)
            logger.info(f"Deleted file from MinIO: {file_path}")
        except S3Error as e:
            logger.error(f"Error deleting file from MinIO: {e}")
            raise
    
    def delete_folder(self, folder_path: str):
        """Delete folder (all objects with prefix) from MinIO
        
        Args:
            folder_path: Folder path in bucket
        """
        try:
            client = self.get_client()
            objects = client.list_objects(
                self.bucket,
                prefix=folder_path,
                recursive=True
            )
            for obj in objects:
                client.remove_object(self.bucket, obj.object_name)
            logger.info(f"Deleted folder from MinIO: {folder_path}")
        except S3Error as e:
            logger.error(f"Error deleting folder from MinIO: {e}")
            raise
    
    def list_files(
        self,
        folder_path: str = "",
        recursive: bool = True
    ) -> List[dict]:
        """List files in folder
        
        Args:
            folder_path: Folder path in bucket
            recursive: Whether to list recursively
        
        Returns:
            List of file info dicts with keys: name, size, last_modified
        """
        try:
            client = self.get_client()
            objects = client.list_objects(
                self.bucket,
                prefix=folder_path,
                recursive=recursive
            )
            files = []
            for obj in objects:
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                })
            return files
        except S3Error as e:
            logger.error(f"Error listing files from MinIO: {e}")
            raise
    
    def get_presigned_url(
        self,
        file_path: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """Get presigned URL for file access
        
        Args:
            file_path: Path in bucket
            expires: URL expiration time
        
        Returns:
            Presigned URL
        """
        try:
            client = self.get_client()
            url = client.presigned_get_object(
                self.bucket,
                file_path,
                expires=expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists
        
        Args:
            file_path: Path in bucket
        
        Returns:
            True if file exists, False otherwise
        """
        try:
            client = self.get_client()
            client.stat_object(self.bucket, file_path)
            return True
        except S3Error:
            return False
    
    def copy_file(self, source_path: str, target_path: str):
        """Copy file within bucket
        
        Args:
            source_path: Source file path
            target_path: Target file path
        """
        try:
            client = self.get_client()
            from minio.commonconfig import CopySource
            client.copy_object(
                self.bucket,
                target_path,
                CopySource(self.bucket, source_path)
            )
            logger.info(f"Copied file in MinIO: {source_path} -> {target_path}")
        except S3Error as e:
            logger.error(f"Error copying file in MinIO: {e}")
            raise


# Global MinIO client instance
minio_client = MinIOClient()


# Dependency for FastAPI
def get_minio() -> MinIOClient:
    """Get MinIO client dependency"""
    return minio_client

