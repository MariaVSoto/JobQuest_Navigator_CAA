"""
Proxy resolvers for gradual migration from Django to FastAPI
Calls original Django GraphQL endpoint when needed
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class DjangoGraphQLProxy:
    """
    Proxy client for calling Django GraphQL endpoint during migration
    """
    
    def __init__(self):
        self.django_endpoint = settings.django_graphql_endpoint
        self.session = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def execute_query(
        self, 
        query: str, 
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute GraphQL query against Django endpoint.
        
        Args:
            query: GraphQL query string
            variables: Query variables
            headers: Additional headers (for auth)
            
        Returns:
            GraphQL response dict
        """
        try:
            session = await self.get_session()
            
            payload = {
                "query": query,
                "variables": variables or {}
            }
            
            request_headers = {
                "Content-Type": "application/json"
            }
            if headers:
                request_headers.update(headers)
            
            async with session.post(
                self.django_endpoint,
                json=payload,
                headers=request_headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Django GraphQL error {response.status}: {error_text}")
                    return {
                        "errors": [{"message": f"Django endpoint error: {response.status}"}]
                    }
                    
        except asyncio.TimeoutError:
            logger.error("Django GraphQL request timeout")
            return {
                "errors": [{"message": "Django endpoint timeout"}]
            }
        except Exception as e:
            logger.error(f"Django GraphQL request failed: {str(e)}")
            return {
                "errors": [{"message": f"Django endpoint error: {str(e)}"}]
            }


# Global proxy instance
django_proxy = DjangoGraphQLProxy()


async def proxy_user_query(
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    auth_header: Optional[str] = None
) -> Dict[str, Any]:
    """
    Proxy user-related queries to Django.
    
    Example queries:
    - User profile data
    - User preferences
    - Activity logs
    """
    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header
    
    return await django_proxy.execute_query(query, variables, headers)


async def proxy_job_query(
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    auth_header: Optional[str] = None
) -> Dict[str, Any]:
    """
    Proxy job-related queries to Django.
    
    Example queries:
    - Job listings with location data
    - Skills and categories
    - Application status
    """
    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header
    
    return await django_proxy.execute_query(query, variables, headers)


async def proxy_mutation(
    mutation: str,
    variables: Optional[Dict[str, Any]] = None,
    auth_header: Optional[str] = None
) -> Dict[str, Any]:
    """
    Proxy mutations to Django.
    
    Example mutations:
    - User registration/profile updates
    - Job applications
    - Saved jobs
    """
    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header
    
    return await django_proxy.execute_query(mutation, variables, headers)


# Predefined query templates for common operations
DJANGO_QUERIES = {
    "user_profile": """
        query GetUserProfile($id: ID!) {
            user(id: $id) {
                id
                email
                username
                fullName
                dateOfBirth
                bio
                currentJobTitle
                yearsOfExperience
                industry
                careerLevel
                jobSearchStatus
                preferredWorkType
                dateJoined
                lastLogin
            }
        }
    """,
    
    "jobs_with_location": """
        query GetJobsWithLocation(
            $search: String, 
            $location: String,
            $limit: Int,
            $offset: Int
        ) {
            jobs(
                search: $search,
                location: $location,
                limit: $limit,
                offset: $offset
            ) {
                id
                title
                description
                company {
                    id
                    name
                    logoUrl
                }
                location {
                    id
                    name
                    city
                    state
                    latitude
                    longitude
                }
                salaryMin
                salaryMax
                jobType
                remoteType
                postedDate
                isSaved
                isApplied
            }
        }
    """,
    
    "user_applications": """
        query GetUserApplications {
            myApplications {
                id
                status
                appliedDate
                lastUpdated
                job {
                    id
                    title
                    company {
                        name
                        logoUrl
                    }
                    location {
                        name
                        city
                        state
                    }
                }
            }
        }
    """,
    
    "apply_to_job": """
        mutation ApplyToJob($jobId: ID!, $coverLetter: String, $notes: String) {
            applyToJob(jobId: $jobId, coverLetter: $coverLetter, notes: $notes) {
                success
                errors
                application {
                    id
                    status
                    appliedDate
                }
            }
        }
    """,
    
    "save_job": """
        mutation SaveJob($jobId: ID!) {
            saveJob(jobId: $jobId) {
                success
                errors
                savedJob {
                    id
                    savedDate
                }
            }
        }
    """
}


async def get_user_from_django(user_id: str, auth_header: str) -> Optional[Dict[str, Any]]:
    """Get user data from Django endpoint."""
    result = await proxy_user_query(
        DJANGO_QUERIES["user_profile"],
        {"id": user_id},
        auth_header
    )
    
    if "errors" in result:
        logger.warning(f"Django user query failed: {result['errors']}")
        return None
        
    return result.get("data", {}).get("user")


async def get_jobs_from_django(
    search: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    auth_header: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Get jobs with location data from Django endpoint."""
    result = await proxy_job_query(
        DJANGO_QUERIES["jobs_with_location"],
        {
            "search": search,
            "location": location,
            "limit": limit,
            "offset": offset
        },
        auth_header
    )
    
    if "errors" in result:
        logger.warning(f"Django jobs query failed: {result['errors']}")
        return None
        
    return result.get("data", {}).get("jobs")


async def get_user_applications_from_django(auth_header: str) -> Optional[Dict[str, Any]]:
    """Get user applications from Django endpoint."""
    result = await proxy_job_query(
        DJANGO_QUERIES["user_applications"],
        {},
        auth_header
    )
    
    if "errors" in result:
        logger.warning(f"Django applications query failed: {result['errors']}")
        return None
        
    return result.get("data", {}).get("myApplications")


async def apply_to_job_via_django(
    job_id: str,
    cover_letter: Optional[str] = None,
    notes: Optional[str] = None,
    auth_header: str = None
) -> Dict[str, Any]:
    """Apply to job via Django endpoint."""
    return await proxy_mutation(
        DJANGO_QUERIES["apply_to_job"],
        {
            "jobId": job_id,
            "coverLetter": cover_letter,
            "notes": notes
        },
        auth_header
    )


async def save_job_via_django(job_id: str, auth_header: str) -> Dict[str, Any]:
    """Save job via Django endpoint."""
    return await proxy_mutation(
        DJANGO_QUERIES["save_job"],
        {"jobId": job_id},
        auth_header
    )


# Cleanup function for application shutdown
async def cleanup_proxy():
    """Clean up proxy resources."""
    await django_proxy.close()