#!/usr/bin/env python3
"""
Create AWS Cognito App Client for JobQuest Navigator v2
"""

import boto3
import json
import os
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message):
    print(f"{Colors.GREEN}[INFO]{Colors.END} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.END} {message}")

def print_step(message):
    print(f"\n{Colors.BLUE}{Colors.BOLD}==== {message} ===={Colors.END}")

def create_cognito_client():
    """Create Cognito App Client"""
    
    # Configuration
    USER_POOL_ID = "us-east-1_blSZREFys"
    REGION = "us-east-1"
    CLIENT_NAME = "jobquest-navigator-v2"
    
    print_step("Creating AWS Cognito App Client")
    print_status(f"User Pool ID: {USER_POOL_ID}")
    print_status(f"Region: {REGION}")
    print_status(f"Client Name: {CLIENT_NAME}")
    
    try:
        # Initialize Cognito client
        cognito_client = boto3.client('cognito-idp', region_name=REGION)
        
        # Check if user pool exists
        print_status("Verifying user pool exists...")
        try:
            user_pool = cognito_client.describe_user_pool(UserPoolId=USER_POOL_ID)
            print_status(f"User pool found: {user_pool['UserPool']['Name']}")
        except cognito_client.exceptions.ResourceNotFoundException:
            print_error(f"User pool {USER_POOL_ID} not found")
            return None
        
        # Check for existing app clients
        print_status("Checking for existing app clients...")
        existing_clients = cognito_client.list_user_pool_clients(UserPoolId=USER_POOL_ID)
        
        for client in existing_clients['UserPoolClients']:
            if client['ClientName'] == CLIENT_NAME:
                print_warning(f"App client '{CLIENT_NAME}' already exists")
                print_status(f"Existing Client ID: {client['ClientId']}")
                
                response = input("Do you want to use the existing client? (y/n): ").lower()
                if response == 'y':
                    return client['ClientId']
                else:
                    # Delete existing client
                    cognito_client.delete_user_pool_client(
                        UserPoolId=USER_POOL_ID,
                        ClientId=client['ClientId']
                    )
                    print_status("Deleted existing client")
        
        # Create new app client
        print_status("Creating new app client...")
        
        response = cognito_client.create_user_pool_client(
            UserPoolId=USER_POOL_ID,
            ClientName=CLIENT_NAME,
            GenerateSecret=False,  # For frontend apps, no client secret
            RefreshTokenValidity=30,  # 30 days
            AccessTokenValidity=60,   # 60 minutes
            IdTokenValidity=60,       # 60 minutes
            TokenValidityUnits={
                'AccessToken': 'minutes',
                'IdToken': 'minutes',
                'RefreshToken': 'days'
            },
            ExplicitAuthFlows=[
                'ALLOW_USER_PASSWORD_AUTH',
                'ALLOW_USER_SRP_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH'
            ],
            SupportedIdentityProviders=['COGNITO'],
            PreventUserExistenceErrors='ENABLED'
        )
        
        client_id = response['UserPoolClient']['ClientId']
        print_status(f"✅ App client created successfully!")
        print_status(f"Client ID: {client_id}")
        
        return client_id
        
    except Exception as e:
        print_error(f"Failed to create app client: {str(e)}")
        return None

def update_config_files(client_id):
    """Update configuration files with the new client ID"""
    
    print_step("Updating Configuration Files")
    
    # Update .env.example
    env_example_path = Path(__file__).parent.parent / "backend-fastapi-graphql" / ".env.example"
    if env_example_path.exists():
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        content = content.replace(
            'COGNITO_APP_CLIENT_ID=""  # Will be filled after creating App Client',
            f'COGNITO_APP_CLIENT_ID="{client_id}"'
        )
        
        with open(env_example_path, 'w') as f:
            f.write(content)
        print_status("Updated .env.example")
    
    # Update .env if it exists
    env_path = Path(__file__).parent.parent / "backend-fastapi-graphql" / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Replace empty client ID or existing one
        import re
        content = re.sub(
            r'COGNITO_APP_CLIENT_ID="[^"]*"',
            f'COGNITO_APP_CLIENT_ID="{client_id}"',
            content
        )
        
        with open(env_path, 'w') as f:
            f.write(content)
        print_status("Updated .env")
    else:
        print_warning(".env file not found - copy from .env.example and update manually")
    
    # Update docker-compose.yml
    docker_compose_path = Path(__file__).parent.parent / "infrastructure" / "docker" / "docker-compose.yml"
    if docker_compose_path.exists():
        with open(docker_compose_path, 'r') as f:
            content = f.read()
        
        content = content.replace(
            'COGNITO_CLIENT_ID: ""  # 需要创建 App client 后填入',
            f'COGNITO_CLIENT_ID: "{client_id}"'
        )
        
        with open(docker_compose_path, 'w') as f:
            f.write(content)
        print_status("Updated docker-compose.yml")
    
    # Update config.py
    config_path = Path(__file__).parent.parent / "backend-fastapi-graphql" / "app" / "core" / "config.py"
    if config_path.exists():
        with open(config_path, 'r') as f:
            content = f.read()
        
        content = content.replace(
            'cognito_client_id: str = ""  # 需要创建 App client 后填入',
            f'cognito_client_id: str = "{client_id}"'
        )
        
        with open(config_path, 'w') as f:
            f.write(content)
        print_status("Updated config.py")

def create_test_user():
    """Create a test user for development"""
    
    print_step("Creating Test User")
    
    USER_POOL_ID = "us-east-1_blSZREFys"
    REGION = "us-east-1"
    
    email = input("Enter test user email (or press Enter to skip): ").strip()
    if not email:
        print_status("Skipping test user creation")
        return
    
    try:
        cognito_client = boto3.client('cognito-idp', region_name=REGION)
        
        # Create user
        response = cognito_client.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=email,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'}
            ],
            TemporaryPassword='TempPass123!',
            MessageAction='SUPPRESS'  # Don't send email
        )
        
        print_status(f"✅ Test user created: {email}")
        print_status("Temporary password: TempPass123!")
        print_warning("User must change password on first login")
        
    except Exception as e:
        print_error(f"Failed to create test user: {str(e)}")

def main():
    """Main function"""
    
    print("🔐 JobQuest Navigator v2 - Cognito App Client Creator")
    print("=" * 60)
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print_status(f"AWS Account: {identity['Account']}")
        print_status(f"User/Role: {identity['Arn']}")
    except Exception as e:
        print_error("AWS credentials not configured or invalid")
        print_error("Please run 'aws configure' first")
        return False
    
    # Create app client
    client_id = create_cognito_client()
    if not client_id:
        return False
    
    # Update configuration files
    update_config_files(client_id)
    
    # Ask about test user
    create_test_user()
    
    print_step("Setup Complete!")
    print_status("🎉 Cognito App Client configured successfully!")
    print()
    print("Next steps:")
    print("1. Start the development environment:")
    print("   ./scripts/dev-start.sh")
    print()
    print("2. Test the configuration:")
    print("   ./scripts/test-cognito.py")
    print()
    print("3. Access the application:")
    print("   - Frontend: http://localhost:3001")
    print("   - Backend: http://localhost:8001")
    print("   - GraphQL: http://localhost:8001/graphql")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)