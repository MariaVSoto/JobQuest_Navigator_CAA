"""
Adzuna API Service for JobQuest Navigator.

This service handles all communication with the Adzuna API for fetching job listings.
Leverages the SecureAPIManager for safe API key handling and usage tracking.
"""

import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from django.conf import settings
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout

from core.security import api_manager, usage_tracker, APILimitExceededException

logger = logging.getLogger('adzuna_api')


class AdzunaAPIService:
    """
    A service to interact with the Adzuna API for fetching job listings.
    """
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    def __init__(self):
        self.session = requests.Session()
        # Set timeout and user agent
        self.session.headers.update({
            'User-Agent': 'JobQuest-Navigator/1.0 (Django Application)',
            'Accept': 'application/json',
        })
        self.timeout = 30  # 30 second timeout
    
    def _get_api_credentials(self) -> tuple[str, str]:
        """Get Adzuna API credentials securely."""
        try:
            app_id = api_manager.adzuna_app_id
            app_key = api_manager.adzuna_app_key
            return app_id, app_key
        except Exception as e:
            logger.error(f"Failed to get Adzuna API credentials: {e}")
            raise
    
    def search_jobs(
        self,
        country_code: str = 'us',
        page: int = 1,
        results_per_page: int = 50,
        what: Optional[str] = None,
        where: Optional[str] = None,
        max_days_old: Optional[int] = None,
        sort_by: str = 'date'
    ) -> Optional[Dict[str, Any]]:
        """
        Search for jobs using the Adzuna API.

        Args:
            country_code: The 2-letter country code (e.g., 'gb', 'us').
            page: The page number of the results (starts at 1).
            results_per_page: Number of results to return per page (max 50).
            what: The search query for job title or keywords.
            where: The location search query.
            max_days_old: Filter jobs posted within X days.
            sort_by: Sort results by 'date', 'relevance', or 'salary'.

        Returns:
            A dictionary containing the API response JSON, or None on failure.
        """
        # Check usage limits before making request
        try:
            usage_tracker.track_adzuna_usage()
        except APILimitExceededException as e:
            logger.error(f"Adzuna API usage limit exceeded: {e}")
            return None
        
        # Get credentials
        try:
            app_id, app_key = self._get_api_credentials()
        except Exception:
            return None
        
        # Build URL and parameters
        url = f"{self.BASE_URL}/{country_code}/search/{page}"
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'results_per_page': min(results_per_page, 50),  # Adzuna max is 50
            'content-type': 'application/json',
            'sort_by': sort_by
        }
        
        # Add optional parameters
        if what:
            params['what'] = what
        if where:
            params['where'] = where
        if max_days_old:
            params['max_days_old'] = max_days_old
        
        try:
            logger.info(f"Making Adzuna API request: {url} with params: {self._mask_params(params)}")
            
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results_count = len(data.get('results', []))
            
            logger.info(f"Adzuna API request successful: {results_count} jobs returned")
            return data
            
        except HTTPError as e:
            logger.error(f"Adzuna API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except ConnectionError as e:
            logger.error(f"Adzuna API connection error: {e}")
            return None
        except Timeout as e:
            logger.error(f"Adzuna API timeout: {e}")
            return None
        except RequestException as e:
            logger.error(f"Adzuna API request failed: {e}")
            return None
        except ValueError as e:
            logger.error(f"Adzuna API response parsing failed: {e}")
            return None
    
    def get_job_details(self, country_code: str, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific job.
        
        Args:
            country_code: The 2-letter country code.
            job_id: The Adzuna job ID.
            
        Returns:
            Job details dictionary or None on failure.
        """
        try:
            usage_tracker.track_adzuna_usage()
        except APILimitExceededException as e:
            logger.error(f"Adzuna API usage limit exceeded: {e}")
            return None
        
        try:
            app_id, app_key = self._get_api_credentials()
        except Exception:
            return None
        
        url = f"{self.BASE_URL}/{country_code}/jobs/{job_id}"
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'content-type': 'application/json'
        }
        
        try:
            logger.info(f"Getting Adzuna job details for ID: {job_id}")
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved job details for ID: {job_id}")
            return data
            
        except RequestException as e:
            logger.error(f"Failed to get Adzuna job details for ID {job_id}: {e}")
            return None
    
    def get_categories(self, country_code: str = 'us') -> Optional[Dict[str, Any]]:
        """
        Get available job categories from Adzuna.
        
        Args:
            country_code: The 2-letter country code.
            
        Returns:
            Categories dictionary or None on failure.
        """
        try:
            app_id, app_key = self._get_api_credentials()
        except Exception:
            return None
        
        url = f"{self.BASE_URL}/{country_code}/categories"
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'content-type': 'application/json'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to get Adzuna categories: {e}")
            return None
    
    def _mask_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive parameters for logging."""
        masked = params.copy()
        if 'app_key' in masked:
            masked['app_key'] = api_manager.get_masked_key(masked['app_key'])
        return masked
    
    def test_connection(self) -> bool:
        """
        Test the connection to Adzuna API.
        
        Returns:
            True if connection successful, False otherwise.
        """
        try:
            result = self.search_jobs(results_per_page=1)
            return result is not None
        except Exception as e:
            logger.error(f"Adzuna API connection test failed: {e}")
            return False