"""
GraphQL mutations for Resume operations
"""

import strawberry
import base64
import json
import logging
from typing import List, Optional
from io import BytesIO
from datetime import datetime

from app.models.resume import Resume, ResumeProcessingLog
from app.services.storage import storage_service
from app.services.pdf_service import pdf_service
from app.core.database import AsyncSessionLocal
from app.graphql.types.resume_types import (
    CreateResumeInput, UploadResumeFileInput, ResumeResponse, 
    FileUploadResponse, ProcessPDFResponse
)

logger = logging.getLogger(__name__)


@strawberry.type
class ResumeMutations:
    """Resume-related GraphQL mutations"""
    
    @strawberry.mutation
    async def create_resume(self, input: CreateResumeInput, info) -> ResumeResponse:
        """Create a new resume from form data"""
        try:
            # Get user from context
            user = getattr(info.context, 'user', None)
            if not user:
                return ResumeResponse(
                    success=False,
                    errors=["Authentication required"]
                )
            
            # Validate input
            if not input.title or not input.title.strip():
                return ResumeResponse(
                    success=False,
                    errors=["Resume title is required"]
                )
            
            # Create resume data
            resume_data = {
                'user_id': user.id,
                'title': input.title.strip(),
                'personal_info': input.personal_info.__dict__ if input.personal_info else None,
                'summary': input.summary,
                'experience': [exp.__dict__ for exp in input.experience] if input.experience else None,
                'education': [edu.__dict__ for edu in input.education] if input.education else None,
                'skills': input.skills,
                'projects': [proj.__dict__ for proj in input.projects] if input.projects else None,
                'target_role': input.target_role,
                'target_industry': input.target_industry,
                'keywords': input.keywords,
                'source_type': 'manual',
                'processing_status': 'completed'
            }
            
            # Create resume in database
            async with AsyncSessionLocal() as session:
                resume = Resume(**resume_data)
                session.add(resume)
                await session.commit()
                await session.refresh(resume)
                
                logger.info(f"Resume created successfully: {resume.id}")
                
                return ResumeResponse(
                    success=True,
                    message="Resume created successfully",
                    resume_id=str(resume.id)
                )
                
        except Exception as e:
            logger.error(f"Error creating resume: {e}")
            return ResumeResponse(
                success=False,
                errors=[f"Failed to create resume: {str(e)}"]
            )
    
    @strawberry.mutation
    async def update_resume(self, resume_id: str, input: CreateResumeInput, info) -> ResumeResponse:
        """Update an existing resume"""
        try:
            # Get user from context
            user = getattr(info.context, 'user', None)
            if not user:
                return ResumeResponse(
                    success=False,
                    errors=["Authentication required"]
                )
            
            async with AsyncSessionLocal() as session:
                # Find resume
                resume = await session.get(Resume, resume_id)
                if not resume:
                    return ResumeResponse(
                        success=False,
                        errors=["Resume not found"]
                    )
                
                # Check ownership
                if str(resume.user_id) != str(user.id):
                    return ResumeResponse(
                        success=False,
                        errors=["Access denied"]
                    )
                
                # Update resume data
                resume.title = input.title.strip()
                resume.personal_info = input.personal_info.__dict__ if input.personal_info else None
                resume.summary = input.summary
                resume.experience = [exp.__dict__ for exp in input.experience] if input.experience else None
                resume.education = [edu.__dict__ for edu in input.education] if input.education else None
                resume.skills = input.skills
                resume.projects = [proj.__dict__ for proj in input.projects] if input.projects else None
                resume.target_role = input.target_role
                resume.target_industry = input.target_industry
                resume.keywords = input.keywords
                resume.version += 1
                resume.updated_at = datetime.utcnow()
                
                await session.commit()
                
                logger.info(f"Resume updated successfully: {resume.id}")
                
                return ResumeResponse(
                    success=True,
                    message="Resume updated successfully",
                    resume_id=str(resume.id)
                )
                
        except Exception as e:
            logger.error(f"Error updating resume: {e}")
            return ResumeResponse(
                success=False,
                errors=[f"Failed to update resume: {str(e)}"]
            )
    
    @strawberry.mutation
    async def upload_resume_file(self, input: UploadResumeFileInput, info) -> FileUploadResponse:
        """Upload a PDF resume file"""
        try:
            # Get user from context
            user = getattr(info.context, 'user', None)
            if not user:
                return FileUploadResponse(
                    success=False,
                    errors=["Authentication required"]
                )
            
            # Validate input
            if not input.title or not input.title.strip():
                return FileUploadResponse(
                    success=False,
                    errors=["Resume title is required"]
                )
            
            if not input.file_data or not input.filename:
                return FileUploadResponse(
                    success=False,
                    errors=["File data and filename are required"]
                )
            
            # Decode base64 file data
            try:
                file_data = base64.b64decode(input.file_data)
                file_stream = BytesIO(file_data)
            except Exception as e:
                return FileUploadResponse(
                    success=False,
                    errors=["Invalid file data encoding"]
                )
            
            # Upload file to storage
            try:
                file_path, file_metadata = storage_service.upload_resume_file(
                    user_id=str(user.id),
                    file_data=file_stream,
                    filename=input.filename,
                    content_type=input.content_type
                )
            except Exception as e:
                return FileUploadResponse(
                    success=False,
                    errors=[f"File upload failed: {str(e)}"]
                )
            
            # Create resume record in database
            async with AsyncSessionLocal() as session:
                resume_data = {
                    'user_id': user.id,
                    'title': input.title.strip(),
                    'source_type': 'pdf_upload',
                    'processing_status': 'pending',
                    'original_filename': input.filename,
                    'file_path': file_path,
                    'file_size': file_metadata['file_size'],
                    'file_type': file_metadata['content_type']
                }
                
                resume = Resume(**resume_data)
                session.add(resume)
                await session.commit()
                await session.refresh(resume)
                
                # Create processing log
                log = ResumeProcessingLog(
                    resume_id=resume.id,
                    operation='pdf_upload',
                    status='completed',
                    message='File uploaded successfully',
                    file_info=file_metadata
                )
                session.add(log)
                await session.commit()
                
                # Generate download URL
                download_url = storage_service.get_file_url(file_path)
                
                logger.info(f"Resume file uploaded successfully: {resume.id}")
                
                return FileUploadResponse(
                    success=True,
                    message="File uploaded successfully",
                    resume_id=str(resume.id),
                    processing_status="pending",
                    download_url=download_url
                )
                
        except Exception as e:
            logger.error(f"Error uploading resume file: {e}")
            return FileUploadResponse(
                success=False,
                errors=[f"Failed to upload file: {str(e)}"]
            )
    
    @strawberry.mutation
    async def process_pdf_resume(self, resume_id: str, info) -> ProcessPDFResponse:
        """Process uploaded PDF to extract resume data"""
        try:
            # Get user from context
            user = getattr(info.context, 'user', None)
            if not user:
                return ProcessPDFResponse(
                    success=False,
                    errors=["Authentication required"]
                )
            
            async with AsyncSessionLocal() as session:
                # Find resume
                resume = await session.get(Resume, resume_id)
                if not resume:
                    return ProcessPDFResponse(
                        success=False,
                        errors=["Resume not found"]
                    )
                
                # Check ownership
                if str(resume.user_id) != str(user.id):
                    return ProcessPDFResponse(
                        success=False,
                        errors=["Access denied"]
                    )
                
                # Check if it's a PDF upload
                if resume.source_type != 'pdf_upload' or not resume.file_path:
                    return ProcessPDFResponse(
                        success=False,
                        errors=["Resume is not a PDF upload"]
                    )
                
                # Update processing status
                resume.processing_status = 'processing'
                await session.commit()
                
                # Create processing log
                start_time = datetime.utcnow()
                log = ResumeProcessingLog(
                    resume_id=resume.id,
                    operation='pdf_processing',
                    status='started',
                    message='Starting PDF processing'
                )
                session.add(log)
                await session.commit()
                
                try:
                    # Download PDF file from storage
                    pdf_stream = storage_service.download_file(resume.file_path)
                    pdf_data = pdf_stream.read()
                    pdf_stream.close()
                    
                    # Extract text from PDF
                    pdf_text = pdf_service.extract_text_from_pdf(pdf_data)
                    
                    # Parse resume data from text
                    parsed_data = pdf_service.parse_resume_data(pdf_text)
                    
                    # Structure extracted data
                    extracted_data = {
                        'title': resume.title,
                        'personal_info': parsed_data.get('personal_info', {}),
                        'summary': parsed_data.get('summary'),
                        'experience': parsed_data.get('experience', []),
                        'education': parsed_data.get('education', []),
                        'skills': parsed_data.get('skills', []),
                        'projects': parsed_data.get('projects', [])
                    }
                    
                    # Update resume with extracted data
                    resume.personal_info = extracted_data.get('personal_info')
                    resume.summary = extracted_data.get('summary')
                    resume.experience = extracted_data.get('experience')
                    resume.education = extracted_data.get('education')
                    resume.skills = extracted_data.get('skills')
                    resume.projects = extracted_data.get('projects')
                    resume.processing_status = 'completed'
                    
                    # Calculate processing time
                    processing_time = (datetime.utcnow() - start_time).total_seconds()
                    
                    # Update processing log
                    log.status = 'completed'
                    log.message = 'PDF processing completed successfully'
                    log.processing_time = processing_time
                    log.extracted_fields = list(extracted_data.keys())
                    
                    await session.commit()
                    
                    logger.info(f"PDF processing completed for resume: {resume.id}")
                    
                    # Convert to CreateResumeInput format for response
                    response_data = CreateResumeInput(
                        title=extracted_data['title'],
                        personal_info=extracted_data.get('personal_info'),
                        summary=extracted_data.get('summary'),
                        experience=extracted_data.get('experience'),
                        education=extracted_data.get('education'),
                        skills=extracted_data.get('skills'),
                        projects=extracted_data.get('projects')
                    )
                    
                    return ProcessPDFResponse(
                        success=True,
                        message="PDF processed successfully",
                        # extracted_data=response_data,  # Temporarily disabled
                        processing_time=processing_time
                    )
                    
                except Exception as e:
                    # Update status on error
                    resume.processing_status = 'failed'
                    resume.processing_error = str(e)
                    
                    log.status = 'failed'
                    log.message = f'PDF processing failed: {str(e)}'
                    log.error_details = {'error': str(e)}
                    
                    await session.commit()
                    raise e
                
        except Exception as e:
            logger.error(f"Error processing PDF resume: {e}")
            return ProcessPDFResponse(
                success=False,
                errors=[f"Failed to process PDF: {str(e)}"]
            )
    
    @strawberry.mutation
    async def delete_resume(self, resume_id: str, info) -> ResumeResponse:
        """Delete a resume"""
        try:
            # Get user from context
            user = getattr(info.context, 'user', None)
            if not user:
                return ResumeResponse(
                    success=False,
                    errors=["Authentication required"]
                )
            
            async with AsyncSessionLocal() as session:
                # Find resume
                resume = await session.get(Resume, resume_id)
                if not resume:
                    return ResumeResponse(
                        success=False,
                        errors=["Resume not found"]
                    )
                
                # Check ownership
                if str(resume.user_id) != str(user.id):
                    return ResumeResponse(
                        success=False,
                        errors=["Access denied"]
                    )
                
                # Delete file from storage if exists
                if resume.file_path:
                    try:
                        storage_service.delete_file(resume.file_path)
                    except Exception as e:
                        logger.warning(f"Failed to delete file from storage: {e}")
                
                # Delete resume from database
                await session.delete(resume)
                await session.commit()
                
                logger.info(f"Resume deleted successfully: {resume_id}")
                
                return ResumeResponse(
                    success=True,
                    message="Resume deleted successfully"
                )
                
        except Exception as e:
            logger.error(f"Error deleting resume: {e}")
            return ResumeResponse(
                success=False,
                errors=[f"Failed to delete resume: {str(e)}"]
            )