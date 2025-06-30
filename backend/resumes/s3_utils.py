"""
S3 utility functions for resume file operations in JobQuest Navigator
"""

import os
import uuid
from typing import Optional, Dict, Any
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import boto3
from botocore.exceptions import ClientError


class S3ResumeManager:
    """Manager class for S3 resume file operations"""
    
    def __init__(self):
        self.bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'caa900resume')
        self.resume_path = getattr(settings, 'RESUME_STORAGE_PATH', 'resumes/')
        
        if hasattr(settings, 'AWS_ACCESS_KEY_ID') and settings.AWS_ACCESS_KEY_ID:
            # Check if using MinIO (has endpoint URL) or real AWS S3
            endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
            verify_ssl = getattr(settings, 'AWS_S3_VERIFY', True)
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
                endpoint_url=endpoint_url,  # For MinIO
                verify=verify_ssl  # Disable for local MinIO
            )
            
            self.is_minio = endpoint_url is not None
        else:
            self.s3_client = None
            self.is_minio = False

    def upload_resume(self, file_content: bytes, original_filename: str, 
                     user_id: Optional[int] = None, content_type: str = 'application/pdf') -> str:
        """
        Upload a resume file to S3
        
        Args:
            file_content: The file content as bytes
            original_filename: Original filename
            user_id: ID of the user uploading the file
            content_type: MIME type of the file
            
        Returns:
            The S3 key (path) of the uploaded file
        """
        # Generate unique filename
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create S3 key with user folder structure
        if user_id:
            s3_key = f"{self.resume_path}users/{user_id}/{unique_filename}"
        else:
            s3_key = f"{self.resume_path}uploads/{unique_filename}"
        
        try:
            if self.s3_client:
                # Upload directly to S3
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_content,
                    ContentType=content_type,
                    Metadata={
                        'original_filename': original_filename,
                        'user_id': str(user_id) if user_id else 'anonymous',
                        'upload_source': 'jobquest_navigator'
                    }
                )
            else:
                # Fallback to default storage (local or configured storage backend)
                file_obj = ContentFile(file_content, name=unique_filename)
                s3_key = default_storage.save(s3_key, file_obj)
                
            return s3_key
            
        except ClientError as e:
            raise Exception(f"Failed to upload resume to S3: {e}")

    def download_resume(self, s3_key: str) -> bytes:
        """
        Download a resume file from S3
        
        Args:
            s3_key: The S3 key (path) of the file
            
        Returns:
            The file content as bytes
        """
        try:
            if self.s3_client:
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
                return response['Body'].read()
            else:
                # Fallback to default storage
                with default_storage.open(s3_key, 'rb') as file:
                    return file.read()
                    
        except ClientError as e:
            raise Exception(f"Failed to download resume from S3: {e}")

    def delete_resume(self, s3_key: str) -> bool:
        """
        Delete a resume file from S3
        
        Args:
            s3_key: The S3 key (path) of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.s3_client:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            else:
                default_storage.delete(s3_key)
            return True
            
        except ClientError as e:
            print(f"Failed to delete resume from S3: {e}")
            return False

    def get_resume_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for resume access
        
        Args:
            s3_key: The S3 key (path) of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL for the file
        """
        try:
            if self.s3_client:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': s3_key},
                    ExpiresIn=expiration
                )
                return url
            else:
                # Fallback to default storage URL
                return default_storage.url(s3_key)
                
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {e}")

    def list_user_resumes(self, user_id: int) -> list:
        """
        List all resumes for a specific user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of resume file information
        """
        try:
            prefix = f"{self.resume_path}users/{user_id}/"
            resumes = []
            
            if self.s3_client:
                paginator = self.s3_client.get_paginator('list_objects_v2')
                pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
                
                for page in pages:
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            # Get object metadata
                            try:
                                metadata_response = self.s3_client.head_object(
                                    Bucket=self.bucket_name, 
                                    Key=obj['Key']
                                )
                                metadata = metadata_response.get('Metadata', {})
                                
                                resumes.append({
                                    's3_key': obj['Key'],
                                    'filename': os.path.basename(obj['Key']),
                                    'original_filename': metadata.get('original_filename', ''),
                                    'size': obj['Size'],
                                    'last_modified': obj['LastModified'],
                                    'content_type': metadata_response.get('ContentType', ''),
                                })
                            except ClientError:
                                # Skip files we can't access
                                continue
            
            return resumes
            
        except ClientError as e:
            print(f"Failed to list user resumes: {e}")
            return []

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics for the resume bucket
        
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'user_folders': 0
        }
        
        try:
            if self.s3_client:
                paginator = self.s3_client.get_paginator('list_objects_v2')
                pages = paginator.paginate(Bucket=self.bucket_name, Prefix=self.resume_path)
                
                user_ids = set()
                
                for page in pages:
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            stats['total_files'] += 1
                            stats['total_size'] += obj['Size']
                            
                            # Count file types
                            ext = os.path.splitext(obj['Key'])[1].lower()
                            stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                            
                            # Count unique users
                            if '/users/' in obj['Key']:
                                parts = obj['Key'].split('/users/')
                                if len(parts) > 1:
                                    user_id = parts[1].split('/')[0]
                                    user_ids.add(user_id)
                
                stats['user_folders'] = len(user_ids)
                stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
            
        except ClientError as e:
            print(f"Failed to get storage stats: {e}")
        
        return stats


# Global instance
resume_manager = S3ResumeManager()


def upload_resume_file(file_content: bytes, filename: str, user_id: Optional[int] = None) -> str:
    """Convenience function to upload a resume file"""
    return resume_manager.upload_resume(file_content, filename, user_id)


def get_resume_download_url(s3_key: str, expiration: int = 3600) -> str:
    """Convenience function to get a download URL for a resume"""
    return resume_manager.get_resume_url(s3_key, expiration)


def delete_resume_file(s3_key: str) -> bool:
    """Convenience function to delete a resume file"""
    return resume_manager.delete_resume(s3_key)