"""
Pydantic schemas for AI service responses.

These schemas define the expected structure of AI-generated content,
providing validation and type safety for all AI operations.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CompanyResearch(BaseModel):
    """Schema for AI-generated company research summaries."""
    
    summary: str = Field(
        description="A concise, professional summary of the company (1-2 paragraphs)",
        min_length=50,
        max_length=1000
    )
    
    key_insights: List[str] = Field(
        description="2-4 key insights about the company's business, market position, or notable characteristics",
        min_length=2,
        max_length=4
    )
    
    industry_focus: str = Field(
        description="The primary industry or sector the company operates in",
        min_length=3,
        max_length=100
    )
    
    technologies: Optional[List[str]] = Field(
        default=None,
        description="Key technologies, tools, or platforms the company uses or develops",
        max_length=10
    )
    
    company_size_estimate: Optional[str] = Field(
        default=None,
        description="Estimated company size (e.g., 'startup', 'small', 'medium', 'large', 'enterprise')"
    )


class JobSuggestion(BaseModel):
    """Schema for AI-generated job suggestions and recommendations."""
    
    recommendation_score: float = Field(
        description="AI confidence score for this recommendation (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    reasoning: str = Field(
        description="Explanation of why this job matches the user's profile",
        min_length=20,
        max_length=500
    )
    
    skill_match: List[str] = Field(
        description="Skills from user's profile that match this job",
        max_length=15
    )
    
    skill_gaps: List[str] = Field(
        description="Skills the user might need to develop for this role",
        max_length=10
    )
    
    career_growth_potential: str = Field(
        description="Assessment of career growth potential in this role",
        max_length=200
    )


class MarketAnalysis(BaseModel):
    """Schema for AI-generated market and industry analysis."""
    
    market_overview: str = Field(
        description="Overview of the current market conditions and trends",
        min_length=100,
        max_length=800
    )
    
    key_trends: List[str] = Field(
        description="3-5 key trends shaping this market or industry",
        min_length=3,
        max_length=5
    )
    
    growth_outlook: str = Field(
        description="Assessment of growth prospects and future outlook",
        max_length=300
    )
    
    opportunities: List[str] = Field(
        description="Emerging opportunities in this space",
        max_length=8
    )
    
    challenges: List[str] = Field(
        description="Key challenges and risks to be aware of",
        max_length=8
    )
    
    salary_insights: Optional[str] = Field(
        default=None,
        description="Insights about salary trends and compensation",
        max_length=300
    )


class AIValidationError(Exception):
    """Custom exception for AI response validation failures."""
    pass


class AIServiceError(Exception):
    """Base exception for AI service operations."""
    pass


class AIContentGenerationError(AIServiceError):
    """Exception raised when content generation fails."""
    pass


class AIRateLimitError(AIServiceError):
    """Exception raised when API rate limits are exceeded."""
    pass


class AIModelNotAvailableError(AIServiceError):
    """Exception raised when requested AI model is not available."""
    pass