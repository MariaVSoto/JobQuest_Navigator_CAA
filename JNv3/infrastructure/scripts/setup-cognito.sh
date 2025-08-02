#!/bin/bash
# JobQuest Navigator v2 - AWS Cognito Setup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

echo "🔐 JobQuest Navigator v2 - AWS Cognito Configuration"
echo "=================================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first:"
    echo "  macOS: brew install awscli"
    echo "  Linux: sudo apt-get install awscli"
    echo "  Windows: Download from https://aws.amazon.com/cli/"
    exit 1
fi

# Current Cognito configuration
USER_POOL_ID="us-east-1_bISZREFys"
REGION="us-east-1"

print_step "Current Configuration"
print_status "User Pool ID: $USER_POOL_ID"
print_status "Region: $REGION"

# Check if user pool exists and get details
print_step "Verifying User Pool"
if aws cognito-idp describe-user-pool --user-pool-id "$USER_POOL_ID" --region "$REGION" &>/dev/null; then
    print_status "User pool verified successfully"
    
    # Get user pool details
    USER_POOL_NAME=$(aws cognito-idp describe-user-pool --user-pool-id "$USER_POOL_ID" --region "$REGION" --query 'UserPool.Name' --output text)
    print_status "User Pool Name: $USER_POOL_NAME"
else
    print_error "Cannot access user pool $USER_POOL_ID"
    print_warning "Please check your AWS credentials and permissions"
    exit 1
fi

# Check for existing app clients
print_step "Checking App Clients"
APP_CLIENTS=$(aws cognito-idp list-user-pool-clients --user-pool-id "$USER_POOL_ID" --region "$REGION" --query 'UserPoolClients[*].[ClientId,ClientName]' --output table)

if [ -n "$APP_CLIENTS" ]; then
    print_status "Existing App Clients:"
    echo "$APP_CLIENTS"
    
    # Ask if user wants to use existing client
    read -p "Do you want to use an existing app client? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter the Client ID: " CLIENT_ID
        
        # Update configuration files
        print_step "Updating Configuration Files"
        
        # Update .env.template
        if [ -f "../backend-fastapi-graphql/.env.template" ]; then
            sed -i.bak "s/COGNITO_CLIENT_ID=\"\"/COGNITO_CLIENT_ID=\"$CLIENT_ID\"/" ../backend-fastapi-graphql/.env.template
            print_status "Updated backend .env.template"
        fi
        
        # Update docker-compose.yml
        if [ -f "../infrastructure/docker/docker-compose.yml" ]; then
            sed -i.bak "s/COGNITO_CLIENT_ID: \"\"/COGNITO_CLIENT_ID: \"$CLIENT_ID\"/" ../infrastructure/docker/docker-compose.yml
            print_status "Updated docker-compose.yml"
        fi
        
        # Update config.py
        if [ -f "../backend-fastapi-graphql/app/core/config.py" ]; then
            sed -i.bak "s/cognito_client_id: str = \"\"/cognito_client_id: str = \"$CLIENT_ID\"/" ../backend-fastapi-graphql/app/core/config.py
            print_status "Updated config.py"
        fi
        
        print_step "Configuration Complete!"
        print_status "Cognito Client ID: $CLIENT_ID"
        exit 0
    fi
fi

# Create new app client
print_step "Creating New App Client"
read -p "Enter a name for the new app client (default: jobquest-navigator-v2): " CLIENT_NAME
CLIENT_NAME=${CLIENT_NAME:-"jobquest-navigator-v2"}

print_status "Creating app client: $CLIENT_NAME"

# Create the app client
CLIENT_RESPONSE=$(aws cognito-idp create-user-pool-client \
    --user-pool-id "$USER_POOL_ID" \
    --client-name "$CLIENT_NAME" \
    --no-generate-secret \
    --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH ALLOW_USER_SRP_AUTH \
    --supported-identity-providers COGNITO \
    --read-attributes email name \
    --write-attributes email name \
    --access-token-validity 60 \
    --id-token-validity 60 \
    --refresh-token-validity 30 \
    --token-validity-units AccessToken=minutes IdToken=minutes RefreshToken=days \
    --region "$REGION" \
    --output json)

if [ $? -eq 0 ]; then
    CLIENT_ID=$(echo "$CLIENT_RESPONSE" | jq -r '.UserPoolClient.ClientId')
    print_status "App client created successfully!"
    print_status "Client ID: $CLIENT_ID"
    
    # Update configuration files
    print_step "Updating Configuration Files"
    
    # Update .env.template
    if [ -f "../backend-fastapi-graphql/.env.template" ]; then
        sed -i.bak "s/COGNITO_CLIENT_ID=\"\"/COGNITO_CLIENT_ID=\"$CLIENT_ID\"/" ../backend-fastapi-graphql/.env.template
        print_status "Updated backend .env.template"
    fi
    
    # Update docker-compose.yml
    if [ -f "../infrastructure/docker/docker-compose.yml" ]; then
        sed -i.bak "s/COGNITO_CLIENT_ID: \"\"/COGNITO_CLIENT_ID: \"$CLIENT_ID\"/" ../infrastructure/docker/docker-compose.yml
        print_status "Updated docker-compose.yml"
    fi
    
    # Update config.py
    if [ -f "../backend-fastapi-graphql/app/core/config.py" ]; then
        sed -i.bak "s/cognito_client_id: str = \"\"/cognito_client_id: str = \"$CLIENT_ID\"/" ../backend-fastapi-graphql/app/core/config.py
        print_status "Updated config.py"
    fi
    
    print_step "Configuration Complete!"
    print_status "User Pool ID: $USER_POOL_ID"
    print_status "Client ID: $CLIENT_ID"
    print_status "Region: $REGION"
    
    echo
    print_status "Next steps:"
    echo "1. Copy .env.template to .env in backend-fastapi-graphql/"
    echo "2. Start the development environment: ./scripts/dev-start.sh"
    echo "3. Test authentication at http://localhost:8001/auth/status"
    
else
    print_error "Failed to create app client"
    exit 1
fi