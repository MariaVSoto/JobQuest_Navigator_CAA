"""
Resume models for SQLAlchemy
Supports both form-based and PDF-uploaded resumes
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Resume(BaseModel):
    """
    Resume model supporting both manual creation and PDF uploads
    """
    __tablename__ = 'resumes'
    __table_args__ = {'extend_existing': True}
    
    # Basic Information
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    
    # Personal Information (JSON field for flexibility)
    personal_info = Column(JSON, nullable=True)  # {fullName, email, phone, location, linkedin, website}
    
    # Content Sections
    summary = Column(Text, nullable=True)
    experience = Column(JSON, nullable=True)  # Array of experience objects
    education = Column(JSON, nullable=True)   # Array of education objects
    skills = Column(JSON, nullable=True)      # Array of skills
    projects = Column(JSON, nullable=True)    # Array of project objects
    
    # Targeting Information
    target_role = Column(String(200), nullable=True)
    target_industry = Column(String(100), nullable=True)
    keywords = Column(JSON, nullable=True)    # Array of keywords for ATS optimization
    
    # File Information (for PDF uploads)
    original_filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)      # MinIO/S3 path
    file_size = Column(Integer, nullable=True)          # File size in bytes
    file_type = Column(String(20), nullable=True)       # e.g., 'application/pdf'
    
    # Processing Status
    source_type = Column(String(20), default='manual')  # 'manual', 'pdf_upload', 'imported'
    processing_status = Column(String(20), default='completed')  # 'pending', 'processing', 'completed', 'failed'
    processing_error = Column(Text, nullable=True)      # Error message if processing failed
    
    # Metadata
    version = Column(Integer, default=1)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Resume(id='{self.id}', title='{self.title}', user_id='{self.user_id}')>"
    
    @property
    def status_display(self):
        """Human-readable processing status"""
        status_map = {
            'pending': 'Pending Processing',
            'processing': 'Processing PDF...',
            'completed': 'Ready',
            'failed': 'Processing Failed'
        }
        return status_map.get(self.processing_status, self.processing_status.title())
    
    @property
    def file_size_display(self):
        """Human-readable file size"""
        if not self.file_size:
            return None
        
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"


class ResumeVersion(BaseModel):
    """
    Resume version history for tracking changes
    """
    __tablename__ = 'resume_versions'
    __table_args__ = {'extend_existing': True}
    
    resume_id = Column(UUID(as_uuid=True), ForeignKey('resumes.id'), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    
    # Snapshot of resume data at this version
    title = Column(String(255), nullable=False)
    personal_info = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    experience = Column(JSON, nullable=True)
    education = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    projects = Column(JSON, nullable=True)
    target_role = Column(String(200), nullable=True)
    target_industry = Column(String(100), nullable=True)
    keywords = Column(JSON, nullable=True)
    
    # Version metadata
    change_summary = Column(Text, nullable=True)  # What changed in this version
    created_by_action = Column(String(50), nullable=True)  # 'manual_edit', 'pdf_reprocessing', 'ai_suggestion'
    
    # Relationships
    resume = relationship("Resume", back_populates="versions")
    
    def __repr__(self):
        return f"<ResumeVersion(resume_id='{self.resume_id}', version={self.version_number})>"


class ResumeProcessingLog(BaseModel):
    """
    Log entries for PDF processing and other resume operations
    """
    __tablename__ = 'resume_processing_logs'
    __table_args__ = {'extend_existing': True}
    
    resume_id = Column(UUID(as_uuid=True), ForeignKey('resumes.id'), nullable=False, index=True)
    operation = Column(String(50), nullable=False)  # 'pdf_upload', 'pdf_processing', 'data_extraction', 'validation'
    status = Column(String(20), nullable=False)     # 'started', 'completed', 'failed'
    
    # Processing details
    message = Column(Text, nullable=True)           # Success/error message
    processing_time = Column(Float, nullable=True)  # Time taken in seconds
    extracted_fields = Column(JSON, nullable=True)  # Fields successfully extracted from PDF
    
    # Technical details
    file_info = Column(JSON, nullable=True)         # File metadata (size, type, etc.)
    error_details = Column(JSON, nullable=True)     # Detailed error information
    
    # Relationships
    resume = relationship("Resume", back_populates="processing_logs")
    
    def __repr__(self):
        return f"<ResumeProcessingLog(resume_id='{self.resume_id}', operation='{self.operation}', status='{self.status}')>"


# Add reverse relationships
Resume.versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")
Resume.processing_logs = relationship("ResumeProcessingLog", back_populates="resume", cascade="all, delete-orphan")