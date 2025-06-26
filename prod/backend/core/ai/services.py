"""
OpenAI API service for AI-powered content generation.

This module provides a high-level interface to OpenAI's API with
token tracking, cost management, and structured response validation.
"""

import json
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import openai
from openai import AsyncOpenAI
from pydantic import ValidationError
from django.conf import settings

from core.security import api_manager, usage_tracker, APILimitExceededException
from .schemas import (
    CompanyResearch, JobSuggestion, MarketAnalysis,
    AIValidationError, AIServiceError, AIContentGenerationError,
    AIRateLimitError, AIModelNotAvailableError
)
from .responses import AIResponse
from .prompt_manager import prompt_manager, PromptTemplate

logger = logging.getLogger('ai.services')


class OpenAIService:
    """
    High-level OpenAI API service with token tracking and structured responses.
    
    This service provides a clean interface to OpenAI's API with automatic
    cost tracking, response validation, and error handling.
    """
    
    def __init__(self, default_model: str = 'gpt-4o-mini'):
        """
        Initialize the OpenAI service.
        
        Args:
            default_model: Default model to use for requests
        """
        self.default_model = default_model
        self._client: Optional[AsyncOpenAI] = None
        self._sync_client: Optional[openai.OpenAI] = None
    
    def _get_client(self, async_client: bool = True) -> openai.OpenAI:
        """
        Get the OpenAI client (async or sync).
        
        Args:
            async_client: Whether to return async client (for Celery tasks)
            
        Returns:
            OpenAI client instance
        """
        try:
            api_key = api_manager.openai_key
        except Exception as e:
            logger.error(f"Failed to get OpenAI API key: {e}")
            raise AIServiceError("OpenAI API key not configured") from e
        
        if async_client:
            if self._client is None:
                self._client = AsyncOpenAI(api_key=api_key)
            return self._client
        else:
            if self._sync_client is None:
                self._sync_client = openai.OpenAI(api_key=api_key)
            return self._sync_client
    
    def _handle_openai_exceptions(self, e: Exception) -> None:
        """
        Convert OpenAI exceptions to our custom exceptions.
        
        Args:
            e: The original OpenAI exception
            
        Raises:
            Custom AI service exceptions
        """
        if isinstance(e, openai.RateLimitError):
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise AIRateLimitError("OpenAI API rate limit exceeded") from e
        elif isinstance(e, openai.APIConnectionError):
            logger.error(f"OpenAI API connection error: {e}")
            raise AIServiceError("Failed to connect to OpenAI API") from e
        elif isinstance(e, openai.AuthenticationError):
            logger.error(f"OpenAI authentication error: {e}")
            raise AIServiceError("OpenAI API authentication failed") from e
        elif isinstance(e, openai.BadRequestError):
            logger.error(f"OpenAI bad request: {e}")
            if "model" in str(e).lower():
                raise AIModelNotAvailableError(f"Requested model not available: {e}") from e
            raise AIContentGenerationError(f"Invalid request to OpenAI API: {e}") from e
        else:
            logger.error(f"Unexpected OpenAI error: {e}")
            raise AIServiceError(f"Unexpected OpenAI API error: {e}") from e
    
    def _validate_and_parse_response(self, response_content: str, expected_schema: str) -> Any:
        """
        Validate and parse AI response JSON according to expected schema.
        
        Args:
            response_content: Raw JSON string from AI
            expected_schema: Expected schema name (e.g., 'CompanyResearch')
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            AIValidationError: If validation fails
        """
        try:
            # Parse JSON
            raw_data = json.loads(response_content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in AI response: {e}")
            logger.debug(f"Raw response content: {response_content}")
            raise AIValidationError(f"AI returned invalid JSON: {e}") from e
        
        # Validate against Pydantic schema
        schema_map = {
            'CompanyResearch': CompanyResearch,
            'JobSuggestion': JobSuggestion,
            'MarketAnalysis': MarketAnalysis,
        }
        
        if expected_schema not in schema_map:
            raise AIValidationError(f"Unknown schema: {expected_schema}")
        
        schema_class = schema_map[expected_schema]
        
        try:
            validated_data = schema_class.model_validate(raw_data)
            logger.debug(f"Successfully validated {expected_schema} response")
            return validated_data
        except ValidationError as e:
            logger.error(f"Pydantic validation failed for {expected_schema}: {e}")
            logger.debug(f"Raw data: {raw_data}")
            raise AIValidationError(f"AI response validation failed: {e}") from e
    
    async def generate_content(
        self,
        prompt_name: str,
        prompt_variables: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        expected_schema: str = 'CompanyResearch'
    ) -> AIResponse:
        """
        Generate AI content using a structured prompt and validate the response.
        
        Args:
            prompt_name: Name of the prompt template to use
            prompt_variables: Variables to substitute in the prompt
            model: OpenAI model to use (defaults to instance default)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            expected_schema: Expected response schema for validation
            
        Returns:
            AIResponse with validated content and metadata
            
        Raises:
            AIServiceError: For various AI service failures
        """
        start_time = time.time()
        model = model or self.default_model
        
        # Get and format the prompt
        try:
            prompt_template = prompt_manager.get_prompt(prompt_name)
            formatted_prompt = prompt_template.substitute(**prompt_variables)
        except Exception as e:
            logger.error(f"Failed to get/format prompt '{prompt_name}': {e}")
            raise AIContentGenerationError(f"Prompt preparation failed: {e}") from e
        
        # Check usage limits before making the request
        try:
            # Pre-flight check with estimated tokens (will be updated with actual usage)
            estimated_prompt_tokens = len(formatted_prompt.split()) * 1.3  # Rough estimate
            usage_tracker.track_openai_usage(model, int(estimated_prompt_tokens), 0, int(estimated_prompt_tokens))
        except APILimitExceededException as e:
            logger.error(f"Usage limit check failed: {e}")
            raise AIRateLimitError(str(e)) from e
        
        # Make the API request
        client = self._get_client(async_client=True)
        
        try:
            logger.info(f"Making OpenAI API request: model={model}, prompt={prompt_name}")
            
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional AI assistant that provides accurate, structured responses in JSON format."
                    },
                    {
                        "role": "user",
                        "content": formatted_prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=max_tokens
            )
            
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            self._handle_openai_exceptions(e)
        
        # Extract response data
        response_content = response.choices[0].message.content
        usage = response.usage
        request_id = getattr(response, 'id', None)
        
        # Track actual usage
        try:
            usage_stats = usage_tracker.track_openai_usage(
                model_name=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens
            )
            estimated_cost = usage_stats['current_request']['cost']
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
            estimated_cost = 0.0
        
        # Validate and parse the response
        try:
            validated_data = self._validate_and_parse_response(response_content, expected_schema)
        except AIValidationError as e:
            logger.error(f"Response validation failed: {e}")
            # Still log the usage even if validation failed
            raise
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Create structured response
        ai_response = AIResponse(
            data=validated_data,
            model_used=model,
            prompt_version=prompt_template.full_name,
            request_id=request_id,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            estimated_cost=estimated_cost,
            response_time_ms=response_time_ms,
            generated_at=datetime.now(),
            validation_passed=True
        )
        
        logger.info(f"AI content generation successful: "
                   f"{usage.total_tokens} tokens, ${estimated_cost:.6f} cost, "
                   f"{response_time_ms}ms response time")
        
        return ai_response
    
    def generate_content_sync(
        self,
        prompt_name: str,
        prompt_variables: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        expected_schema: str = 'CompanyResearch'
    ) -> AIResponse:
        """
        Synchronous version of generate_content for non-async contexts.
        
        Args:
            prompt_name: Name of the prompt template to use
            prompt_variables: Variables to substitute in the prompt
            model: OpenAI model to use (defaults to instance default)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            expected_schema: Expected response schema for validation
            
        Returns:
            AIResponse with validated content and metadata
        """
        start_time = time.time()
        model = model or self.default_model
        
        # Get and format the prompt
        try:
            prompt_template = prompt_manager.get_prompt(prompt_name)
            formatted_prompt = prompt_template.substitute(**prompt_variables)
        except Exception as e:
            logger.error(f"Failed to get/format prompt '{prompt_name}': {e}")
            raise AIContentGenerationError(f"Prompt preparation failed: {e}") from e
        
        # Check usage limits
        try:
            estimated_prompt_tokens = len(formatted_prompt.split()) * 1.3
            usage_tracker.track_openai_usage(model, int(estimated_prompt_tokens), 0, int(estimated_prompt_tokens))
        except APILimitExceededException as e:
            logger.error(f"Usage limit check failed: {e}")
            raise AIRateLimitError(str(e)) from e
        
        # Make the API request
        client = self._get_client(async_client=False)
        
        try:
            logger.info(f"Making OpenAI API request (sync): model={model}, prompt={prompt_name}")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional AI assistant that provides accurate, structured responses in JSON format."
                    },
                    {
                        "role": "user",
                        "content": formatted_prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=max_tokens
            )
            
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            self._handle_openai_exceptions(e)
        
        # Process response (same as async version)
        response_content = response.choices[0].message.content
        usage = response.usage
        request_id = getattr(response, 'id', None)
        
        # Track actual usage
        try:
            usage_stats = usage_tracker.track_openai_usage(
                model_name=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens
            )
            estimated_cost = usage_stats['current_request']['cost']
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
            estimated_cost = 0.0
        
        # Validate response
        validated_data = self._validate_and_parse_response(response_content, expected_schema)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Create structured response
        ai_response = AIResponse(
            data=validated_data,
            model_used=model,
            prompt_version=prompt_template.full_name,
            request_id=request_id,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            estimated_cost=estimated_cost,
            response_time_ms=response_time_ms,
            generated_at=datetime.now(),
            validation_passed=True
        )
        
        logger.info(f"AI content generation successful (sync): "
                   f"{usage.total_tokens} tokens, ${estimated_cost:.6f} cost, "
                   f"{response_time_ms}ms response time")
        
        return ai_response


# Global service instance
openai_service = OpenAIService()