#!/bin/bash

# GitHub Actions Script to Check for Hardcoded Secrets
# This script identifies potential hardcoded secrets in the codebase

set -e

echo "🔍 Checking for hardcoded secrets and sensitive information..."

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Initialize counters
ISSUES_FOUND=0
WARNINGS_FOUND=0

# Function to report issues
report_issue() {
    local file="$1"
    local line="$2"
    local pattern="$3"
    local severity="$4"
    
    if [ "$severity" = "ERROR" ]; then
        echo -e "${RED}❌ ERROR: $file:$line - $pattern${NC}"
        ((ISSUES_FOUND++))
    else
        echo -e "${YELLOW}⚠️  WARNING: $file:$line - $pattern${NC}"
        ((WARNINGS_FOUND++))
    fi
}

# Check for common hardcoded secrets patterns
echo "Checking for hardcoded secrets..."

# Search for hardcoded passwords and keys
while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    line_num=$(echo "$line" | cut -d: -f2)
    content=$(echo "$line" | cut -d: -f3-)
    
    # Skip certain files and patterns
    if [[ "$file" == *"node_modules"* ]] || \
       [[ "$file" == *".git"* ]] || \
       [[ "$file" == *"coverage"* ]] || \
       [[ "$file" == *".md"* ]] || \
       [[ "$file" == *"check-hardcoded-secrets.sh"* ]]; then
        continue
    fi
    
    # Check for actual secret values (not templates or references)
    if [[ "$content" =~ (SECRET_KEY|PASSWORD|API_KEY).*=.*[\"\'](dev-|test-|your-|change|example|placeholder|secret|password|key)[\"\']*[^$] ]] && \
       [[ ! "$content" =~ \$\{ ]]; then
        report_issue "$file" "$line_num" "Hardcoded secret detected" "ERROR"
    fi
    
done < <(grep -rn -E "(SECRET_KEY|PASSWORD|API_KEY|ACCESS_KEY|PRIVATE_KEY).*=" JNv3/ 2>/dev/null || true)

# Check for hardcoded credentials
while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    line_num=$(echo "$line" | cut -d: -f2)
    content=$(echo "$line" | cut -d: -f3-)
    
    # Skip documentation and example files
    if [[ "$file" == *"node_modules"* ]] || \
       [[ "$file" == *".git"* ]] || \
       [[ "$file" == *"coverage"* ]] || \
       [[ "$file" == *".md"* ]] || \
       [[ "$file" == *"example"* ]]; then
        continue
    fi
    
    # Check for hardcoded minioadmin credentials
    if [[ "$content" =~ minioadmin ]] && [[ ! "$content" =~ \$\{ ]]; then
        report_issue "$file" "$line_num" "Hardcoded MinIO credentials" "ERROR"
    fi
    
done < <(grep -rn "minioadmin" JNv3/ 2>/dev/null || true)

# Check for database connection strings with embedded passwords
while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    line_num=$(echo "$line" | cut -d: -f2)
    content=$(echo "$line" | cut -d: -f3-)
    
    if [[ "$file" == *"node_modules"* ]] || \
       [[ "$file" == *".git"* ]] || \
       [[ "$file" == *"coverage"* ]] || \
       [[ "$file" == *".md"* ]]; then
        continue
    fi
    
    # Check for database URLs with hardcoded passwords
    if [[ "$content" =~ (mysql|postgresql|postgres)://.*:.*@.* ]] && \
       [[ ! "$content" =~ \$\{ ]] && \
       [[ ! "$content" =~ \$[A-Z_] ]]; then
        report_issue "$file" "$line_num" "Database URL with embedded credentials" "ERROR"
    fi
    
done < <(grep -rn -E "(mysql|postgresql|postgres)://" JNv3/ 2>/dev/null || true)

# Check for AWS access keys (pattern matching)
while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    line_num=$(echo "$line" | cut -d: -f2)
    content=$(echo "$line" | cut -d: -f3-)
    
    if [[ "$file" == *"node_modules"* ]] || \
       [[ "$file" == *".git"* ]] || \
       [[ "$file" == *"coverage"* ]] || \
       [[ "$file" == *".md"* ]]; then
        continue
    fi
    
    # Check for AWS access key patterns
    if [[ "$content" =~ AKIA[0-9A-Z]{16} ]]; then
        report_issue "$file" "$line_num" "Potential AWS Access Key detected" "ERROR"
    fi
    
done < <(grep -rn "AKIA[0-9A-Z]\{16\}" JNv3/ 2>/dev/null || true)

# Check for JWT tokens and other long secrets
while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    line_num=$(echo "$line" | cut -d: -f2)
    content=$(echo "$line" | cut -d: -f3-)
    
    if [[ "$file" == *"node_modules"* ]] || \
       [[ "$file" == *".git"* ]] || \
       [[ "$file" == *"coverage"* ]] || \
       [[ "$file" == *".md"* ]]; then
        continue
    fi
    
    # Check for JWT tokens (basic pattern)
    if [[ "$content" =~ eyJ[A-Za-z0-9+/=]{20,} ]]; then
        report_issue "$file" "$line_num" "Potential JWT token detected" "ERROR"
    fi
    
done < <(grep -rn "eyJ[A-Za-z0-9+/=]\{20,\}" JNv3/ 2>/dev/null || true)

# Summary
echo -e "\n📊 Security Scan Summary:"
echo -e "🔴 Critical Issues: $ISSUES_FOUND"
echo -e "🟡 Warnings: $WARNINGS_FOUND"

if [ $ISSUES_FOUND -eq 0 ] && [ $WARNINGS_FOUND -eq 0 ]; then
    echo -e "\n${GREEN}✅ No hardcoded secrets detected!${NC}"
    exit 0
elif [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "\n${YELLOW}⚠️  Only warnings found. Review recommended but not blocking.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Critical security issues found! Please fix before deployment.${NC}"
    echo -e "\n📚 Solutions:"
    echo -e "1. Move secrets to GitHub repository secrets"
    echo -e "2. Use environment variables with \${{ secrets.SECRET_NAME }}"
    echo -e "3. For AWS: Use AWS Secrets Manager integration"
    echo -e "4. Review .github/GITHUB_SECRETS_SETUP.md for guidance"
    exit 1
fi