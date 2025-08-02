#!/bin/bash
# Terraform Backend Verification Script

set -e

echo "🔍 Terraform Backend Configuration Verification"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "main.tf" ] || [ ! -f "backend.tf" ]; then
  echo "❌ Error: Please run this script from the terraform directory"
  exit 1
fi

echo "📋 Backend Configuration:"
echo "   Bucket: caa900resume"
echo "   Key: terraform/terraform.tfstate"
echo "   Region: us-east-1"
echo "   Encryption: Enabled"
echo ""

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
  echo "⚠️  AWS CLI not found - please install AWS CLI to verify bucket access"
else
  echo "🔍 Checking S3 bucket access..."
  
  # Test bucket access
  if aws s3 ls s3://caa900resume/ &> /dev/null; then
    echo "✅ S3 bucket 'caa900resume' is accessible"
  else
    echo "❌ Cannot access S3 bucket 'caa900resume'"
    echo "   Please check your AWS credentials and bucket permissions"
    exit 1
  fi
fi

echo ""
echo "🚀 Ready to initialize Terraform!"
echo ""
echo "Run the following commands:"
echo "   terraform init"
echo "   terraform plan -var-file=environments/production.tfvars"
echo ""
echo "The backend will automatically use:"
echo "   s3://caa900resume/terraform/terraform.tfstate"