"""
API Security Management for JobQuest Navigator.

This module provides secure API key management, usage tracking, and rate limiting
to prevent unauthorized access and control costs.
"""

import os
import logging
import redis
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured


logger = logging.getLogger('security')


class APISecurityException(Exception):
    """Base exception for API security issues."""
    pass


class APILimitExceededException(APISecurityException):
    """Raised when API usage limits are exceeded."""
    pass


class APIKeyNotFoundException(APISecurityException):
    """Raised when required API keys are not found."""
    pass


class SecureAPIManager:
    """
    Manages API keys securely and prevents exposure in logs or errors.
    """
    
    def __init__(self):
        self._api_keys = {}
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load and validate API keys from environment variables."""
        required_keys = ['OPENAI_API_KEY']  # Adzuna API removed as per project requirements
        
        for key_name in required_keys:
            key_value = getattr(settings, key_name, None)
            if not key_value:
                logger.warning(f"API key {key_name} is not configured")
                self._api_keys[key_name] = None
            else:
                self._api_keys[key_name] = key_value
                logger.info(f"API key {key_name} loaded successfully: {self.get_masked_key(key_value)}")
    
    def get_api_key(self, key_name: str) -> str:
        """Get API key by name with validation."""
        if key_name not in self._api_keys:
            raise APIKeyNotFoundException(f"Unknown API key: {key_name}")
        
        key_value = self._api_keys[key_name]
        if not key_value:
            raise APIKeyNotFoundException(f"API key {key_name} is not configured")
        
        return key_value
    
    @staticmethod
    def get_masked_key(key: str) -> str:
        """Return partially masked key for logging purposes."""
        if len(key) <= 8:
            return "*" * len(key)
        return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"
    
    @property
    def openai_key(self) -> str:
        """Get OpenAI API key."""
        return self.get_api_key('OPENAI_API_KEY')
    
    # Adzuna API methods removed as per project requirements


class APIUsageTracker:
    """
    Tracks API usage and enforces limits to prevent cost overruns.
    """
    
    def __init__(self):
        self.redis_client = self._get_redis_client()
        self.openai_token_limit = getattr(settings, 'OPENAI_DAILY_TOKEN_LIMIT', 100000)
        self.openai_cost_limit = Decimal(str(getattr(settings, 'OPENAI_DAILY_COST_LIMIT', 50.00)))
        # Adzuna limits removed as per project requirements
    
    def _get_redis_client(self):
        """Get Redis client for usage tracking."""
        try:
            if hasattr(settings, 'CACHES') and 'default' in settings.CACHES:
                return cache
            else:
                # Fallback to direct Redis connection
                redis_url = getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379/1')
                return redis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Redis not available, using local cache: {e}")
            return cache
    
    def _get_daily_key(self, service: str, metric: str) -> str:
        """Generate daily cache key for usage tracking."""
        today = datetime.now().strftime('%Y-%m-%d')
        return f"api_usage:{service}:{metric}:{today}"
    
    def _calculate_openai_cost(self, model_name: str, prompt_tokens: int, completion_tokens: int) -> Decimal:
        """
        Calculate precise cost for OpenAI API usage based on model pricing.
        
        Args:
            model_name: OpenAI model name
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            
        Returns:
            Calculated cost as Decimal
        """
        model_costs = getattr(settings, 'OPENAI_MODEL_COSTS', {})
        
        if model_name not in model_costs:
            logger.warning(f"Unknown model '{model_name}', using gpt-4o pricing as fallback")
            model_name = 'gpt-4o'
        
        if model_name not in model_costs:
            # Ultimate fallback if even gpt-4o is not configured
            logger.error(f"No pricing configured for model '{model_name}' or fallback 'gpt-4o'")
            prompt_cost_per_1k = Decimal('0.005')  # Default to gpt-4o pricing
            completion_cost_per_1k = Decimal('0.015')
        else:
            pricing = model_costs[model_name]
            prompt_cost_per_1k = Decimal(str(pricing['prompt_usd_per_1k_tokens']))
            completion_cost_per_1k = Decimal(str(pricing['completion_usd_per_1k_tokens']))
        
        # Calculate costs
        prompt_cost = (Decimal(str(prompt_tokens)) / 1000) * prompt_cost_per_1k
        completion_cost = (Decimal(str(completion_tokens)) / 1000) * completion_cost_per_1k
        total_cost = prompt_cost + completion_cost
        
        logger.debug(f"Cost calculation for {model_name}: "
                    f"prompt={prompt_tokens}*${prompt_cost_per_1k}/1k=${prompt_cost:.6f}, "
                    f"completion={completion_tokens}*${completion_cost_per_1k}/1k=${completion_cost:.6f}, "
                    f"total=${total_cost:.6f}")
        
        return total_cost
    
    def track_openai_usage(self, model_name: str, prompt_tokens: int, completion_tokens: int, 
                          total_tokens: int = None) -> Dict:
        """
        Track OpenAI API usage with detailed token breakdown and model-specific cost calculation.
        
        Args:
            model_name: OpenAI model name (e.g., 'gpt-4o', 'gpt-4-turbo')
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            total_tokens: Total tokens (defaults to prompt + completion)
            
        Returns:
            Dict with detailed usage statistics
            
        Raises:
            APILimitExceededException: When limits are exceeded
        """
        # Calculate total tokens if not provided
        if total_tokens is None:
            total_tokens = prompt_tokens + completion_tokens
        
        # Calculate precise cost based on model pricing
        calculated_cost = self._calculate_openai_cost(model_name, prompt_tokens, completion_tokens)
        
        # Cache keys for different metrics
        token_key = self._get_daily_key('openai', 'tokens')
        cost_key = self._get_daily_key('openai', 'cost')
        prompt_token_key = self._get_daily_key('openai', 'prompt_tokens')
        completion_token_key = self._get_daily_key('openai', 'completion_tokens')
        
        try:
            # Track tokens
            current_tokens = int(self.redis_client.get(token_key) or 0)
            current_prompt_tokens = int(self.redis_client.get(prompt_token_key) or 0)
            current_completion_tokens = int(self.redis_client.get(completion_token_key) or 0)
            
            new_token_total = current_tokens + total_tokens
            new_prompt_total = current_prompt_tokens + prompt_tokens
            new_completion_total = current_completion_tokens + completion_tokens
            
            # Track cost
            current_cost = Decimal(str(self.redis_client.get(cost_key) or 0))
            new_cost_total = current_cost + calculated_cost
            
            # Check limits before updating
            if new_token_total > self.openai_token_limit:
                logger.error(f"OpenAI daily token limit exceeded: {new_token_total} > {self.openai_token_limit}")
                raise APILimitExceededException(
                    f"Daily OpenAI token limit ({self.openai_token_limit}) exceeded"
                )
            
            if new_cost_total > Decimal(str(self.openai_cost_limit)):
                logger.error(f"OpenAI daily cost limit exceeded: ${new_cost_total} > ${self.openai_cost_limit}")
                raise APILimitExceededException(
                    f"Daily OpenAI cost limit (${self.openai_cost_limit}) exceeded"
                )
            
            # Update all usage metrics
            self.redis_client.set(token_key, new_token_total, 86400)  # 24 hours
            self.redis_client.set(cost_key, str(new_cost_total), 86400)
            self.redis_client.set(prompt_token_key, new_prompt_total, 86400)
            self.redis_client.set(completion_token_key, new_completion_total, 86400)
            
            usage_stats = {
                'model_name': model_name,
                'tokens_used_today': new_token_total,
                'prompt_tokens_today': new_prompt_total,
                'completion_tokens_today': new_completion_total,
                'cost_today': float(new_cost_total),
                'tokens_remaining': self.openai_token_limit - new_token_total,
                'cost_remaining': float(Decimal(str(self.openai_cost_limit)) - new_cost_total),
                'tokens_limit': self.openai_token_limit,
                'cost_limit': float(self.openai_cost_limit),
                'current_request': {
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                    'cost': float(calculated_cost)
                }
            }
            
            # Log detailed usage
            logger.info(f"OpenAI usage tracked: {model_name} - {total_tokens} tokens "
                       f"(prompt: {prompt_tokens}, completion: {completion_tokens}), "
                       f"cost: ${calculated_cost:.6f}")
            
            # Alert at 80% usage
            if new_token_total > (self.openai_token_limit * 0.8):
                logger.warning(f"OpenAI token usage at {(new_token_total/self.openai_token_limit)*100:.1f}%")
            
            cost_limit_decimal = Decimal(str(self.openai_cost_limit))
            if new_cost_total > (cost_limit_decimal * Decimal('0.8')):
                logger.warning(f"OpenAI cost usage at {(new_cost_total/cost_limit_decimal)*100:.1f}%")
            
            return usage_stats
            
        except Exception as e:
            logger.error(f"Failed to track OpenAI usage: {e}")
            raise
    
    # Adzuna tracking methods removed as per project requirements
    
    def get_usage_stats(self, service: str = None) -> Dict:
        """Get current usage statistics with detailed breakdown."""
        stats = {}
        
        try:
            if service is None or service == 'openai':
                token_key = self._get_daily_key('openai', 'tokens')
                cost_key = self._get_daily_key('openai', 'cost')
                prompt_token_key = self._get_daily_key('openai', 'prompt_tokens')
                completion_token_key = self._get_daily_key('openai', 'completion_tokens')
                
                current_tokens = int(self.redis_client.get(token_key) or 0)
                current_cost = float(self.redis_client.get(cost_key) or 0)
                current_prompt_tokens = int(self.redis_client.get(prompt_token_key) or 0)
                current_completion_tokens = int(self.redis_client.get(completion_token_key) or 0)
                
                stats['openai'] = {
                    'tokens_used': current_tokens,
                    'prompt_tokens_used': current_prompt_tokens,
                    'completion_tokens_used': current_completion_tokens,
                    'cost_used': current_cost,
                    'tokens_remaining': max(0, self.openai_token_limit - current_tokens),
                    'cost_remaining': max(0, float(self.openai_cost_limit) - current_cost),
                    'tokens_limit': self.openai_token_limit,
                    'cost_limit': float(self.openai_cost_limit),
                    'token_usage_percentage': (current_tokens / self.openai_token_limit * 100) if self.openai_token_limit > 0 else 0,
                    'cost_usage_percentage': (current_cost / float(self.openai_cost_limit) * 100) if self.openai_cost_limit > 0 else 0,
                }
            
            # Adzuna stats removed as per project requirements
                
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            
        return stats


# Global instances
api_manager = SecureAPIManager()
usage_tracker = APIUsageTracker()