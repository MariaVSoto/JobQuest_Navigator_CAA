"""
AWS Secrets Manager utility for retrieving application secrets
"""

import boto3
import json
from typing import Dict, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class SecretsManager:
    """Utility class for retrieving secrets from AWS Secrets Manager"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of boto3 client"""
        if self._client is None:
            self._client = boto3.client('secretsmanager', region_name=self.region)
        return self._client
    
    @lru_cache(maxsize=32)
    def get_secret(self, secret_name: str) -> Optional[Dict]:
        """
        Retrieve and parse a secret from AWS Secrets Manager
        
        Args:
            secret_name: Name of the secret in Secrets Manager
            
        Returns:
            Dictionary containing the secret data, or None if not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_data = json.loads(response['SecretString'])
            logger.info(f"Successfully retrieved secret: {secret_name}")
            return secret_data
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {str(e)}")
            return None
    
    def get_aws_credentials(self) -> Optional[Dict[str, str]]:
        """
        Retrieve AWS credentials from Secrets Manager
        
        Returns:
            Dictionary with aws_access_key_id and aws_secret_access_key, or None
        """
        secret_name = "jobquest-navigator-v3-aws-credentials"
        credentials = self.get_secret(secret_name)
        
        if credentials and 'aws_access_key_id' in credentials and 'aws_secret_access_key' in credentials:
            return {
                'aws_access_key_id': credentials['aws_access_key_id'],
                'aws_secret_access_key': credentials['aws_secret_access_key']
            }
        
        logger.warning(f"AWS credentials not found or incomplete in secret: {secret_name}")
        return None


# Global instance
secrets_manager = SecretsManager()