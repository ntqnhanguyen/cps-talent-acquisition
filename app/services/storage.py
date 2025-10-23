"""MinIO storage service."""
import io
import logging
from typing import BinaryIO
from minio import Minio
from minio.error import S3Error
from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for handling file storage with MinIO."""
    
    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self.bucket_name = settings.minio_bucket
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if not."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    async def upload_file(self, file_content: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
        """
        Upload a file to MinIO.
        
        Args:
            file_content: File content as bytes
            object_name: Name of the object in storage
            content_type: MIME type of the file
            
        Returns:
            URL of the uploaded file
        """
        try:
            file_stream = io.BytesIO(file_content)
            file_size = len(file_content)
            
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_stream,
                file_size,
                content_type=content_type
            )
            
            # Generate URL
            url = f"http://{settings.minio_endpoint}/{self.bucket_name}/{object_name}"
            logger.info(f"Uploaded file: {object_name}")
            return url
            
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    async def download_file(self, object_name: str) -> bytes:
        """
        Download a file from MinIO.
        
        Args:
            object_name: Name of the object in storage
            
        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            content = response.read()
            response.close()
            response.release_conn()
            return content
            
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            raise
    
    async def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from MinIO.
        
        Args:
            object_name: Name of the object in storage
            
        Returns:
            True if successful
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Deleted file: {object_name}")
            return True
            
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            raise


# Singleton instance
storage_service = StorageService()

