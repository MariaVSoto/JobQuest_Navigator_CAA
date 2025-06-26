"""
Data mappers for converting external API responses to Django models.

This module handles the mapping of flat API structures (like Adzuna)
to our relational Django model structure with proper data normalization.
"""

import logging
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, Tuple, Optional

from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from core.models import Company, Location
from jobs.models import Job, Category

logger = logging.getLogger('mappers')


def normalize_company_name(name: str) -> str:
    """
    Normalize company name to reduce duplicate entries.
    
    Args:
        name: Raw company name from API
        
    Returns:
        Normalized company name
    """
    if not name:
        return name
    
    # Convert to lowercase and strip whitespace
    normalized = name.lower().strip()
    
    # Remove common legal suffixes
    suffixes = [
        ', inc.', ', inc', ' inc.', ' inc',
        ', llc', ' llc', ', ltd.', ', ltd', ' ltd.', ' ltd',
        ', limited', ' limited', ', corporation', ' corporation',
        ', corp.', ', corp', ' corp.', ' corp',
        ', co.', ', co', ' co.', ' co',
        ', plc', ' plc', ', gmbh', ' gmbh'
    ]
    
    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
            break
    
    # Remove extra whitespace and normalize spacing
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized.title()  # Convert back to title case


def parse_salary(salary_value: Any) -> Optional[Decimal]:
    """
    Parse salary value from API response to Decimal.
    
    Args:
        salary_value: Salary value from API (could be int, float, str, or None)
        
    Returns:
        Decimal value or None if parsing fails
    """
    if salary_value is None:
        return None
    
    try:
        return Decimal(str(salary_value))
    except (InvalidOperation, ValueError, TypeError):
        logger.warning(f"Failed to parse salary value: {salary_value}")
        return None


def clean_optional_unique_field(value: Any) -> Optional[str]:
    """
    Converts empty strings or other 'empty' values to None for DB storage.
    
    This prevents unique constraint violations on nullable unique fields
    where empty strings would be treated as distinct values.
    
    Args:
        value: Field value that might be empty
        
    Returns:
        None if value is empty, otherwise the original value
    """
    if isinstance(value, str) and not value.strip():
        return None
    if value is None or value == '':
        return None
    return str(value)


def parse_adzuna_datetime(date_string: str) -> Optional[datetime]:
    """
    Parse Adzuna datetime string to Python datetime.
    
    Args:
        date_string: ISO format datetime string from Adzuna
        
    Returns:
        Parsed datetime or None if parsing fails
    """
    if not date_string:
        return None
    
    try:
        # Try Django's built-in parser first
        parsed = parse_datetime(date_string)
        if parsed:
            return parsed
        
        # Fallback for different formats
        # ISO format: "2013-11-08T18:07:39Z"
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
        
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse datetime: {date_string} - {e}")
        return None


def map_contract_time_to_job_type(contract_time: str) -> str:
    """
    Map Adzuna contract_time to our job_type choices.
    
    Args:
        contract_time: Adzuna contract_time value
        
    Returns:
        Mapped job_type value
    """
    mapping = {
        'full_time': 'full_time',
        'part_time': 'part_time',
        'contract': 'contract',
        'freelance': 'freelance',
        'internship': 'internship',
    }
    
    return mapping.get(contract_time, 'full_time')  # Default to full_time


