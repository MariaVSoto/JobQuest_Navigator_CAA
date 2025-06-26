"""
Job Synchronization Service for JobQuest Navigator.

This service orchestrates the fetching and saving of jobs from external APIs,
particularly Adzuna. It implements batch processing with proper error handling
and transaction management.
"""

import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

from django.db import transaction
from django.conf import settings

from jobs.services.adzuna_api import AdzunaAPIService
from jobs.mappers import AdzunaJobMapper
from jobs.models import Job
from core.security import APILimitExceededException

logger = logging.getLogger('job_sync')


class JobSyncStats:
    """Statistics for job synchronization operations."""
    
    def __init__(self):
        self.total_jobs_processed = 0
        self.jobs_created = 0
        self.jobs_updated = 0
        self.jobs_failed = 0
        self.errors = []
        self.start_time = datetime.now()
        self.end_time = None
    
    def add_success(self, created: bool):
        """Record a successful job processing."""
        self.total_jobs_processed += 1
        if created:
            self.jobs_created += 1
        else:
            self.jobs_updated += 1
    
    def add_failure(self, error_message: str):
        """Record a failed job processing."""
        self.total_jobs_processed += 1
        self.jobs_failed += 1
        self.errors.append(error_message)
    
    def finish(self):
        """Mark the sync operation as complete."""
        self.end_time = datetime.now()
    
    @property
    def duration(self) -> float:
        """Get the duration of the sync operation in seconds."""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary for logging/reporting."""
        return {
            'total_processed': self.total_jobs_processed,
            'created': self.jobs_created,
            'updated': self.jobs_updated,
            'failed': self.jobs_failed,
            'duration_seconds': self.duration,
            'success_rate': (self.total_jobs_processed - self.jobs_failed) / max(self.total_jobs_processed, 1),
            'errors': self.errors[:10]  # Limit errors for logging
        }


class JobSyncService:
    """
    Orchestrates the fetching and saving of jobs from external APIs.
    """
    
    def __init__(self):
        self.adzuna_api = AdzunaAPIService()
        self.mapper = AdzunaJobMapper()
    
    def sync_adzuna_jobs(
        self,
        country_code: str = 'us',
        what: str = None,
        where: str = None,
        max_pages: int = 5,
        results_per_page: int = 50
    ) -> JobSyncStats:
        """
        High-level method to sync multiple pages of jobs from Adzuna.
        
        Args:
            country_code: Country to search in
            what: Job keywords/title search
            where: Location search
            max_pages: Maximum number of pages to fetch
            results_per_page: Results per page (max 50 for Adzuna)
            
        Returns:
            JobSyncStats object with operation results
        """
        stats = JobSyncStats()
        
        logger.info(f"Starting Adzuna job sync: '{what}' in '{where}, {country_code}' "
                   f"(max {max_pages} pages, {results_per_page} per page)")
        
        try:
            for page in range(1, max_pages + 1):
                try:
                    page_stats = self._sync_single_page(
                        country_code=country_code,
                        page=page,
                        what=what,
                        where=where,
                        results_per_page=results_per_page
                    )
                    
                    # Aggregate page stats
                    stats.total_jobs_processed += page_stats.total_jobs_processed
                    stats.jobs_created += page_stats.jobs_created
                    stats.jobs_updated += page_stats.jobs_updated
                    stats.jobs_failed += page_stats.jobs_failed
                    stats.errors.extend(page_stats.errors)
                    
                    logger.info(f"Page {page} completed: {page_stats.total_jobs_processed} jobs processed")
                    
                    # Break if no results on this page
                    if page_stats.total_jobs_processed == 0:
                        logger.info(f"No results on page {page}, stopping pagination")
                        break
                        
                except APILimitExceededException as e:
                    logger.error(f"API limit exceeded on page {page}: {e}")
                    stats.add_failure(f"API limit exceeded on page {page}")
                    break
                except Exception as e:
                    logger.error(f"Failed to sync page {page}: {e}", exc_info=True)
                    stats.add_failure(f"Page {page} sync failed: {str(e)}")
                    continue
            
        finally:
            stats.finish()
            
        logger.info(f"Adzuna job sync completed: {stats.to_dict()}")
        return stats
    
    def _sync_single_page(
        self,
        country_code: str,
        page: int,
        what: str = None,
        where: str = None,
        results_per_page: int = 50
    ) -> JobSyncStats:
        """
        Sync a single page of jobs from Adzuna.
        
        Args:
            country_code: Country to search in
            page: Page number to fetch
            what: Job keywords/title search
            where: Location search
            results_per_page: Results per page
            
        Returns:
            JobSyncStats for this page
        """
        page_stats = JobSyncStats()
        
        # Fetch data from API
        response_data = self.adzuna_api.search_jobs(
            country_code=country_code,
            page=page,
            what=what,
            where=where,
            results_per_page=results_per_page
        )
        
        if not response_data or 'results' not in response_data:
            logger.warning(f"No results found for page {page} or API error occurred")
            return page_stats
        
        job_results = response_data['results']
        
        if not job_results:
            return page_stats
        
        # Process jobs in a single transaction for this page
        try:
            with transaction.atomic():
                for job_data in job_results:
                    job, created, message = self.mapper.map_and_save(job_data)
                    
                    if job:
                        page_stats.add_success(created)
                        logger.debug(f"Processed job {job_data.get('id')}: {message}")
                    else:
                        page_stats.add_failure(message)
                        logger.warning(f"Failed to process job {job_data.get('id')}: {message}")
                
                logger.info(f"Page {page} transaction completed: "
                           f"{page_stats.jobs_created} created, "
                           f"{page_stats.jobs_updated} updated, "
                           f"{page_stats.jobs_failed} failed")
                
        except Exception as e:
            # Transaction will be rolled back automatically
            error_msg = f"Transaction failed for page {page}. No jobs were saved. Error: {e}"
            logger.error(error_msg, exc_info=True)
            
            # Mark all jobs in this page as failed
            for job_data in job_results:
                page_stats.add_failure(f"Transaction rollback: {str(e)}")
        
        page_stats.finish()
        return page_stats
    
    def sync_job_details(self, job_ids: List[str], country_code: str = 'us') -> JobSyncStats:
        """
        Fetch detailed information for specific jobs and update database.
        
        Args:
            job_ids: List of Adzuna job IDs to fetch details for
            country_code: Country code for the jobs
            
        Returns:
            JobSyncStats object with operation results
        """
        stats = JobSyncStats()
        
        logger.info(f"Starting job details sync for {len(job_ids)} jobs")
        
        for job_id in job_ids:
            try:
                job_details = self.adzuna_api.get_job_details(country_code, job_id)
                
                if job_details:
                    job, created, message = self.mapper.map_and_save(job_details)
                    
                    if job:
                        stats.add_success(created)
                        logger.debug(f"Updated job details for {job_id}: {message}")
                    else:
                        stats.add_failure(f"Failed to save job details for {job_id}: {message}")
                else:
                    stats.add_failure(f"Failed to fetch job details for {job_id}")
                    
            except Exception as e:
                error_msg = f"Error processing job details for {job_id}: {e}"
                logger.error(error_msg, exc_info=True)
                stats.add_failure(error_msg)
        
        stats.finish()
        logger.info(f"Job details sync completed: {stats.to_dict()}")
        return stats
    
    def test_adzuna_connection(self) -> bool:
        """
        Test the connection to Adzuna API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            return self.adzuna_api.test_connection()
        except Exception as e:
            logger.error(f"Adzuna connection test failed: {e}")
            return False
    
    def get_sync_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get a summary of jobs synced in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Summary dictionary
        """
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        recent_jobs = Job.objects.filter(
            source='adzuna',
            created_at__gte=cutoff_date
        )
        
        return {
            'total_jobs': recent_jobs.count(),
            'active_jobs': recent_jobs.filter(is_active=True).count(),
            'unique_companies': recent_jobs.values('company').distinct().count(),
            'unique_locations': recent_jobs.values('location').distinct().count(),
            'date_range': f"Last {days} days",
            'cutoff_date': cutoff_date.isoformat(),
        }