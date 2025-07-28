"""
Storage service for handling file uploads to MinIO/S3
Provides abstraction layer for different storage backends
"""

import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, BinaryIO, Tuple
from minio import Minio
from minio.error import S3Error, MinioException
import magic

logger = logging.getLogger(__name__)


class StorageService:
    """
    Storage service for handling file operations
    Supports MinIO (development) and S3 (production)
    """
    
    def __init__(self):
        self.endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        self.secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')
        self.secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
        self.bucket_name = os.getenv('MINIO_BUCKET_NAME', 'jobquest-resumes')
        
        # Initialize MinIO client
        try:
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            logger.info(f"MinIO client initialized with endpoint: {self.endpoint}")
            self._ensure_bucket_exists()
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            self.client = None
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def upload_resume_file(
        self, 
        user_id: str, 
        file_data: BinaryIO, 
        filename: str,
        content_type: Optional[str] = None
    ) -> Tuple[str, dict]:
        """
        Upload resume file to storage
        
        Args:
            user_id: User ID for organizing files
            file_data: File binary data
            filename: Original filename
            content_type: MIME type of the file
        
        Returns:
            Tuple of (file_path, file_metadata)
        """
        if not self.client:
            raise Exception("Storage client not initialized")
        
        try:
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"resumes/users/{user_id}/{unique_filename}"
            
            # Detect content type if not provided
            if not content_type:
                content_type = self._detect_content_type(file_data, filename)
            
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Reset to beginning
            
            # Validate file
            self._validate_resume_file(file_size, content_type, filename)
            
            # Upload file
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                data=file_data,
                length=file_size,
                content_type=content_type,
                metadata={
                    'original-filename': filename,
                    'user-id': user_id,
                    'upload-timestamp': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"File uploaded successfully: {file_path}")
            
            # Return file path and metadata
            file_metadata = {
                'file_path': file_path,
                'original_filename': filename,
                'file_size': file_size,
                'content_type': content_type,
                'upload_timestamp': datetime.utcnow().isoformat()
            }
            
            return file_path, file_metadata
            
        except S3Error as e:
            logger.error(f"MinIO error uploading file: {e}")
            raise Exception(f"Storage error: {e}")
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        Get pre-signed URL for file access
        
        Args:
            file_path: Path to file in storage
            expires_in: URL expiration time in seconds (default 1 hour)
        
        Returns:
            Pre-signed URL for file access
        """
        if not self.client:
            raise Exception("Storage client not initialized")
        
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                expires=timedelta(seconds=expires_in)
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating file URL: {e}")
            raise Exception(f"Storage error: {e}")
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage
        
        Args:
            file_path: Path to file in storage
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            raise Exception("Storage client not initialized")
        
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=file_path
            )
            logger.info(f"File deleted successfully: {file_path}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get file metadata from storage
        
        Args:
            file_path: Path to file in storage
        
        Returns:
            Dictionary with file metadata
        """
        if not self.client:
            raise Exception("Storage client not initialized")
        
        try:
            stat = self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=file_path
            )
            
            return {
                'file_path': file_path,
                'size': stat.size,
                'content_type': stat.content_type,
                'last_modified': stat.last_modified,
                'etag': stat.etag,
                'metadata': stat.metadata
            }
        except S3Error as e:
            logger.error(f"Error getting file info: {e}")
            raise Exception(f"Storage error: {e}")
    
    def download_file(self, file_path: str) -> BinaryIO:
        """
        Download file from storage
        
        Args:
            file_path: Path to file in storage
        
        Returns:
            File binary data stream
        """
        if not self.client:
            raise Exception("Storage client not initialized")
        
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=file_path
            )
            return response
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            raise Exception(f"Storage error: {e}")
    
    def _detect_content_type(self, file_data: BinaryIO, filename: str) -> str:
        """Detect MIME type of file"""
        try:
            # Try to use python-magic for better detection
            file_data.seek(0)
            file_sample = file_data.read(1024)
            file_data.seek(0)
            
            mime_type = magic.from_buffer(file_sample, mime=True)
            return mime_type
        except:
            # Fallback to extension-based detection
            ext = os.path.splitext(filename)[1].lower()
            mime_map = {
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            return mime_map.get(ext, 'application/octet-stream')
    
    def _validate_resume_file(self, file_size: int, content_type: str, filename: str):
        """Validate uploaded resume file"""
        # File size validation (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise Exception(f"File too large. Maximum size is {max_size / (1024*1024):.1f}MB")
        
        # Content type validation
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        
        if content_type not in allowed_types:
            raise Exception(f"File type not allowed. Supported types: PDF, DOC, DOCX")
        
        # File extension validation
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise Exception(f"File extension not allowed. Supported extensions: {', '.join(allowed_extensions)}")
    
    def health_check(self) -> dict:
        """Check storage service health"""
        try:
            if not self.client:
                return {'status': 'unhealthy', 'error': 'Client not initialized'}
            
            # Try to list objects in bucket (should not fail even if empty)
            list(self.client.list_objects(self.bucket_name, max_keys=1))
            
            return {
                'status': 'healthy',
                'endpoint': self.endpoint,
                'bucket': self.bucket_name,
                'secure': self.secure
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'endpoint': self.endpoint
            }


# Singleton instance
storage_service = StorageService()