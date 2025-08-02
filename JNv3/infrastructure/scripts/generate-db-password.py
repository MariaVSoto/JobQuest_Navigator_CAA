#!/usr/bin/env python3
"""
Generate secure database password for JobQuest Navigator v3
This script generates a random password that can be used for the database
"""

import secrets
import string
import sys

def generate_password(length=32):
    """Generate a secure random password"""
    # Define character sets
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special_chars = "!@#$%^&*"
    
    # Ensure at least one character from each set
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase), 
        secrets.choice(digits),
        secrets.choice(special_chars)
    ]
    
    # Fill the rest with random characters from all sets
    all_chars = uppercase + lowercase + digits + special_chars
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password list
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        try:
            length = int(sys.argv[1])
            if length < 8:
                print("Password length should be at least 8 characters")
                sys.exit(1)
        except ValueError:
            print("Invalid length specified. Using default length of 32.")
            length = 32
    else:
        length = 32
    
    password = generate_password(length)
    print(f"Generated secure database password ({length} characters):")
    print(password)
    
    # Provide instructions
    print("\n" + "="*50)
    print("IMPORTANT: Add this password to GitHub Secrets")
    print("="*50)
    print("1. Go to your GitHub repository")
    print("2. Navigate to Settings > Secrets and variables > Actions")
    print("3. Add a new repository secret:")
    print("   Name: DB_PASSWORD")
    print(f"   Value: {password}")
    print("\nThis password will be used by the deployment workflow")
    print("to connect to the PostgreSQL database.")

if __name__ == "__main__":
    main()