"""
Management command to upload test data to S3 for JobQuest Navigator
Uploads sample resume files and test data to s3://caa900resume/resumes/
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
    help = 'Upload test data to S3 bucket for JobQuest Navigator'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bucket',
            type=str,
            default='caa900resume',
            help='S3 bucket name (default: caa900resume)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading'
        )

    def handle(self, *args, **options):
        bucket_name = options['bucket']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No files will be uploaded')
            )

        # Initialize S3 client
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Test S3 connection
            if not dry_run:
                s3_client.head_bucket(Bucket=bucket_name)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Connected to S3 bucket: {bucket_name}')
                )
            else:
                self.stdout.write(f'Would connect to S3 bucket: {bucket_name}')
                
        except ClientError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to connect to S3: {e}')
            )
            return

        # Sample resume data
        sample_resumes = [
            {
                'filename': 'sample_software_engineer_resume.pdf',
                'title': 'Software Engineer Resume',
                'content_type': 'application/pdf',
                'description': 'Sample resume for software engineering positions'
            },
            {
                'filename': 'sample_data_scientist_resume.pdf', 
                'title': 'Data Scientist Resume',
                'content_type': 'application/pdf',
                'description': 'Sample resume for data science positions'
            },
            {
                'filename': 'sample_product_manager_resume.pdf',
                'title': 'Product Manager Resume', 
                'content_type': 'application/pdf',
                'description': 'Sample resume for product management positions'
            },
            {
                'filename': 'sample_marketing_resume.pdf',
                'title': 'Marketing Specialist Resume',
                'content_type': 'application/pdf', 
                'description': 'Sample resume for marketing positions'
            }
        ]

        # Sample JSON resume data
        sample_json_data = [
            {
                'filename': 'software_engineer_data.json',
                'data': {
                    'personal_info': {
                        'name': 'John Smith',
                        'email': 'john.smith@example.com',
                        'phone': '+1-555-0123',
                        'location': 'San Francisco, CA'
                    },
                    'summary': 'Experienced software engineer with 5+ years developing scalable web applications.',
                    'experience': [
                        {
                            'title': 'Senior Software Engineer',
                            'company': 'TechCorp Inc.',
                            'duration': '2021 - Present',
                            'description': 'Led development of microservices architecture serving 1M+ users'
                        }
                    ],
                    'skills': ['Python', 'JavaScript', 'React', 'Django', 'AWS', 'Docker'],
                    'education': [
                        {
                            'degree': 'Bachelor of Science in Computer Science',
                            'school': 'Stanford University',
                            'year': '2018'
                        }
                    ]
                }
            },
            {
                'filename': 'data_scientist_data.json',
                'data': {
                    'personal_info': {
                        'name': 'Sarah Johnson',
                        'email': 'sarah.johnson@example.com',
                        'phone': '+1-555-0456',
                        'location': 'New York, NY'
                    },
                    'summary': 'Data scientist with expertise in machine learning and statistical analysis.',
                    'experience': [
                        {
                            'title': 'Data Scientist',
                            'company': 'Analytics Corp',
                            'duration': '2020 - Present',
                            'description': 'Built predictive models increasing revenue by 20%'
                        }
                    ],
                    'skills': ['Python', 'R', 'SQL', 'TensorFlow', 'Pandas', 'Scikit-learn'],
                    'education': [
                        {
                            'degree': 'Master of Science in Data Science',
                            'school': 'MIT',
                            'year': '2020'
                        }
                    ]
                }
            }
        ]

        # Create sample PDF content (placeholder)
        def create_sample_pdf_content(title):
            return f"""
%PDF-1.4
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
72 720 Td
({title}) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000205 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF
""".strip().encode('utf-8')

        uploaded_count = 0
        total_files = len(sample_resumes) + len(sample_json_data)

        # Upload sample PDF resumes
        for resume in sample_resumes:
            s3_key = f"resumes/{resume['filename']}"
            
            if dry_run:
                self.stdout.write(f"Would upload: {s3_key}")
                continue
                
            try:
                pdf_content = create_sample_pdf_content(resume['title'])
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=s3_key,
                    Body=pdf_content,
                    ContentType=resume['content_type'],
                    Metadata={
                        'title': resume['title'],
                        'description': resume['description'],
                        'uploaded_by': 'jobquest_test_data'
                    }
                )
                
                uploaded_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Uploaded: {s3_key}')
                )
                
            except ClientError as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to upload {s3_key}: {e}')
                )

        # Upload sample JSON data
        for json_file in sample_json_data:
            s3_key = f"resumes/data/{json_file['filename']}"
            
            if dry_run:
                self.stdout.write(f"Would upload: {s3_key}")
                continue
                
            try:
                json_content = json.dumps(json_file['data'], indent=2).encode('utf-8')
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=s3_key,
                    Body=json_content,
                    ContentType='application/json',
                    Metadata={
                        'type': 'resume_data',
                        'uploaded_by': 'jobquest_test_data'
                    }
                )
                
                uploaded_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Uploaded: {s3_key}')
                )
                
            except ClientError as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to upload {s3_key}: {e}')
                )

        # Upload metadata file
        metadata = {
            'bucket': bucket_name,
            'upload_date': '2024-06-28',
            'total_files': total_files,
            'file_types': ['PDF resumes', 'JSON data'],
            'purpose': 'JobQuest Navigator test data',
            'resumes': [r['filename'] for r in sample_resumes],
            'data_files': [j['filename'] for j in sample_json_data]
        }
        
        metadata_key = 'resumes/metadata.json'
        
        if dry_run:
            self.stdout.write(f"Would upload: {metadata_key}")
        else:
            try:
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=metadata_key,
                    Body=json.dumps(metadata, indent=2).encode('utf-8'),
                    ContentType='application/json'
                )
                
                uploaded_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Uploaded: {metadata_key}')
                )
                
            except ClientError as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to upload {metadata_key}: {e}')
                )

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would upload {total_files + 1} files to s3://{bucket_name}/resumes/')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Upload complete! {uploaded_count}/{total_files + 1} files uploaded to s3://{bucket_name}/resumes/'
                )
            )
            
        # List uploaded files
        if not dry_run:
            self.stdout.write('\nUploaded files:')
            try:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix='resumes/'
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        size_kb = round(obj['Size'] / 1024, 1)
                        self.stdout.write(f"  - {obj['Key']} ({size_kb} KB)")
                else:
                    self.stdout.write("  No files found in resumes/ directory")
                    
            except ClientError as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to list files: {e}')
                )