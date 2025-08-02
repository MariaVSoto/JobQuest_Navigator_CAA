#!/usr/bin/env python3
"""
JobQuest Navigator v2 - Configuration Loader
A utility to load and validate environment configurations with AWS integration
"""

import os
import re
import json
import boto3
from typing import Dict, Any, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigLoader:
    """Configuration loader with AWS Secrets Manager and Parameter Store integration"""
    
    def __init__(self, environment: str = None, region: str = "us-east-1"):
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.region = region
        self.config_dir = Path(__file__).parent
        self.env_file = self.config_dir / "environments" / f"{self.environment}.env"
        
        # AWS clients (lazy loading)
        self._secrets_client = None
        self._ssm_client = None
        self._sts_client = None
        
        # Cache for AWS values
        self._secrets_cache = {}
        self._parameters_cache = {}
        
    @property
    def secrets_client(self):
        """Lazy load AWS Secrets Manager client"""
        if self._secrets_client is None:
            self._secrets_client = boto3.client("secretsmanager", region_name=self.region)
        return self._secrets_client
    
    @property
    def ssm_client(self):
        """Lazy load AWS Systems Manager client"""
        if self._ssm_client is None:
            self._ssm_client = boto3.client("ssm", region_name=self.region)
        return self._ssm_client
    
    @property
    def sts_client(self):
        """Lazy load AWS STS client"""
        if self._sts_client is None:
            self._sts_client = boto3.client("sts", region_name=self.region)
        return self._sts_client
    
    def load_config(self) -> Dict[str, str]:
        """Load configuration from environment file with AWS value resolution"""
        if not self.env_file.exists():
            raise FileNotFoundError(f"Environment file not found: {self.env_file}")
        
        config = {}
        
        logger.info(f"Loading configuration for environment: {self.environment}")
        
        with open(self.env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Resolve special value patterns
                    resolved_value = self._resolve_value(key, value)
                    config[key] = resolved_value
                else:
                    logger.warning(f"Invalid line {line_num} in {self.env_file}: {line}")
        
        # Validate required configurations
        self._validate_config(config)
        
        logger.info(f"Loaded {len(config)} configuration values")
        return config
    
    def _resolve_value(self, key: str, value: str) -> str:
        """Resolve special value patterns like AWS_SECRET_MANAGER, AWS_PARAMETER_STORE, etc."""
        if not value:
            return value
        
        # Pattern: ${AWS_SECRET_MANAGER:secret-name}
        secret_pattern = r'\$\{AWS_SECRET_MANAGER:([^}]+)\}'
        secret_match = re.search(secret_pattern, value)
        if secret_match:
            secret_name = secret_match.group(1)
            return self._get_secret_value(secret_name)
        
        # Pattern: ${AWS_PARAMETER_STORE:parameter-name}
        param_pattern = r'\$\{AWS_PARAMETER_STORE:([^}]+)\}'
        param_match = re.search(param_pattern, value)
        if param_match:
            param_name = param_match.group(1)
            return self._get_parameter_value(param_name)
        
        # Pattern: ${TERRAFORM_OUTPUT:output-name}
        terraform_pattern = r'\$\{TERRAFORM_OUTPUT:([^}]+)\}'
        terraform_match = re.search(terraform_pattern, value)
        if terraform_match:
            output_name = terraform_match.group(1)
            return self._get_terraform_output(output_name)
        
        # Pattern: ${ENV:variable-name} or ${variable-name}
        env_pattern = r'\$\{(?:ENV:)?([^}]+)\}'
        env_match = re.search(env_pattern, value)
        if env_match:
            env_var = env_match.group(1)
            return os.getenv(env_var, "")
        
        return value
    
    def _get_secret_value(self, secret_name: str) -> str:
        """Retrieve value from AWS Secrets Manager"""
        if secret_name in self._secrets_cache:
            return self._secrets_cache[secret_name]
        
        try:
            logger.debug(f"Fetching secret: {secret_name}")
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            secret_value = response['SecretString']
            
            # Try to parse as JSON first
            try:
                secret_data = json.loads(secret_value)
                if isinstance(secret_data, dict) and len(secret_data) == 1:
                    # Single key-value pair
                    secret_value = list(secret_data.values())[0]
            except json.JSONDecodeError:
                # Not JSON, use as plain string
                pass
            
            self._secrets_cache[secret_name] = secret_value
            logger.debug(f"Successfully retrieved secret: {secret_name}")
            return secret_value
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            if self.environment == "development":
                # Return placeholder for development
                return f"dev-placeholder-{secret_name}"
            raise
    
    def _get_parameter_value(self, param_name: str) -> str:
        """Retrieve value from AWS Systems Manager Parameter Store"""
        if param_name in self._parameters_cache:
            return self._parameters_cache[param_name]
        
        try:
            logger.debug(f"Fetching parameter: {param_name}")
            response = self.ssm_client.get_parameter(Name=param_name, WithDecryption=True)
            param_value = response['Parameter']['Value']
            
            self._parameters_cache[param_name] = param_value
            logger.debug(f"Successfully retrieved parameter: {param_name}")
            return param_value
            
        except Exception as e:
            logger.error(f"Failed to retrieve parameter {param_name}: {e}")
            if self.environment == "development":
                # Return placeholder for development
                return f"dev-placeholder-{param_name}"
            raise
    
    def _get_terraform_output(self, output_name: str) -> str:
        """Retrieve Terraform output from state or parameter store"""
        # First try Parameter Store (recommended approach)
        param_name = f"/terraform/{self.environment}/{output_name}"
        try:
            return self._get_parameter_value(param_name)
        except:
            pass
        
        # Fallback to local terraform output (development only)
        if self.environment == "development":
            terraform_dir = self.config_dir.parent / "terraform"
            if terraform_dir.exists():
                try:
                    import subprocess
                    result = subprocess.run(
                        ["terraform", "output", "-raw", output_name],
                        cwd=terraform_dir,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        return result.stdout.strip()
                except Exception as e:
                    logger.debug(f"Failed to get terraform output {output_name}: {e}")
        
        logger.warning(f"Could not resolve terraform output: {output_name}")
        return f"terraform-output-{output_name}"
    
    def _validate_config(self, config: Dict[str, str]) -> None:
        """Validate configuration for required values"""
        required_keys = [
            "ENVIRONMENT",
            "SECRET_KEY",
            "DATABASE_URL",
            "REDIS_URL"
        ]
        
        missing_keys = [key for key in required_keys if not config.get(key)]
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        
        # Environment-specific validation
        if self.environment == "production":
            self._validate_production_config(config)
        
        logger.info("Configuration validation passed")
    
    def _validate_production_config(self, config: Dict[str, str]) -> None:
        """Additional validation for production environment"""
        production_requirements = {
            "DEBUG": "false",
            "GRAPHQL_INTROSPECTION": "false",
            "GRAPHQL_PLAYGROUND": "false",
            "ENABLE_DOCS": "false"
        }
        
        for key, expected_value in production_requirements.items():
            if config.get(key, "").lower() != expected_value:
                raise ValueError(f"Production config error: {key} must be {expected_value}")
        
        # Check for development placeholders
        for key, value in config.items():
            if "dev-placeholder" in value or "dev-secret" in value:
                raise ValueError(f"Production config contains development placeholder: {key}")
    
    def export_to_file(self, config: Dict[str, str], output_file: str) -> None:
        """Export resolved configuration to a file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(f"# JobQuest Navigator v2 - Resolved Configuration\n")
            f.write(f"# Environment: {self.environment}\n")
            f.write(f"# Generated at: {os.popen('date').read().strip()}\n\n")
            
            for key, value in sorted(config.items()):
                # Mask sensitive values
                if any(sensitive in key.lower() for sensitive in 
                      ['password', 'secret', 'key', 'token', 'credential']):
                    masked_value = value[:4] + "*" * (len(value) - 4) if len(value) > 4 else "****"
                    f.write(f"{key}={masked_value}\n")
                else:
                    f.write(f"{key}={value}\n")
        
        logger.info(f"Configuration exported to: {output_path}")
    
    def validate_aws_access(self) -> bool:
        """Validate AWS access for the current environment"""
        try:
            # Test STS access
            self.sts_client.get_caller_identity()
            logger.info("AWS access validated successfully")
            return True
        except Exception as e:
            logger.error(f"AWS access validation failed: {e}")
            return False


def main():
    """CLI interface for the configuration loader"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JobQuest Navigator v2 Configuration Loader")
    parser.add_argument("--environment", "-e", default=None, 
                       help="Environment to load (development, staging, production)")
    parser.add_argument("--output", "-o", default=None,
                       help="Output file for resolved configuration")
    parser.add_argument("--validate", "-v", action="store_true",
                       help="Validate configuration only")
    parser.add_argument("--check-aws", action="store_true",
                       help="Check AWS connectivity")
    parser.add_argument("--region", default="us-east-1",
                       help="AWS region")
    
    args = parser.parse_args()
    
    try:
        loader = ConfigLoader(environment=args.environment, region=args.region)
        
        if args.check_aws:
            loader.validate_aws_access()
            return
        
        config = loader.load_config()
        
        if args.validate:
            print(f"✅ Configuration validation passed for {loader.environment}")
            return
        
        if args.output:
            loader.export_to_file(config, args.output)
        else:
            print(f"Configuration loaded successfully for {loader.environment}")
            print(f"Loaded {len(config)} configuration values")
    
    except Exception as e:
        logger.error(f"Configuration loading failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()