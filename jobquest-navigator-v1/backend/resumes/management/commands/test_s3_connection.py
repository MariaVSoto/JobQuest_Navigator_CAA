"""
Management command to test S3 connection and list files in the resume bucket
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'Test S3 connection and list resume files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bucket',
            type=str,
            default='caa900resume',
            help='S3 bucket name (default: caa900resume)'
        )
        parser.add_argument(
            '--prefix',
            type=str,
            default='resumes/',
            help='S3 prefix to list files under (default: resumes/)'
        )

    def handle(self, *args, **options):
        bucket_name = options['bucket']
        prefix = options['prefix']

        self.stdout.write(f'Testing S3 connection to bucket: {bucket_name}')
        
        # Check if AWS credentials are configured
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            self.stdout.write(
                self.style.WARNING(
                    'AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.'
                )
            )
            return

        try:
            # Initialize S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            # Test bucket access
            s3_client.head_bucket(Bucket=bucket_name)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully connected to S3 bucket: {bucket_name}')
            )

            # List files in the bucket with specified prefix
            self.stdout.write(f'\nListing files under prefix: {prefix}')
            
            paginator = s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

            total_files = 0
            total_size = 0

            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        size_kb = round(obj['Size'] / 1024, 1)
                        last_modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                        
                        self.stdout.write(
                            f"  {obj['Key']:<50} {size_kb:>8} KB  {last_modified}"
                        )
                        
                        total_files += 1
                        total_size += obj['Size']

            if total_files == 0:
                self.stdout.write(
                    self.style.WARNING(f'No files found under prefix: {prefix}')
                )
            else:
                total_size_mb = round(total_size / (1024 * 1024), 2)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nTotal: {total_files} files, {total_size_mb} MB'
                    )
                )

            # Test upload capability with a small test file
            test_key = f'{prefix}test_connection.txt'
            test_content = f'JobQuest Navigator S3 test - {bucket_name}'
            
            try:
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=test_key,
                    Body=test_content.encode('utf-8'),
                    ContentType='text/plain'
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Upload test successful: {test_key}')
                )
                
                # Clean up test file
                s3_client.delete_object(Bucket=bucket_name, Key=test_key)
                self.stdout.write('✓ Test file cleaned up')
                
            except ClientError as upload_error:
                self.stdout.write(
                    self.style.ERROR(f'✗ Upload test failed: {upload_error}')
                )

        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'NoSuchBucket':
                self.stdout.write(
                    self.style.ERROR(f'✗ Bucket does not exist: {bucket_name}')
                )
            elif error_code == 'AccessDenied':
                self.stdout.write(
                    self.style.ERROR(f'✗ Access denied to bucket: {bucket_name}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ S3 error: {e}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Unexpected error: {e}')
            )