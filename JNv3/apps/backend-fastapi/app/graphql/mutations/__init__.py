"""
GraphQL mutations module
"""

from .user import UserMutation
from .job import JobMutation
from .user_job import UserJobMutation
from .resume_mutations import ResumeMutations

__all__ = ["UserMutation", "JobMutation", "UserJobMutation", "ResumeMutations"]