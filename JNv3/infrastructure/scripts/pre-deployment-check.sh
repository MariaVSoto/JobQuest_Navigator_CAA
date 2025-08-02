#!/bin/bash
"""
Pre-deployment check script for JobQuest Navigator v3
This script verifies that all required GitHub Secrets are configured
"""

set -e

echo "🔍 JobQuest Navigator v3 - Pre-deployment Check"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "Please install GitHub CLI: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub CLI${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI is installed and authenticated${NC}"

# Required secrets
REQUIRED_SECRETS=(
    "AWS_ACCESS_KEY_ID"
    "AWS_SECRET_ACCESS_KEY" 
    "SECRET_KEY"
    "DB_PASSWORD"
)

# Optional secrets (will warn if missing but not fail)
OPTIONAL_SECRETS=(
    "OPENAI_API_KEY"
)

echo ""
echo "🔐 Checking required GitHub Secrets..."

missing_secrets=()
for secret in "${REQUIRED_SECRETS[@]}"; do
    if gh secret list | grep -q "^${secret}"; then
        echo -e "${GREEN}✅ ${secret}${NC}"
    else
        echo -e "${RED}❌ ${secret} - MISSING${NC}"
        missing_secrets+=("$secret")
    fi
done

echo ""
echo "🔓 Checking optional GitHub Secrets..."
for secret in "${OPTIONAL_SECRETS[@]}"; do
    if gh secret list | grep -q "^${secret}"; then
        echo -e "${GREEN}✅ ${secret}${NC}"
    else
        echo -e "${YELLOW}⚠️  ${secret} - Missing (optional)${NC}"
    fi
done

echo ""
echo "🏗️  Checking AWS infrastructure files..."

# Check if Terraform files exist
terraform_files=(
    "JNv3/infrastructure/terraform/main.tf"
    "JNv3/infrastructure/terraform/variables.tf"
    "JNv3/infrastructure/terraform/outputs.tf"
    "JNv3/infrastructure/terraform/backend-configs/production.hcl"
)

missing_files=()
for file in "${terraform_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✅ ${file}${NC}"
    else
        echo -e "${RED}❌ ${file} - MISSING${NC}"
        missing_files+=("$file")
    fi
done

echo ""
echo "🐳 Checking application files..."

# Check if application files exist
app_files=(
    "JNv3/apps/backend-fastapi/Dockerfile"
    "JNv3/apps/backend-fastapi/requirements.txt"
    "JNv3/apps/frontend-react/Dockerfile"
    "JNv3/apps/frontend-react/package.json"
)

for file in "${app_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✅ ${file}${NC}"
    else
        echo -e "${RED}❌ ${file} - MISSING${NC}"
        missing_files+=("$file")
    fi
done

echo ""
echo "📋 Summary"
echo "=========="

if [[ ${#missing_secrets[@]} -eq 0 ]] && [[ ${#missing_files[@]} -eq 0 ]]; then
    echo -e "${GREEN}🎉 All required secrets and files are present!${NC}"
    echo -e "${GREEN}✅ Ready for deployment${NC}"
    echo ""
    echo "To deploy, push your changes to the main branch:"
    echo "  git add ."
    echo "  git commit -m \"Add complete deployment workflow\""
    echo "  git push origin main"
    echo ""
    echo "Or trigger manual deployment:"
    echo "  gh workflow run deploy-complete-app.yml"
    exit 0
else
    echo -e "${RED}❌ Missing required items:${NC}"
    
    if [[ ${#missing_secrets[@]} -gt 0 ]]; then
        echo ""
        echo "Missing secrets:"
        for secret in "${missing_secrets[@]}"; do
            echo "  - $secret"
        done
        echo ""
        echo "Add missing secrets:"
        echo "  1. Go to https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/settings/secrets/actions"
        echo "  2. Click 'New repository secret'"
        echo "  3. Add each missing secret"
        echo ""
        echo "Secret values:"
        echo "  SECRET_KEY: Use output from: python3 -c \"import secrets; print(secrets.token_urlsafe(50))\""
        echo "  DB_PASSWORD: Use output from: python3 JNv3/infrastructure/scripts/generate-db-password.py"
        echo "  AWS_ACCESS_KEY_ID: Your AWS access key"
        echo "  AWS_SECRET_ACCESS_KEY: Your AWS secret key"
    fi
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo ""
        echo "Missing files:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
    fi
    
    exit 1
fi