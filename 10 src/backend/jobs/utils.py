"""
Utility functions for job processing and geographic location standardization.

This module provides helper functions for normalizing location data,
processing geographic coordinates, and other job-related utilities.
"""

import re
import logging
from typing import Tuple, Optional, Dict, Any
from decimal import Decimal

logger = logging.getLogger('job_utils')


class LocationStandardizer:
    """
    Standardizes and normalizes geographic location data.
    """
    
    # Common location name variations and their standardized forms
    LOCATION_ALIASES = {
        # US Cities
        'nyc': 'New York City',
        'new york': 'New York City', 
        'ny': 'New York',
        'la': 'Los Angeles',
        'sf': 'San Francisco',
        'san fran': 'San Francisco',
        'chi': 'Chicago',
        'philly': 'Philadelphia',
        'dc': 'Washington',
        'washington dc': 'Washington',
        
        # UK Cities
        'london': 'London',
        'manchester': 'Manchester',
        'birmingham': 'Birmingham',
        'edinburgh': 'Edinburgh',
        'glasgow': 'Glasgow',
        
        # Common abbreviations
        'uk': 'United Kingdom',
        'us': 'United States',
        'usa': 'United States',
    }
    
    # Country code mappings
    COUNTRY_CODES = {
        'us': 'United States',
        'uk': 'United Kingdom', 
        'gb': 'United Kingdom',
        'ca': 'Canada',
        'au': 'Australia',
        'de': 'Germany',
        'fr': 'France',
        'es': 'Spain',
        'it': 'Italy',
        'nl': 'Netherlands',
    }
    
    @staticmethod
    def normalize_location_name(location_name: str) -> str:
        """
        Normalize a location name to a standard format.
        
        Args:
            location_name: Raw location name
            
        Returns:
            Normalized location name
        """
        if not location_name:
            return location_name
        
        # Clean and normalize
        normalized = location_name.strip().lower()
        
        # Remove common punctuation and extra spaces
        normalized = re.sub(r'[,\.]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Apply common aliases
        if normalized in LocationStandardizer.LOCATION_ALIASES:
            return LocationStandardizer.LOCATION_ALIASES[normalized]
        
        # Convert back to title case
        return normalized.title()
    
    @staticmethod
    def extract_country_from_area(area_list: list) -> str:
        """
        Extract and normalize country from Adzuna area array.
        
        Args:
            area_list: List of location components from most general to specific
            
        Returns:
            Normalized country name
        """
        if not area_list or not isinstance(area_list, list):
            return ''
        
        # First element is typically the country
        country = area_list[0].lower().strip()
        
        # Map country codes to full names
        if country in LocationStandardizer.COUNTRY_CODES:
            return LocationStandardizer.COUNTRY_CODES[country]
        
        return country.title()
    
    @staticmethod
    def validate_coordinates(latitude: Any, longitude: Any) -> Tuple[Optional[float], Optional[float]]:
        """
        Validate and normalize latitude/longitude coordinates.
        
        Args:
            latitude: Latitude value (could be string, int, float, or None)
            longitude: Longitude value (could be string, int, float, or None)
            
        Returns:
            Tuple of (validated_lat, validated_lng) or (None, None) if invalid
        """
        try:
            if latitude is None or longitude is None:
                return None, None
            
            lat = float(latitude)
            lng = float(longitude)
            
            # Validate ranges
            if not (-90 <= lat <= 90):
                logger.warning(f"Invalid latitude: {lat} (must be between -90 and 90)")
                return None, None
            
            if not (-180 <= lng <= 180):
                logger.warning(f"Invalid longitude: {lng} (must be between -180 and 180)")
                return None, None
            
            return lat, lng
            
        except (ValueError, TypeError, OverflowError) as e:
            logger.warning(f"Failed to parse coordinates ({latitude}, {longitude}): {e}")
            return None, None
    
    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate the distance between two points using the Haversine formula.
        
        Args:
            lat1, lng1: First point coordinates
            lat2, lng2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        import math
        
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return c * r
    
    @staticmethod
    def find_nearby_locations(target_lat: float, target_lng: float, 
                            locations: list, max_distance_km: float = 50) -> list:
        """
        Find locations within a specified distance from a target point.
        
        Args:
            target_lat: Target latitude
            target_lng: Target longitude  
            locations: List of location dictionaries with 'latitude' and 'longitude'
            max_distance_km: Maximum distance in kilometers
            
        Returns:
            List of locations within the specified distance
        """
        nearby = []
        
        for location in locations:
            lat = location.get('latitude')
            lng = location.get('longitude')
            
            if lat is None or lng is None:
                continue
            
            try:
                distance = LocationStandardizer.calculate_distance(
                    target_lat, target_lng, float(lat), float(lng)
                )
                
                if distance <= max_distance_km:
                    location_copy = location.copy()
                    location_copy['distance_km'] = round(distance, 2)
                    nearby.append(location_copy)
                    
            except (ValueError, TypeError):
                continue
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        return nearby


class JobDataCleaner:
    """
    Cleans and standardizes job data from external APIs.
    """
    
    @staticmethod
    def clean_job_title(title: str) -> str:
        """
        Clean and standardize job title.
        
        Args:
            title: Raw job title
            
        Returns:
            Cleaned job title
        """
        if not title:
            return title
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', title.strip())
        
        # Remove common spam patterns
        spam_patterns = [
            r'\$\d+[\-\+].*?per\s+(hour|day|week)',  # Salary in title
            r'work\s+from\s+home\s*[!\$]*',         # Work from home spam
            r'immediate\s+start\s*[!\$]*',          # Immediate start spam
            r'urgent\s*[!\$]*',                     # Urgent spam
        ]
        
        for pattern in spam_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove excessive punctuation
        cleaned = re.sub(r'[!]{2,}', '!', cleaned)
        cleaned = re.sub(r'[\$]{2,}', '$', cleaned)
        
        return cleaned.strip()
    
    @staticmethod
    def extract_experience_level(title: str, description: str = '') -> str:
        """
        Extract experience level from job title and description.
        
        Args:
            title: Job title
            description: Job description
            
        Returns:
            Experience level string
        """
        text = f"{title} {description}".lower()
        
        # Define experience level patterns
        patterns = {
            'entry': [r'entry\s*level', r'graduate', r'junior', r'trainee', r'intern'],
            'senior': [r'senior', r'sr\.', r'lead', r'principal', r'architect'],
            'manager': [r'manager', r'director', r'head\s+of', r'vp', r'vice\s+president'],
            'mid': [r'mid\s*level', r'intermediate', r'experienced'],
        }
        
        for level, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text):
                    return level
        
        return 'mid'  # Default to mid-level
    
    @staticmethod
    def extract_remote_type(title: str, description: str = '') -> str:
        """
        Extract remote work type from job title and description.
        
        Args:
            title: Job title
            description: Job description
            
        Returns:
            Remote type string
        """
        text = f"{title} {description}".lower()
        
        # Remote patterns
        remote_patterns = [
            r'remote', r'work\s+from\s+home', r'wfh', r'distributed',
            r'anywhere', r'location\s+independent'
        ]
        
        # Hybrid patterns  
        hybrid_patterns = [
            r'hybrid', r'flexible', r'part\s+remote', r'some\s+remote'
        ]
        
        # On-site patterns (explicit)
        onsite_patterns = [
            r'on\s*site', r'in\s+office', r'office\s+based'
        ]
        
        for pattern in remote_patterns:
            if re.search(pattern, text):
                return 'remote'
        
        for pattern in hybrid_patterns:
            if re.search(pattern, text):
                return 'hybrid'
        
        for pattern in onsite_patterns:
            if re.search(pattern, text):
                return 'on_site'
        
        return 'on_site'  # Default to on-site


def format_salary_range(min_salary: Optional[Decimal], max_salary: Optional[Decimal], 
                       currency: str = 'USD') -> str:
    """
    Format salary range for display.
    
    Args:
        min_salary: Minimum salary
        max_salary: Maximum salary
        currency: Currency code
        
    Returns:
        Formatted salary range string
    """
    if not min_salary and not max_salary:
        return 'Salary not specified'
    
    currency_symbols = {
        'USD': '$',
        'GBP': '£', 
        'EUR': '€',
        'CAD': 'C$',
        'AUD': 'A$',
    }
    
    symbol = currency_symbols.get(currency, currency)
    
    if min_salary and max_salary:
        return f"{symbol}{min_salary:,.0f} - {symbol}{max_salary:,.0f}"
    elif min_salary:
        return f"From {symbol}{min_salary:,.0f}"
    else:
        return f"Up to {symbol}{max_salary:,.0f}"


def truncate_text(text: str, max_length: int = 500, suffix: str = '...') -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix