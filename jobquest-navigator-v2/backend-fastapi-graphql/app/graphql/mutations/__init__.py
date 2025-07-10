"""
GraphQL mutations module
"""

from .user import UserMutation
from .job import JobMutation
from .user_job import UserJobMutation

__all__ = ["UserMutation", "JobMutation", "UserJobMutation"]