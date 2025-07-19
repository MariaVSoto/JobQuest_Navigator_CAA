# Management command to test LocalStack AWS services connection

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Test connection to LocalStack AWS services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--service',
            type=str,
            choices=['s3', 'lambda', 'apigateway', 'all'],
            default='all',
            help='Which LocalStack service to test (default: all)',
        )
        parser.add_argument(
            '--bucket-name',
            type=str,
            default=getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'jobquest-resumes'),
            help='S3 bucket name to test (default: jobquest-resumes)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Testing LocalStack AWS services connection...')
        )

        # LocalStack configuration
        endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', 'http://localhost:4566')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', 'test')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', 'test')
        region = getattr(settings, 'AWS_DEFAULT_REGION', 'us-east-1')

        self.stdout.write(f"📍 LocalStack endpoint: {endpoint_url}")
        self.stdout.write(f"🔑 Access key: {access_key}")
        self.stdout.write(f"🌍 Region: {region}")

        service = options['service']
        
        if service == 'all' or service == 's3':
            self.test_s3_connection(endpoint_url, access_key, secret_key, region, options['bucket_name'])
        
        if service == 'all' or service == 'lambda':
            self.test_lambda_connection(endpoint_url, access_key, secret_key, region)
            
        if service == 'all' or service == 'apigateway':
            self.test_apigateway_connection(endpoint_url, access_key, secret_key, region)

        self.stdout.write(
            self.style.SUCCESS('✅ LocalStack connection tests completed!')
        )

    def test_s3_connection(self, endpoint_url, access_key, secret_key, region, bucket_name):
        """Test S3 service connection"""
        self.stdout.write('\n📦 Testing S3 service...')
        
        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
                verify=False
            )

            # Test basic S3 operations
            try:
                # List buckets
                response = s3_client.list_buckets()
                self.stdout.write(f"✅ S3 connection successful")
                self.stdout.write(f"📊 Found {len(response['Buckets'])} buckets:")
                for bucket in response['Buckets']:
                    self.stdout.write(f"  🪣 {bucket['Name']} (created: {bucket['CreationDate']})")

                # Test specific bucket if it exists
                try:
                    s3_client.head_bucket(Bucket=bucket_name)
                    self.stdout.write(f"✅ Bucket '{bucket_name}' exists and is accessible")
                    
                    # List objects in bucket
                    try:
                        response = s3_client.list_objects_v2(Bucket=bucket_name)
                        if 'Contents' in response:
                            self.stdout.write(f"📄 Found {len(response['Contents'])} objects in bucket:")
                            for obj in response['Contents'][:5]:  # Show first 5 objects
                                self.stdout.write(f"  📄 {obj['Key']} ({obj['Size']} bytes)")
                            if len(response['Contents']) > 5:
                                self.stdout.write(f"  ... and {len(response['Contents']) - 5} more objects")
                        else:
                            self.stdout.write(f"📭 Bucket '{bucket_name}' is empty")
                    except ClientError as e:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️ Could not list objects in bucket: {e}")
                        )

                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        self.stdout.write(
                            self.style.WARNING(f"⚠️ Bucket '{bucket_name}' does not exist")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️ Error accessing bucket: {e}")
                        )

            except ClientError as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ S3 operation failed: {e}")
                )

        except NoCredentialsError:
            self.stdout.write(
                self.style.ERROR('❌ AWS credentials not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ S3 connection failed: {e}')
            )

    def test_lambda_connection(self, endpoint_url, access_key, secret_key, region):
        """Test Lambda service connection"""
        self.stdout.write('\n🔧 Testing Lambda service...')
        
        try:
            lambda_client = boto3.client(
                'lambda',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
                verify=False
            )

            # List functions
            response = lambda_client.list_functions()
            self.stdout.write(f"✅ Lambda connection successful")
            self.stdout.write(f"🔧 Found {len(response['Functions'])} Lambda functions:")
            for func in response['Functions']:
                self.stdout.write(f"  ⚡ {func['FunctionName']} (runtime: {func['Runtime']})")

        except ClientError as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ Lambda operation failed: {e}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Lambda connection failed: {e}')
            )

    def test_apigateway_connection(self, endpoint_url, access_key, secret_key, region):
        """Test API Gateway service connection"""
        self.stdout.write('\n🌐 Testing API Gateway service...')
        
        try:
            apigateway_client = boto3.client(
                'apigateway',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
                verify=False
            )

            # List REST APIs
            response = apigateway_client.get_rest_apis()
            self.stdout.write(f"✅ API Gateway connection successful")
            self.stdout.write(f"🌐 Found {len(response['items'])} REST APIs:")
            for api in response['items']:
                self.stdout.write(f"  🔗 {api['name']} (id: {api['id']})")

        except ClientError as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ API Gateway operation failed: {e}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ API Gateway connection failed: {e}')
            )