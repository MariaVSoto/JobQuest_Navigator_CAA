"""
Structured response types for AI services.

This module defines the standardized response format for all AI operations,
including token usage tracking and metadata.
"""

from dataclasses import dataclass
from typing import Union, Optional
from datetime import datetime

from .schemas import CompanyResearch, JobSuggestion, MarketAnalysis


@dataclass
class AIResponse:
    """
    Standardized response structure for all AI service operations.
    
    This response type ensures consistent token tracking, cost calculation,
    and metadata across all AI-powered features.
    """
    
    # The validated AI-generated content (one of our Pydantic schemas)
    data: Union[CompanyResearch, JobSuggestion, MarketAnalysis]
    
    # Model and request metadata
    model_used: str
    prompt_version: str
    
    # Token usage and cost information
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    
    # Timing information
    response_time_ms: int
    generated_at: datetime
    
    # Optional fields with defaults
    request_id: Optional[str] = None
    validation_passed: bool = True
    validation_warnings: list = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.validation_warnings is None:
            self.validation_warnings = []
        
        if self.total_tokens == 0:
            self.total_tokens = self.prompt_tokens + self.completion_tokens
    
    @property
    def cost_per_token(self) -> float:
        """Calculate cost per token for this request."""
        return self.estimated_cost / self.total_tokens if self.total_tokens > 0 else 0.0
    
    @property
    def tokens_per_second(self) -> float:
        """Calculate token generation rate."""
        if self.response_time_ms > 0:
            return (self.total_tokens * 1000) / self.response_time_ms
        return 0.0
    
    def to_dict(self) -> dict:
        """Convert response to dictionary for logging or storage."""
        return {
            'model_used': self.model_used,
            'prompt_version': self.prompt_version,
            'request_id': self.request_id,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'estimated_cost': self.estimated_cost,
            'response_time_ms': self.response_time_ms,
            'generated_at': self.generated_at.isoformat(),
            'validation_passed': self.validation_passed,
            'validation_warnings': self.validation_warnings,
            'cost_per_token': self.cost_per_token,
            'tokens_per_second': self.tokens_per_second,
        }