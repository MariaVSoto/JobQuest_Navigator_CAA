"""
Storage service for handling file uploads to MinIO/S3
Provides abstraction layer for different storage backends
Supports environment-based switching: MinIO (dev) -> S3 (prod)
"""

import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, BinaryIO, Tuple
from minio import Minio
from minio.error import S3Error, MinioException
import magic
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class StorageService:
    """
    Storage service for handling file operations
    Supports MinIO (development) and S3 (production) with environment-based switching
    """
    
    def __init__(self):
        # Determine storage backend based on environment
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.use_s3 = self.environment.lower() in ['production', 'staging']
        
        # Common settings
        self.bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME', 'jobquest-resumes')
        
        if self.use_s3:
            self._initialize_s3()
        else:
            self._initialize_minio()
    
    def _initialize_s3(self):
        """Initialize AWS S3 client for production/staging"""
        try:
            self.aws_region = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
            self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
            self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            
            if not self.access_key or not self.secret_key:
                raise Exception("AWS credentials not provided")
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.aws_region
            )
            
            self.client_type = 's3'
            logger.info(f"S3 client initialized for {self.environment} environment")
            self._ensure_bucket_exists()
            
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None
            
    def _initialize_minio(self):
        """Initialize MinIO client for development"""
        try:
            self.endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
            self.access_key = os.getenv('MINIO_ACCESS_KEY', '')
            self.secret_key = os.getenv('MINIO_SECRET_KEY', '')
            
            # Validate MinIO credentials
            if not self.access_key or not self.secret_key:
                if self.environment == 'production':
                    raise ValueError("MINIO_ACCESS_KEY and MINIO_SECRET_KEY are required for MinIO storage")
                else:
                    # Use development defaults only for non-production
                    self.access_key = self.access_key or 'dev-minio-user'
                    self.secret_key = self.secret_key or 'dev-minio-password'
            self.secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
            
            self.minio_client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            
            self.client_type = 'minio'
            logger.info(f"MinIO client initialized for {self.environment} environment with endpoint: {self.endpoint}")
            self._ensure_bucket_exists()
            
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            self.minio_client = None
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if self.use_s3:
                # Check S3 bucket
                try:
                    self.s3_client.head_bucket(Bucket=self.bucket_name)
                    logger.info(f"S3 bucket exists: {self.bucket_name}")
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        # Bucket doesn't exist, create it
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                        logger.info(f"Created S3 bucket: {self.bucket_name}")
                    else:
                        raise
            else:
                # Check MinIO bucket
                if not self.minio_client.bucket_exists(self.bucket_name):
                    self.minio_client.make_bucket(self.bucket_name)
                    logger.info(f"Created MinIO bucket: {self.bucket_name}")
                else:
                    logger.info(f"MinIO bucket exists: {self.bucket_name}")
        except Exception as e:
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
        if (self.use_s3 and not hasattr(self, 's3_client')) or (not self.use_s3 and not hasattr(self, 'minio_client')):
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
            
            # Upload file based on backend
            if self.use_s3:
                # Upload to S3
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=file_path,
                    Body=file_data,
                    ContentType=content_type,
                    Metadata={
                        'original-filename': filename,
                        'user-id': user_id,
                        'upload-timestamp': datetime.utcnow().isoformat()
                    }
                )
            else:
                # Upload to MinIO
                self.minio_client.put_object(
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
            
            logger.info(f"File uploaded successfully to {self.client_type}: {file_path}")
            
            # Return file path and metadata
            file_metadata = {
                'file_path': file_path,
                'original_filename': filename,
                'file_size': file_size,
                'content_type': content_type,
                'upload_timestamp': datetime.utcnow().isoformat()
            }
            
            return file_path, file_metadata
            
        except (S3Error, ClientError) as e:
            logger.error(f"{self.client_type.upper()} error uploading file: {e}")
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
        if (self.use_s3 and not hasattr(self, 's3_client')) or (not self.use_s3 and not hasattr(self, 'minio_client')):
            raise Exception("Storage client not initialized")
        
        try:
            if self.use_s3:
                # Generate S3 pre-signed URL
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_path},
                    ExpiresIn=expires_in
                )
            else:
                # Generate MinIO pre-signed URL
                url = self.minio_client.presigned_get_object(
                    bucket_name=self.bucket_name,
                    object_name=file_path,
                    expires=timedelta(seconds=expires_in)
                )
            return url
        except (S3Error, ClientError) as e:
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
        if (self.use_s3 and not hasattr(self, 's3_client')) or (not self.use_s3 and not hasattr(self, 'minio_client')):
            raise Exception("Storage client not initialized")
        
        try:
            if self.use_s3:
                # Delete from S3
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=file_path
                )
            else:
                # Delete from MinIO
                self.minio_client.remove_object(
                    bucket_name=self.bucket_name,
                    object_name=file_path
                )
            logger.info(f"File deleted successfully from {self.client_type}: {file_path}")
            return True
        except (S3Error, ClientError) as e:
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
        if (self.use_s3 and not hasattr(self, 's3_client')) or (not self.use_s3 and not hasattr(self, 'minio_client')):
            raise Exception("Storage client not initialized")
        
        try:
            if self.use_s3:
                # Get S3 object metadata
                response = self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=file_path
                )
                return {
                    'file_path': file_path,
                    'size': response['ContentLength'],
                    'content_type': response['ContentType'],
                    'last_modified': response['LastModified'],
                    'etag': response['ETag'],
                    'metadata': response.get('Metadata', {})
                }
            else:
                # Get MinIO object metadata
                stat = self.minio_client.stat_object(
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
        except (S3Error, ClientError) as e:
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
        if (self.use_s3 and not hasattr(self, 's3_client')) or (not self.use_s3 and not hasattr(self, 'minio_client')):
            raise Exception("Storage client not initialized")
        
        try:
            if self.use_s3:
                # Download from S3
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=file_path
                )
                return response['Body']
            else:
                # Download from MinIO
                response = self.minio_client.get_object(
                    bucket_name=self.bucket_name,
                    object_name=file_path
                )
                return response
        except (S3Error, ClientError) as e:
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
            if (self.use_s3 and not hasattr(self, 's3_client')) or (not self.use_s3 and not hasattr(self, 'minio_client')):
                return {'status': 'unhealthy', 'error': 'Client not initialized'}
            
            if self.use_s3:
                # Try to list objects in S3 bucket
                self.s3_client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
                return {
                    'status': 'healthy',
                    'backend': 's3',
                    'environment': self.environment,
                    'bucket': self.bucket_name,
                    'region': self.aws_region
                }
            else:
                # Try to list objects in MinIO bucket
                # Just try to list objects - if bucket exists and is accessible, this will work
                objects = list(self.minio_client.list_objects(self.bucket_name))[:1] if self.minio_client.bucket_exists(self.bucket_name) else []
                return {
                    'status': 'healthy',
                    'backend': 'minio',
                    'environment': self.environment,
                    'endpoint': self.endpoint,
                    'bucket': self.bucket_name,
                    'secure': self.secure
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'backend': self.client_type,
                'environment': self.environment,
                'error': str(e),
                'endpoint': getattr(self, 'endpoint', 'N/A')
            }


# Singleton instance
storage_service = StorageService()