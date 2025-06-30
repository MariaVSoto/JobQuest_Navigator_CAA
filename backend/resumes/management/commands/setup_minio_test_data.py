"""
Management command to set up MinIO bucket and upload test data for JobQuest Navigator
This command works with the local MinIO service in Docker environment
"""

import io
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
import boto3
from botocore.exceptions import ClientError

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up MinIO bucket and upload test data for Docker development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bucket',
            type=str,
            default='jobquest-resumes',
            help='MinIO bucket name (default: jobquest-resumes)'
        )
        parser.add_argument(
            '--create-bucket',
            action='store_true',
            help='Create the bucket if it does not exist'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it'
        )

    def handle(self, *args, **options):
        bucket_name = options['bucket']
        create_bucket = options['create_bucket']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        # Get MinIO configuration from Django settings
        endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', 'http://localhost:9000')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', 'minioadmin')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', 'minioadmin123')
        
        self.stdout.write(f'Connecting to MinIO at: {endpoint_url}')
        self.stdout.write(f'Using bucket: {bucket_name}')

        # Initialize MinIO client
        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name='us-east-1',
                verify=False
            )
            
            # Test connection
            if not dry_run:
                s3_client.list_buckets()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Connected to MinIO at {endpoint_url}')
                )
            else:
                self.stdout.write(f'Would connect to MinIO at {endpoint_url}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to connect to MinIO: {e}')
            )
            self.stdout.write(
                'Make sure MinIO is running: docker-compose up minio'
            )
            return

        # Check if bucket exists, create if needed
        try:
            if not dry_run:
                s3_client.head_bucket(Bucket=bucket_name)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Bucket {bucket_name} exists')
                )
            else:
                self.stdout.write(f'Would check bucket: {bucket_name}')
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                if create_bucket:
                    if not dry_run:
                        try:
                            s3_client.create_bucket(Bucket=bucket_name)
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Created bucket: {bucket_name}')
                            )
                        except ClientError as create_error:
                            self.stdout.write(
                                self.style.ERROR(f'Failed to create bucket: {create_error}')
                            )
                            return
                    else:
                        self.stdout.write(f'Would create bucket: {bucket_name}')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Bucket {bucket_name} does not exist. Use --create-bucket to create it.')
                    )
                    return
            else:
                self.stdout.write(
                    self.style.ERROR(f'Error checking bucket: {e}')
                )
                return

        # Sample resume test data
        sample_files = [
            {
                'key': 'resumes/samples/software_engineer_resume.pdf',
                'content_type': 'application/pdf',
                'metadata': {
                    'title': 'Software Engineer Resume Sample',
                    'category': 'technology',
                    'experience_level': 'senior'
                }
            },
            {
                'key': 'resumes/samples/data_scientist_resume.pdf',
                'content_type': 'application/pdf',
                'metadata': {
                    'title': 'Data Scientist Resume Sample', 
                    'category': 'data_science',
                    'experience_level': 'mid'
                }
            },
            {
                'key': 'resumes/samples/product_manager_resume.pdf',
                'content_type': 'application/pdf',
                'metadata': {
                    'title': 'Product Manager Resume Sample',
                    'category': 'product',
                    'experience_level': 'senior'
                }
            }
        ]

        # Sample JSON data
        json_data = [
            {
                'key': 'resumes/data/software_engineer.json',
                'data': {
                    'name': 'Alex Chen',
                    'title': 'Senior Software Engineer',
                    'experience_years': 5,
                    'skills': ['Python', 'JavaScript', 'React', 'Django', 'AWS'],
                    'location': 'San Francisco, CA',
                    'education': 'BS Computer Science - UC Berkeley'
                }
            },
            {
                'key': 'resumes/data/data_scientist.json', 
                'data': {
                    'name': 'Maria Rodriguez',
                    'title': 'Data Scientist',
                    'experience_years': 3,
                    'skills': ['Python', 'R', 'SQL', 'Machine Learning', 'TensorFlow'],
                    'location': 'New York, NY',
                    'education': 'MS Data Science - Columbia University'
                }
            }
        ]

        def create_sample_pdf_content(title):
            """Create a simple PDF content for testing"""
            return f"""
%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 55>>stream
BT /F1 12 Tf 72 720 Td ({title} - Test Resume) Tj ET
endstream endobj
xref 0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000205 00000 n 
trailer<</Size 5/Root 1 0 R>>
startxref 290
%%EOF""".strip().encode('utf-8')

        uploaded_count = 0
        total_files = len(sample_files) + len(json_data)

        # Upload sample PDF files
        for file_info in sample_files:
            if dry_run:
                self.stdout.write(f"Would upload: {file_info['key']}")
                continue
                
            try:
                pdf_content = create_sample_pdf_content(file_info['metadata']['title'])
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=file_info['key'],
                    Body=pdf_content,
                    ContentType=file_info['content_type'],
                    Metadata=file_info['metadata']
                )
                
                uploaded_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Uploaded: {file_info["key"]}')
                )
                
            except ClientError as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to upload {file_info["key"]}: {e}')
                )

        # Upload JSON data files
        for json_file in json_data:
            if dry_run:
                self.stdout.write(f"Would upload: {json_file['key']}")
                continue
                
            try:
                json_content = json.dumps(json_file['data'], indent=2).encode('utf-8')
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=json_file['key'],
                    Body=json_content,
                    ContentType='application/json',
                    Metadata={
                        'type': 'resume_data',
                        'format': 'json'
                    }
                )
                
                uploaded_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Uploaded: {json_file["key"]}')
                )
                
            except ClientError as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to upload {json_file["key"]}: {e}')
                )

        # Upload configuration metadata
        config_data = {
            'bucket_name': bucket_name,
            'setup_date': '2024-06-28',
            'environment': 'docker_development',
            'minio_endpoint': endpoint_url,
            'total_sample_files': total_files,
            'file_structure': {
                'resumes/samples/': 'Sample PDF resume files',
                'resumes/data/': 'JSON resume data',
                'resumes/users/': 'User uploaded resumes (organized by user ID)'
            }
        }
        
        config_key = 'resumes/minio_config.json'
        
        if dry_run:
            self.stdout.write(f"Would upload: {config_key}")
        else:
            try:
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=config_key,
                    Body=json.dumps(config_data, indent=2).encode('utf-8'),
                    ContentType='application/json'
                )
                
                uploaded_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Uploaded: {config_key}')
                )
                
            except ClientError as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to upload {config_key}: {e}')
                )

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would upload {total_files + 1} files to MinIO bucket {bucket_name}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Setup complete! {uploaded_count}/{total_files + 1} files uploaded to MinIO bucket {bucket_name}'
                )
            )
            
            # Provide access information
            self.stdout.write('\n' + '='*50)
            self.stdout.write('MinIO Access Information:')
            self.stdout.write(f'Web UI: http://localhost:9001')
            self.stdout.write(f'Username: minioadmin')
            self.stdout.write(f'Password: minioadmin123')
            self.stdout.write(f'Bucket: {bucket_name}')
            self.stdout.write('='*50)