class AdzunaJobMapper:
    """
    Maps Adzuna API job responses to Django models.
    """

    @staticmethod
    @transaction.atomic
    def map_and_save(job_data: Dict[str, Any]) -> Tuple[Optional[Job], bool, str]:
        """
        Map a single job listing from Adzuna API response and save to database.
        Uses a transaction to ensure all or nothing is saved.

        Args:
            job_data: Single job dictionary from Adzuna API response

        Returns:
            Tuple of (Job instance or None, created_boolean, status_message)
        """
        try:
            # Validate required fields
            adzuna_id = job_data.get('id')
            if not adzuna_id:
                return None, False, "Missing required 'id' field"
            
            title = job_data.get('title')
            if not title:
                return None, False, f"Job {adzuna_id} missing title"
            
            # 1. Map and save Location
            location_obj, loc_created = AdzunaJobMapper._get_or_create_location(job_data)
            if not location_obj:
                return None, False, f"Job {adzuna_id} failed to create location"
            
            # 2. Map and save Company
            company_obj, comp_created = AdzunaJobMapper._get_or_create_company(job_data)
            if not company_obj:
                return None, False, f"Job {adzuna_id} failed to create company"
            
            # 3. Map and save Category
            category_obj, cat_created = AdzunaJobMapper._get_or_create_category(job_data)
            
            # 4. Parse dates
            posted_date = parse_adzuna_datetime(job_data.get('created'))
            if not posted_date:
                posted_date = datetime.now()
                logger.warning(f"Job {adzuna_id} missing or invalid posted date, using current time")
            
            # 5. Map contract fields
            contract_time = job_data.get('contract_time', 'full_time')
            contract_type = job_data.get('contract_type', 'permanent')
            
            # 6. Map salary information
            salary_min = parse_salary(job_data.get('salary_min'))
            salary_max = parse_salary(job_data.get('salary_max'))
            
            # 7. Create or update Job
            job, job_created = Job.objects.update_or_create(
                external_id=str(adzuna_id),
                source='adzuna',
                defaults={
                    'title': title,
                    'description': job_data.get('description', ''),
                    'company': company_obj,
                    'location': location_obj,
                    'category': category_obj,
                    'external_url': job_data.get('redirect_url', ''),
                    'posted_date': posted_date,
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'salary_currency': 'USD',  # Adzuna doesn't always provide currency
                    'job_type': map_contract_time_to_job_type(contract_time),
                    'contract_type': contract_type,
                    'is_active': True,
                }
            )
            
            status = "created" if job_created else "updated"
            logger.info(f"{status.title()} job '{job.title}' (ID: {job.id}) from Adzuna ID {adzuna_id}")
            
            return job, job_created, f"Successfully {status} job"
            
        except Exception as e:
            error_msg = f"Failed to map and save Adzuna job ID {job_data.get('id', 'unknown')}: {e}"
            logger.error(error_msg, exc_info=True)
            return None, False, error_msg

    @staticmethod
    def _get_or_create_location(job_data: Dict[str, Any]) -> Tuple[Optional[Location], bool]:
        """
        Get or create Location from Adzuna job data.
        
        Args:
            job_data: Adzuna job dictionary
            
        Returns:
            Tuple of (Location instance or None, created_boolean)
        """
        try:
            latitude = job_data.get('latitude')
            longitude = job_data.get('longitude')
            location_data = job_data.get('location', {})
            display_name = location_data.get('display_name', '')
            
            if not display_name:
                logger.warning(f"Job {job_data.get('id')} missing location display_name")
                return AdzunaJobMapper._get_default_location(), False
            
            # Try to find existing location by coordinates first (more reliable)
            if latitude and longitude:
                # Look for location within ~1km radius (0.01 degrees ≈ 1km)
                tolerance = 0.01
                existing_locations = Location.objects.filter(
                    latitude__range=(latitude - tolerance, latitude + tolerance),
                    longitude__range=(longitude - tolerance, longitude + tolerance)
                )
                
                if existing_locations.exists():
                    location = existing_locations.first()
                    logger.debug(f"Found existing location by coordinates: {location.name}")
                    return location, False
            
            # Create new location or find by name
            location, created = Location.objects.get_or_create(
                name=display_name,
                defaults={
                    'city': display_name,  # Use display_name as city for now
                    'country': AdzunaJobMapper._extract_country_from_area(location_data) or 'Unknown',
                    'country_code': 'US' if 'San Francisco' in display_name else 'XX',  # Default based on location
                    'latitude': latitude,
                    'longitude': longitude,
                    'google_place_id': f"adzuna_{display_name.lower().replace(' ', '_')}_{hash(display_name) % 100000}",
                }
            )
            
            # Update coordinates if we found by name but didn't have coordinates
            if not created and latitude and longitude and not location.latitude:
                location.latitude = latitude
                location.longitude = longitude
                location.save(update_fields=['latitude', 'longitude'])
            
            return location, created
            
        except Exception as e:
            logger.error(f"Failed to create location for job {job_data.get('id')}: {e}")
            return AdzunaJobMapper._get_default_location(), False

    @staticmethod
    def _get_or_create_company(job_data: Dict[str, Any]) -> Tuple[Optional[Company], bool]:
        """
        Get or create Company from Adzuna job data.
        
        Args:
            job_data: Adzuna job dictionary
            
        Returns:
            Tuple of (Company instance or None, created_boolean)
        """
        try:
            company_data = job_data.get('company', {})
            company_display_name = company_data.get('display_name', '')
            
            if not company_display_name:
                logger.warning(f"Job {job_data.get('id')} missing company display_name")
                return AdzunaJobMapper._get_default_company(), False
            
            # Normalize the company name for lookup
            normalized_name = normalize_company_name(company_display_name)
            
            # Try to find existing company by normalized name
            company, created = Company.objects.get_or_create(
                name=normalized_name,
                defaults={
                    'slug': slugify(normalized_name),
                    'description': '',
                }
            )
            
            return company, created
            
        except Exception as e:
            logger.error(f"Failed to create company for job {job_data.get('id')}: {e}")
            return AdzunaJobMapper._get_default_company(), False

    @staticmethod
    def _get_or_create_category(job_data: Dict[str, Any]) -> Tuple[Optional[Category], bool]:
        """
        Get or create Category from Adzuna job data.
        
        Args:
            job_data: Adzuna job dictionary
            
        Returns:
            Tuple of (Category instance or None, created_boolean)
        """
        try:
            category_data = job_data.get('category', {})
            if not category_data:
                return None, False
            
            category_tag = category_data.get('tag', '')
            category_label = category_data.get('label', '')
            
            if not category_tag and not category_label:
                return None, False
            
            # Use tag as primary identifier (more stable than label)
            if category_tag:
                category, created = Category.objects.get_or_create(
                    adzuna_tag=category_tag,
                    defaults={
                        'name': category_label or category_tag.replace('-', ' ').title(),
                    }
                )
            else:
                # Fallback to label if no tag
                category, created = Category.objects.get_or_create(
                    name=category_label,
                    defaults={}
                )
            
            return category, created
            
        except Exception as e:
            logger.error(f"Failed to create category for job {job_data.get('id')}: {e}")
            return None, False

    @staticmethod
    def _extract_country_from_area(location_data: Dict[str, Any]) -> str:
        """
        Extract country from Adzuna location area array.
        
        Args:
            location_data: Location dictionary from Adzuna
            
        Returns:
            Country code or name
        """
        area = location_data.get('area', [])
        if area and isinstance(area, list) and len(area) > 0:
            # First element is usually the country
            return area[0]
        return ''

    @staticmethod
    def _get_default_location() -> Location:
        """Get or create a default location for jobs without location data."""
        location, _ = Location.objects.get_or_create(
            name="Unknown Location",
            defaults={
                'city': 'Unknown',
                'country': 'Unknown',
                'country_code': 'XX',
                'latitude': None,
                'longitude': None,
                'google_place_id': None,
            }
        )
        return location

    @staticmethod
    def _get_default_company() -> Company:
        """Get or create a default company for jobs without company data."""
        company, _ = Company.objects.get_or_create(
            name="Unknown Company",
            defaults={
                'slug': 'unknown-company',
                'description': "Company information not available",
            }
        )
        return company