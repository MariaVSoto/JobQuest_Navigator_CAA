import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def upload_file(self, file_obj, s3_key):
        try:
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, s3_key)
            return True
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            return False

    def download_file(self, s3_key):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            return None

    def delete_file(self, s3_key):
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False
