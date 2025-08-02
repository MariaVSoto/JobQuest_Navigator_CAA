"""
Base model classes for SQLAlchemy
Maintains compatibility with Django model structure
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

# Create a custom MetaData instance to handle naming conflicts
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class BaseModel(Base):
    """
    Abstract base model with common fields
    Equivalent to Django's BaseModel
    """
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)