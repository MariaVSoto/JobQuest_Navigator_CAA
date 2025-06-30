# Management command to setup LocalStack S3 test data

import os
import json
import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Setup LocalStack S3 test data with sample resumes and configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-bucket',
            action='store_true',
            help='Create the S3 bucket if it does not exist',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )
        parser.add_argument(
            '--bucket-name',
            type=str,
            default=getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'jobquest-resumes'),
            help='S3 bucket name (default: jobquest-resumes)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up LocalStack S3 test data...')
        )

        # LocalStack configuration
        endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', 'http://localhost:4566')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', 'test')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', 'test')
        region = getattr(settings, 'AWS_DEFAULT_REGION', 'us-east-1')
        bucket_name = options['bucket_name']

        self.stdout.write(f"📍 LocalStack endpoint: {endpoint_url}")
        self.stdout.write(f"🪣 Bucket name: {bucket_name}")

        try:
            # Create S3 client for LocalStack
            s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
                verify=False  # Disable SSL verification for LocalStack
            )

            # Create bucket if requested
            if options['create_bucket']:
                self.create_bucket(s3_client, bucket_name, region)

            # Setup test data
            self.setup_test_data(s3_client, bucket_name, options['dry_run'])

            self.stdout.write(
                self.style.SUCCESS('✅ LocalStack S3 test data setup completed!')
            )
            self.stdout.write(
                f"🌐 LocalStack Web UI: {endpoint_url.replace('4566', '4566')}/_localstack/health"
            )
            self.stdout.write(
                f"📊 S3 Console: {endpoint_url}/_localstack/s3"
            )

        except Exception as e:
            raise CommandError(f'Failed to setup LocalStack test data: {str(e)}')

    def create_bucket(self, s3_client, bucket_name, region):
        """Create S3 bucket in LocalStack"""
        try:
            # Check if bucket exists
            s3_client.head_bucket(Bucket=bucket_name)
            self.stdout.write(f"✅ Bucket '{bucket_name}' already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket doesn't exist, create it
                try:
                    if region == 'us-east-1':
                        s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': region}
                        )
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Created bucket: {bucket_name}")
                    )
                except ClientError as create_error:
                    raise CommandError(f"Failed to create bucket: {create_error}")
            else:
                raise CommandError(f"Error checking bucket: {e}")

    def setup_test_data(self, s3_client, bucket_name, dry_run=False):
        """Upload test data to LocalStack S3"""
        
        # Sample resume data
        test_files = [
            {
                'key': 'resumes/samples/software_engineer_resume.pdf',
                'content': self.generate_sample_pdf_content('Software Engineer'),
                'content_type': 'application/pdf'
            },
            {
                'key': 'resumes/samples/data_scientist_resume.pdf', 
                'content': self.generate_sample_pdf_content('Data Scientist'),
                'content_type': 'application/pdf'
            },
            {
                'key': 'resumes/samples/product_manager_resume.pdf',
                'content': self.generate_sample_pdf_content('Product Manager'),
                'content_type': 'application/pdf'
            },
            {
                'key': 'resumes/data/software_engineer.json',
                'content': json.dumps({
                    'name': 'John Doe',
                    'title': 'Software Engineer',
                    'skills': ['Python', 'Django', 'React', 'AWS'],
                    'experience': [
                        {
                            'company': 'Tech Corp',
                            'position': 'Senior Software Engineer',
                            'duration': '2020-2023',
                            'description': 'Developed web applications using Django and React'
                        }
                    ]
                }, indent=2),
                'content_type': 'application/json'
            },
            {
                'key': 'resumes/data/data_scientist.json',
                'content': json.dumps({
                    'name': 'Jane Smith',
                    'title': 'Data Scientist',
                    'skills': ['Python', 'Machine Learning', 'TensorFlow', 'SQL'],
                    'experience': [
                        {
                            'company': 'AI Solutions',
                            'position': 'Senior Data Scientist',
                            'duration': '2019-2023',
                            'description': 'Built ML models for predictive analytics'
                        }
                    ]
                }, indent=2),
                'content_type': 'application/json'
            },
            {
                'key': 'resumes/localstack_config.json',
                'content': json.dumps({
                    'version': '1.0',
                    'environment': 'localstack',
                    'bucket_name': bucket_name,
                    'created_at': '2024-06-28',
                    'sample_files_count': 5,
                    'test_users': [
                        {'id': 1, 'name': 'John Doe'},
                        {'id': 2, 'name': 'Jane Smith'}
                    ]
                }, indent=2),
                'content_type': 'application/json'
            }
        ]

        # Upload files
        for file_info in test_files:
            s3_key = file_info['key']
            file_content = file_info['content']
            content_type = file_info['content_type']

            if dry_run:
                self.stdout.write(f"📄 Would upload: {s3_key}")
                continue

            try:
                # Upload to LocalStack S3
                if isinstance(file_content, str):
                    file_content = file_content.encode('utf-8')

                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=s3_key,
                    Body=file_content,
                    ContentType=content_type
                )
                self.stdout.write(f"✅ Uploaded: {s3_key}")

            except ClientError as e:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ Failed to upload {s3_key}: {e}")
                )

        if not dry_run:
            # Verify uploads
            try:
                response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='resumes/')
                if 'Contents' in response:
                    self.stdout.write(
                        self.style.SUCCESS(f"📊 Total files in bucket: {len(response['Contents'])}")
                    )
                    for obj in response['Contents']:
                        self.stdout.write(f"  📄 {obj['Key']} ({obj['Size']} bytes)")
                else:
                    self.stdout.write("📭 No files found in bucket")
            except ClientError as e:
                self.stdout.write(
                    self.style.WARNING(f"⚠️ Could not list bucket contents: {e}")
                )

    def generate_sample_pdf_content(self, job_title):
        """Generate sample PDF content (placeholder)"""
        # This is a minimal PDF content - in a real scenario, you'd use a PDF library
        return f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
({job_title} Resume - Sample) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000202 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
295
%%EOF""".encode('utf-8')