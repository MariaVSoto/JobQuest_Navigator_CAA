"""
GraphQL queries module
"""

from .user import UserQuery
# from .job import JobQuery  # Temporarily disabled
from .resume_queries import ResumeQueries

__all__ = ["UserQuery", "ResumeQueries"]  # "JobQuery" temporarily disabled