"""
Main GraphQL schema combining all types, queries and mutations
Strawberry GraphQL implementation maintaining compatibility with original Graphene schema
"""

import strawberry
from typing import List, Optional
from datetime import datetime

# Temporarily disable problematic imports to fix schema loading
# from app.graphql.queries.user import UserQuery  
# from app.graphql.queries.job import JobQuery
# from app.graphql.mutations.user import UserMutation
# from app.graphql.mutations.job import JobMutation
# from app.graphql.mutations.user_job import UserJobMutation
# from app.graphql.resolvers.hybrid import HybridQuery, HybridMutation


@strawberry.type
class User:
    id: str
    email: str
    username: str
    fullName: Optional[str] = None
    bio: Optional[str] = None
    currentJobTitle: Optional[str] = None
    yearsOfExperience: Optional[int] = None
    industry: Optional[str] = None
    careerLevel: Optional[str] = None
    jobSearchStatus: Optional[str] = None
    preferredWorkType: Optional[str] = None

@strawberry.type
class Company:
    id: str
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    logoUrl: Optional[str] = None
    industry: Optional[str] = None
    companySize: Optional[str] = None
    foundedYear: Optional[int] = None

@strawberry.type
class Job:
    id: str
    title: str
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    locationText: Optional[str] = None
    salaryMin: Optional[float] = None
    salaryMax: Optional[float] = None
    salaryCurrency: str = "USD"
    salaryPeriod: str = "yearly"
    jobType: str = "full_time"
    contractType: str = "permanent"
    experienceLevel: Optional[str] = None
    remoteType: str = "on_site"
    userInput: bool = True
    source: str = "user_input"
    postedDate: datetime
    expiresDate: Optional[datetime] = None
    company: Optional[Company] = None
    isSaved: bool = False
    isApplied: bool = False

@strawberry.type
class JobApplication:
    id: str
    userId: str
    jobId: str
    status: str = "applied"
    appliedDate: datetime
    lastUpdated: datetime
    coverLetter: Optional[str] = None
    notes: Optional[str] = None
    optimizedResumeData: Optional[str] = None
    aiSuggestions: Optional[str] = None
    skillsAnalysis: Optional[str] = None
    job: Optional[Job] = None

@strawberry.type
class SavedJob:
    id: str
    userId: str
    jobId: str
    savedDate: datetime
    notes: Optional[str] = None
    job: Optional[Job] = None

@strawberry.type
class SecureAuthResponse:
    """Response for secure authentication operations"""
    success: bool
    user: Optional[User] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None

@strawberry.type
class SessionValidationResponse:
    """Response for session validation"""
    valid: bool
    user: Optional[User] = None
    message: Optional[str] = None

@strawberry.type
class Query:
    """
    Root Query type - minimal implementation to get schema working
    """
    
    @strawberry.field
    async def hello(self) -> str:
        return "Hello from JobQuest Navigator v2!"
    
    @strawberry.field
    async def migration_status(self) -> str:
        """Check which features are using FastAPI vs Django"""
        return "Migration in progress - basic schema loaded"
    
    @strawberry.field
    async def me(self) -> Optional[User]:
        """Get current user - minimal implementation for demo"""
        # For demo purposes, return a mock user
        # In production, this would get user from authentication context
        return User(
            id="demo-user-id",
            email="test@example.com",
            username="testuser",
            fullName="Test User",
            bio="Demo user for testing",
            currentJobTitle="Software Developer",
            yearsOfExperience=5,
            industry="Technology",
            careerLevel="mid",
            jobSearchStatus="actively_looking",
            preferredWorkType="hybrid"
        )
    
    @strawberry.field
    async def jobs(
        self, 
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
        search: Optional[str] = None,
        location: Optional[str] = None,
        jobType: Optional[str] = None,
        experienceLevel: Optional[str] = None,
        remoteType: Optional[str] = None,
        userCreated: Optional[bool] = None
    ) -> List[Job]:
        """Get job listings with filtering - real database implementation with Redis caching"""
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import select, and_, or_
        from app.models import Job as JobModel, Company as CompanyModel
        from app.services.cache_service import get_cache_service
        import json
        from datetime import datetime
        
        # Get cache service
        cache_service = await get_cache_service()
        
        # Try to get results from cache first
        cached_results = await cache_service.get_job_search_results(
            limit=limit,
            offset=offset,
            search=search,
            location=location,
            job_type=jobType,
            experience_level=experienceLevel,
            remote_type=remoteType,
            user_created=userCreated
        )
        
        if cached_results:
            print(f"🚀 Returning {len(cached_results['results'])} cached job results")
            # Reconstruct GraphQL objects from cached data
            jobs = []
            for job_data in cached_results['results']:
                # Create Company object from cached company data
                company = Company(
                    id=job_data['company']['id'],
                    name=job_data['company']['name'],
                    description=job_data['company']['description'],
                    website=job_data['company']['website'],
                    logoUrl=job_data['company']['logoUrl'],
                    industry=job_data['company']['industry'],
                    companySize=job_data['company']['companySize'],
                    foundedYear=job_data['company']['foundedYear']
                )
                
                # Create Job object with Company
                job = Job(
                    id=job_data['id'],
                    title=job_data['title'],
                    description=job_data['description'],
                    requirements=job_data['requirements'],
                    benefits=job_data['benefits'],
                    locationText=job_data['locationText'],
                    salaryMin=job_data['salaryMin'],
                    salaryMax=job_data['salaryMax'],
                    salaryCurrency=job_data['salaryCurrency'],
                    salaryPeriod=job_data['salaryPeriod'],
                    jobType=job_data['jobType'],
                    contractType=job_data['contractType'],
                    experienceLevel=job_data['experienceLevel'],
                    remoteType=job_data['remoteType'],
                    userInput=job_data['userInput'],
                    source=job_data['source'],
                    postedDate=datetime.fromisoformat(job_data['postedDate']) if job_data['postedDate'] else None,
                    expiresDate=datetime.fromisoformat(job_data['expiresDate']) if job_data['expiresDate'] else None,
                    company=company,
                    isSaved=job_data['isSaved'],
                    isApplied=job_data['isApplied']
                )
                jobs.append(job)
            return jobs
        
        # Get database session
        async def get_db_session():
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                return session
        
        db = await get_db_session()
        
        try:
            # Build query with filters
            base_conditions = [JobModel.is_active == True]
            
            # Apply user-created filter if specified
            if userCreated is not None:
                if userCreated:
                    # Only show user-created jobs
                    base_conditions.append(JobModel.user_input == True)
                else:
                    # Only show external/API jobs (not user-created)
                    base_conditions.append(JobModel.user_input == False)
            else:
                # Default: show user-created jobs only (maintaining current behavior)
                base_conditions.append(JobModel.user_input == True)
            
            query = select(JobModel, CompanyModel).join(CompanyModel).where(
                and_(*base_conditions)
            )
            
            # Apply search filter with full-text search capabilities
            if search:
                # Use PostgreSQL full-text search for better performance and relevance
                # Fall back to ILIKE for basic string matching
                from sqlalchemy import text, func
                
                # Full-text search using the GIN indexes we created
                search_terms = search.replace("'", "''")  # Escape single quotes
                
                # Use PostgreSQL ts_query and ts_rank for advanced search
                search_filter = or_(
                    # Full-text search on job title with ranking
                    func.to_tsvector('english', JobModel.title).op('@@')(
                        func.plainto_tsquery('english', search_terms)
                    ),
                    # Full-text search on job description with ranking
                    func.to_tsvector('english', JobModel.description).op('@@')(
                        func.plainto_tsquery('english', search_terms)
                    ),
                    # Full-text search on company name with ranking
                    func.to_tsvector('english', CompanyModel.name).op('@@')(
                        func.plainto_tsquery('english', search_terms)
                    ),
                    # Fallback to ILIKE for exact matching
                    JobModel.title.ilike(f"%{search}%"),
                    JobModel.description.ilike(f"%{search}%"),
                    CompanyModel.name.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
                
                # Order by relevance score for full-text search results
                relevance_score = (
                    func.ts_rank(func.to_tsvector('english', JobModel.title), func.plainto_tsquery('english', search_terms)) * 2.0 +
                    func.ts_rank(func.to_tsvector('english', JobModel.description), func.plainto_tsquery('english', search_terms)) * 1.0 +
                    func.ts_rank(func.to_tsvector('english', CompanyModel.name), func.plainto_tsquery('english', search_terms)) * 1.5
                ).label('relevance')
                
                # Add relevance score to query and order by it
                query = query.add_columns(relevance_score).order_by(relevance_score.desc())
            else:
                # Default ordering by posted date when no search
                query = query.order_by(JobModel.posted_date.desc())
            
            # Apply location filter
            if location:
                query = query.where(JobModel.location_text.ilike(f"%{location}%"))
            
            # Apply job type filter
            if jobType:
                query = query.where(JobModel.job_type == jobType)
            
            # Apply experience level filter
            if experienceLevel:
                query = query.where(JobModel.experience_level == experienceLevel)
            
            # Apply remote type filter
            if remoteType:
                query = query.where(JobModel.remote_type == remoteType)
            
            # Apply pagination
            query = query.offset(offset or 0).limit(limit or 20)
            
            # Execute query
            result = await db.execute(query)
            job_data = result.fetchall()
            
            # Convert to GraphQL types
            jobs = []
            for row in job_data:
                # Handle both search results (with relevance) and regular results
                if search and len(row) == 3:  # job_model, company_model, relevance_score
                    job_model, company_model, relevance_score = row
                    print(f"🎯 Found job '{job_model.title}' with relevance score: {relevance_score:.3f}")
                else:  # job_model, company_model
                    job_model, company_model = row[0], row[1]
                # Create Company GraphQL type
                company = Company(
                    id=str(company_model.id),
                    name=company_model.name,
                    description=company_model.description,
                    website=company_model.website,
                    logoUrl=company_model.logo_url,
                    industry=company_model.industry,
                    companySize=company_model.company_size,
                    foundedYear=company_model.founded_year
                )
                
                # Create Job GraphQL type
                job = Job(
                    id=str(job_model.id),
                    title=job_model.title,
                    description=job_model.description,
                    requirements=job_model.requirements,
                    benefits=job_model.benefits,
                    locationText=job_model.location_text,
                    salaryMin=job_model.salary_min,
                    salaryMax=job_model.salary_max,
                    salaryCurrency=job_model.salary_currency,
                    salaryPeriod=job_model.salary_period,
                    jobType=job_model.job_type,
                    contractType=job_model.contract_type,
                    experienceLevel=job_model.experience_level,
                    remoteType=job_model.remote_type,
                    userInput=job_model.user_input,
                    source=job_model.source,
                    postedDate=job_model.posted_date,
                    expiresDate=job_model.expires_date,
                    company=company,
                    isSaved=False,  # TODO: Check if user has saved this job
                    isApplied=False  # TODO: Check if user has applied to this job
                )
                jobs.append(job)
            
            # Cache the results for future requests
            if jobs:
                job_dicts = []
                for job in jobs:
                    job_dict = {
                        "id": job.id,
                        "title": job.title,
                        "description": job.description,
                        "requirements": job.requirements,
                        "benefits": job.benefits,
                        "locationText": job.locationText,
                        "salaryMin": job.salaryMin,
                        "salaryMax": job.salaryMax,
                        "salaryCurrency": job.salaryCurrency,
                        "salaryPeriod": job.salaryPeriod,
                        "jobType": job.jobType,
                        "contractType": job.contractType,
                        "experienceLevel": job.experienceLevel,
                        "remoteType": job.remoteType,
                        "userInput": job.userInput,
                        "source": job.source,
                        "postedDate": job.postedDate.isoformat() if job.postedDate else None,
                        "expiresDate": job.expiresDate.isoformat() if job.expiresDate else None,
                        "company": {
                            "id": job.company.id,
                            "name": job.company.name,
                            "description": job.company.description,
                            "website": job.company.website,
                            "logoUrl": job.company.logoUrl,
                            "industry": job.company.industry,
                            "companySize": job.company.companySize,
                            "foundedYear": job.company.foundedYear
                        },
                        "isSaved": job.isSaved,
                        "isApplied": job.isApplied
                    }
                    job_dicts.append(job_dict)
                
                # Cache the job search results
                await cache_service.set_job_search_results(
                    results=job_dicts,
                    limit=limit,
                    offset=offset,
                    search=search,
                    location=location,
                    job_type=jobType,
                    experience_level=experienceLevel,
                    remote_type=remoteType,
                    user_created=userCreated
                )
                print(f"💾 Cached {len(job_dicts)} job search results")
            
            return jobs
            
        except Exception as e:
            print(f"Error fetching jobs: {e}")
            return []  # Return empty list on error
        finally:
            await db.close()
    
    @strawberry.field
    async def job(self, id: str) -> Optional[Job]:
        """Get a specific job by ID - demo implementation"""
        # For demo, return the first job from the jobs query
        query_instance = Query()
        jobs = await query_instance.jobs(limit=1)
        return jobs[0] if jobs else None
    
    @strawberry.field
    async def user(self, id: str) -> Optional[User]:
        """Get a specific user by ID - demo implementation"""
        # For demo purposes, return a mock user
        # In production, this would query the database
        return User(
            id=id,
            email="user@example.com",
            username="sampleuser",
            fullName="Sample User",
            bio="Sample user for testing",
            currentJobTitle="Software Engineer",
            yearsOfExperience=3,
            industry="Technology",
            careerLevel="mid",
            jobSearchStatus="passively_looking",
            preferredWorkType="remote"
        )
    
    @strawberry.field
    async def applications(
        self, 
        userId: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0
    ) -> List[JobApplication]:
        """Get job applications with filtering - demo implementation"""
        import uuid
        from datetime import datetime, timedelta
        
        try:
            # Get demo jobs to reference - with error handling
            query_instance = Query()
            demo_jobs = []
            try:
                demo_jobs = await query_instance.jobs(limit=3)
            except Exception as e:
                print(f"Warning: Could not fetch demo jobs: {e}")
                # Create fallback job data for applications
                demo_jobs = [
                    Job(
                        id=str(uuid.uuid4()),
                        title="Senior Frontend Developer",
                        description="Build amazing user interfaces with React and TypeScript. Work with a dynamic team on cutting-edge projects.",
                        locationText="San Francisco, CA",
                        jobType="FULL_TIME",
                        experienceLevel="SENIOR",
                        salaryMin=120000,
                        salaryMax=150000,
                        salaryCurrency="USD",
                        userInput=False,
                        company=Company(
                            id=str(uuid.uuid4()),
                            name="TechCorp",
                            description="Leading technology company",
                            industry="Technology"
                        )
                    ),
                    Job(
                        id=str(uuid.uuid4()),
                        title="Full Stack Engineer",
                        description="Join our engineering team to build scalable web applications using React, Node.js, and cloud technologies.",
                        locationText="Austin, TX",
                        jobType="FULL_TIME",
                        experienceLevel="MID_LEVEL",
                        salaryMin=90000,
                        salaryMax=110000,
                        salaryCurrency="USD",
                        userInput=False,
                        company=Company(
                            id=str(uuid.uuid4()),
                            name="StartupXYZ",
                            description="Fast-growing startup",
                            industry="Technology"
                        )
                    ),
                    Job(
                        id=str(uuid.uuid4()),
                        title="Python Backend Developer",
                        description="Develop robust backend systems using Python, FastAPI, and PostgreSQL. Experience with cloud platforms preferred.",
                        locationText="Remote",
                        jobType="FULL_TIME",
                        experienceLevel="MID_LEVEL",
                        salaryMin=95000,
                        salaryMax=125000,
                        salaryCurrency="USD",
                        userInput=False,
                        company=Company(
                            id=str(uuid.uuid4()),
                            name="CloudTech",
                            description="Cloud-first technology company",
                            industry="Technology"
                        )
                    )
                ]
            
            # Create mock applications
            mock_applications = [
                JobApplication(
                    id=str(uuid.uuid4()),
                    userId=userId or "demo-user-id",
                    jobId=demo_jobs[0].id,
                    status="applied",
                    appliedDate=datetime.now() - timedelta(days=3),
                    lastUpdated=datetime.now() - timedelta(days=3),
                    coverLetter="I am very interested in this position and believe my skills in React and Node.js make me a perfect fit.",
                    notes="Applied through company website",
                    job=demo_jobs[0]
                ),
                JobApplication(
                    id=str(uuid.uuid4()),
                    userId=userId or "demo-user-id",
                    jobId=demo_jobs[1].id,
                    status="interview",
                    appliedDate=datetime.now() - timedelta(days=10),
                    lastUpdated=datetime.now() - timedelta(days=2),
                    coverLetter="As a senior developer with 8+ years of experience, I would love to contribute to your team.",
                    notes="Phone interview scheduled for next week",
                    aiSuggestions='{"keywords": ["React", "TypeScript", "Leadership"], "improvements": ["Highlight management experience"]}',
                    job=demo_jobs[1]
                ),
                JobApplication(
                    id=str(uuid.uuid4()),
                    userId=userId or "demo-user-id",
                    jobId=demo_jobs[2].id,
                    status="offer",
                    appliedDate=datetime.now() - timedelta(days=20),
                    lastUpdated=datetime.now() - timedelta(days=1),
                    coverLetter="I am excited about the opportunity to work with cutting-edge technologies at your company.",
                    notes="Received offer, negotiating salary",
                    skillsAnalysis='{"match_score": 85, "missing_skills": ["Docker", "Kubernetes"], "strong_skills": ["Python", "FastAPI"]}',
                    job=demo_jobs[2]
                )
            ]
            
            # Apply filters
            filtered_applications = mock_applications
            
            if status:
                filtered_applications = [app for app in filtered_applications if app.status == status]
            
            # Apply pagination
            start = offset or 0
            end = start + (limit or 20)
            
            return filtered_applications[start:end]
            
        except Exception as e:
            print(f"Error in applications query: {e}")
            # Return empty list on error to prevent frontend crash
            return []
    
    @strawberry.field
    async def application(self, id: str) -> Optional[JobApplication]:
        """Get a specific application by ID - demo implementation"""
        # For demo, return the first application from the applications query
        query_instance = Query()
        applications = await query_instance.applications(limit=1)
        return applications[0] if applications else None
    
    @strawberry.field
    async def savedJobs(
        self, 
        userId: Optional[str] = None,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0
    ) -> List[SavedJob]:
        """Get saved jobs - demo implementation"""
        import uuid
        from datetime import datetime, timedelta
        
        # Get demo jobs to reference
        query_instance = Query()
        demo_jobs = await query_instance.jobs(limit=2)
        
        # Create mock saved jobs
        mock_saved_jobs = [
            SavedJob(
                id=str(uuid.uuid4()),
                userId=userId or "demo-user-id",
                jobId=demo_jobs[0].id if demo_jobs else str(uuid.uuid4()),
                savedDate=datetime.now() - timedelta(days=5),
                notes="Interesting position, need to research company more",
                job=demo_jobs[0] if demo_jobs else None
            ),
            SavedJob(
                id=str(uuid.uuid4()),
                userId=userId or "demo-user-id",
                jobId=demo_jobs[1].id if len(demo_jobs) > 1 else str(uuid.uuid4()),
                savedDate=datetime.now() - timedelta(days=8),
                notes="Great benefits package, considering application",
                job=demo_jobs[1] if len(demo_jobs) > 1 else None
            )
        ]
        
        # Apply pagination
        start = offset or 0
        end = start + (limit or 20)
        
        return mock_saved_jobs[start:end]
    
    @strawberry.field
    async def validateSession(self) -> SessionValidationResponse:
        """Validate current session - demo implementation"""
        # In production, this would validate the HttpOnly cookie
        # For demo purposes, always return valid session
        demo_user = User(
            id="demo-user-id",
            email="test@example.com",
            username="testuser",
            fullName="Test User",
            bio="Demo user with secure authentication",
            currentJobTitle="Software Developer",
            yearsOfExperience=5,
            industry="Technology",
            careerLevel="mid",
            jobSearchStatus="actively_looking",
            preferredWorkType="hybrid"
        )
        
        print("🔍 Session validation requested - returning valid session for demo")
        
        return SessionValidationResponse(
            valid=True,
            user=demo_user,
            message="Session is valid"
        )


@strawberry.input
class RegisterUserInput:
    email: str
    username: str
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None

@strawberry.type
class RegisterUserResponse:
    success: bool
    errors: Optional[List[str]] = None
    user: Optional[User] = None  # Return full User object

@strawberry.type
class TokenResponse:
    token: Optional[str] = None

@strawberry.input
class UpdateUserProfileInput:
    """Input for updating user profile"""
    fullName: Optional[str] = None
    bio: Optional[str] = None
    currentJobTitle: Optional[str] = None
    yearsOfExperience: Optional[int] = None
    industry: Optional[str] = None
    careerLevel: Optional[str] = None
    jobSearchStatus: Optional[str] = None
    preferredWorkType: Optional[str] = None

@strawberry.type
class UserResponse:
    """Response for user operations"""
    success: bool
    user: Optional[User] = None
    errors: Optional[List[str]] = None

@strawberry.input  
class CreateJobInput:
    """Input for creating a user job position."""
    title: str
    companyName: str  # Changed to camelCase to match frontend
    locationText: str  # Changed to camelCase to match frontend
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salaryMin: Optional[float] = None  # Changed to camelCase
    salaryMax: Optional[float] = None  # Changed to camelCase  
    salaryCurrency: str = "USD"  # Changed to camelCase
    salaryPeriod: str = "yearly"  # Changed to camelCase
    jobType: str = "full_time"  # Changed to camelCase
    contractType: str = "permanent"  # Changed to camelCase
    experienceLevel: Optional[str] = None  # Changed to camelCase
    remoteType: str = "on_site"  # Changed to camelCase

@strawberry.input  
class UpdateJobInput:
    """Input for updating a user job position."""
    title: Optional[str] = None
    companyName: Optional[str] = None
    locationText: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salaryMin: Optional[float] = None
    salaryMax: Optional[float] = None
    salaryCurrency: Optional[str] = None
    salaryPeriod: Optional[str] = None
    jobType: Optional[str] = None
    contractType: Optional[str] = None
    experienceLevel: Optional[str] = None
    remoteType: Optional[str] = None

@strawberry.input
class CreateApplicationInput:
    """Input for creating a job application"""
    jobId: str
    coverLetter: Optional[str] = None
    notes: Optional[str] = None

@strawberry.input
class UpdateApplicationInput:
    """Input for updating a job application"""
    status: Optional[str] = None
    coverLetter: Optional[str] = None
    notes: Optional[str] = None

@strawberry.input
class SaveJobInput:
    """Input for saving a job"""
    jobId: str
    notes: Optional[str] = None

@strawberry.type
class JobResponse:
    """Response for job creation"""
    success: bool
    jobId: Optional[str] = None  # Changed to match frontend expectation
    errors: Optional[List[str]] = None

@strawberry.type
class ApplicationResponse:
    """Response for application operations"""
    success: bool
    application_id: Optional[str] = None
    application: Optional[JobApplication] = None
    errors: Optional[List[str]] = None

@strawberry.type
class SavedJobResponse:
    """Response for saved job operations"""
    success: bool
    saved_job_id: Optional[str] = None
    saved_job: Optional[SavedJob] = None
    errors: Optional[List[str]] = None

@strawberry.input
class PersonalInfoInput:
    """Personal information input for resume"""
    fullName: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None

@strawberry.input
class ExperienceInput:
    """Work experience input"""
    company: str
    position: str
    startDate: str
    endDate: Optional[str] = None
    current: bool = False
    description: Optional[str] = None

@strawberry.input
class EducationInput:
    """Education input"""
    school: str
    degree: str
    field: Optional[str] = None
    startDate: str
    endDate: Optional[str] = None
    current: bool = False
    gpa: Optional[str] = None

@strawberry.input
class ProjectInput:
    """Project input"""
    name: str
    description: Optional[str] = None
    technologies: Optional[str] = None
    link: Optional[str] = None

@strawberry.input
class CreateResumeInput:
    """Input for creating/updating a resume"""
    title: str
    personalInfo: PersonalInfoInput
    summary: Optional[str] = None
    experience: Optional[List[ExperienceInput]] = None
    education: Optional[List[EducationInput]] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[ProjectInput]] = None
    targetRole: Optional[str] = None
    targetIndustry: Optional[str] = None
    keywords: Optional[str] = None

@strawberry.type
class ResumeResponse:
    """Response for resume operations"""
    success: bool
    resume_id: Optional[str] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None

@strawberry.type
class Mutation:
    """
    Root Mutation type - minimal implementation to get schema working
    """
    
    @strawberry.field
    async def test_mutation(self, message: str) -> str:
        return f"Test mutation received: {message}"
    
    @strawberry.field
    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        firstName: Optional[str] = None,
        lastName: Optional[str] = None
    ) -> RegisterUserResponse:
        """Register a new user - minimal implementation for demo"""
        # For demo purposes, always return success
        # In production, this would validate inputs and create user in database
        
        # Create a demo user object with the provided data
        demo_user = User(
            id="demo-user-id",
            email=email,
            username=username,
            fullName=f"{firstName or ''} {lastName or ''}".strip() or None,
            bio="New user registered via demo",
            currentJobTitle="Software Developer",
            yearsOfExperience=0,
            industry="Technology",
            careerLevel="entry",
            jobSearchStatus="actively_looking",
            preferredWorkType="hybrid"
        )
        
        return RegisterUserResponse(
            success=True,
            user=demo_user,
            errors=None
        )
    
    @strawberry.field
    async def token_auth(
        self,
        username: str,
        password: str
    ) -> TokenResponse:
        """Authenticate user and return token - minimal implementation for demo"""
        # For demo purposes, always return a mock token
        # In production, this would validate credentials and return JWT
        return TokenResponse(token="mock-jwt-token-for-demo")
    
    @strawberry.field
    async def verify_token(
        self,
        token: str
    ) -> bool:
        """Verify token - minimal implementation for demo"""
        # For demo purposes, always return True for non-empty tokens
        return bool(token)
    
    @strawberry.field
    async def create_job(
        self,
        input: CreateJobInput,
        info
    ) -> JobResponse:
        """Create a new job with real database persistence"""
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import select
        from fastapi import Depends
        from app.core.database import get_db
        from app.models import Job, Company
        from datetime import datetime
        
        # Get database session
        async def get_db_session():
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                return session
        
        db = await get_db_session()
        
        try:
            # Find or create company
            company_result = await db.execute(
                select(Company).where(Company.name.ilike(f"%{input.companyName}%"))
            )
            company = company_result.scalar_one_or_none()
            
            if not company:
                # Create new company
                company = Company(
                    name=input.companyName,
                    slug=input.companyName.lower().replace(' ', '-').replace('/', '-'),
                    description=f"Company profile for {input.companyName}",
                )
                db.add(company)
                await db.flush()  # Get company ID
            
            # Create job
            job = Job(
                title=input.title,
                company_id=company.id,
                category_id=None,  # Optional for user input
                description=input.description,
                requirements=input.requirements,
                benefits=input.benefits,
                location_text=input.locationText,
                salary_min=input.salaryMin,
                salary_max=input.salaryMax,
                salary_currency=input.salaryCurrency,
                salary_period=input.salaryPeriod,
                job_type=input.jobType,
                contract_type=input.contractType,
                experience_level=input.experienceLevel,
                remote_type=input.remoteType,
                user_input=True,  # Mark as user input
                source="user_input",
                posted_date=datetime.utcnow(),
            )
            
            db.add(job)
            await db.commit()
            await db.refresh(job)
            
            # Invalidate job caches since we created a new job
            from app.services.cache_service import get_cache_service
            cache_service = await get_cache_service()
            await cache_service.invalidate_job_caches()
            print("🗑️ Invalidated job search caches after creating new job")
            
            return JobResponse(
                success=True,
                jobId=str(job.id),  # Convert UUID to string and match frontend expectation
                errors=None
            )
            
        except Exception as e:
            await db.rollback()
            return JobResponse(
                success=False,
                jobId=None,
                errors=[f"Failed to create job: {str(e)}"]
            )
        finally:
            await db.close()
    
    @strawberry.field
    async def delete_job(
        self,
        jobId: str,
        info
    ) -> JobResponse:
        """Delete a job with real database persistence"""
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import select
        from app.models import Job
        from app.services.cache_service import cache_service
        
        # Get database session
        async def get_db_session():
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                return session
        
        db = await get_db_session()
        
        try:
            # Find the job to delete
            job_result = await db.execute(
                select(Job).where(Job.id == jobId)
            )
            job = job_result.scalar_one_or_none()
            
            if not job:
                return JobResponse(
                    success=False,
                    jobId=None,
                    errors=[f"Job with ID {jobId} not found"]
                )
            
            # Delete the job (this will also handle foreign key constraints)
            await db.delete(job)
            await db.commit()
            
            print(f"✅ Successfully deleted job: {job.title} (ID: {jobId})")
            
            # Invalidate cache
            await cache_service.invalidate_job_caches()
            print("🗑️ Invalidated job search caches after deleting job")
            
            return JobResponse(
                success=True,
                jobId=jobId,
                errors=None
            )
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error deleting job {jobId}: {str(e)}")
            return JobResponse(
                success=False,
                jobId=None,
                errors=[f"Failed to delete job: {str(e)}"]
            )
        finally:
            await db.close()
    
    @strawberry.field
    async def update_job(
        self,
        jobId: str,
        input: UpdateJobInput,
        info
    ) -> JobResponse:
        """Update an existing job with real database persistence"""
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import select
        from app.models import Job, Company
        from app.services.cache_service import cache_service
        
        # Get database session
        async def get_db_session():
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                return session
        
        db = await get_db_session()
        
        try:
            # Find the job to update
            job_result = await db.execute(
                select(Job).where(Job.id == jobId)
            )
            job = job_result.scalar_one_or_none()
            
            if not job:
                return JobResponse(
                    success=False,
                    jobId=None,
                    errors=[f"Job with ID {jobId} not found"]
                )
            
            # Update job fields if provided
            if input.title is not None:
                job.title = input.title
            if input.locationText is not None:
                job.location_text = input.locationText
            if input.description is not None:
                job.description = input.description
            if input.requirements is not None:
                job.requirements = input.requirements
            if input.benefits is not None:
                job.benefits = input.benefits
            if input.salaryMin is not None:
                job.salary_min = input.salaryMin
            if input.salaryMax is not None:
                job.salary_max = input.salaryMax
            if input.salaryCurrency is not None:
                job.salary_currency = input.salaryCurrency
            if input.salaryPeriod is not None:
                job.salary_period = input.salaryPeriod
            if input.jobType is not None:
                job.job_type = input.jobType
            if input.contractType is not None:
                job.contract_type = input.contractType
            if input.experienceLevel is not None:
                job.experience_level = input.experienceLevel
            if input.remoteType is not None:
                job.remote_type = input.remoteType
            
            # Handle company update if provided
            if input.companyName is not None:
                # Find or create company
                company_result = await db.execute(
                    select(Company).where(Company.name.ilike(f"%{input.companyName}%"))
                )
                company = company_result.scalar_one_or_none()
                
                if not company:
                    # Create new company
                    company = Company(
                        name=input.companyName,
                        slug=input.companyName.lower().replace(' ', '-').replace('/', '-'),
                        description=f"Company profile for {input.companyName}",
                    )
                    db.add(company)
                    await db.flush()  # Get the company ID
                
                job.company_id = company.id
            
            # Update timestamp
            from datetime import datetime
            job.updated_at = datetime.utcnow()
            
            await db.commit()
            
            print(f"✅ Successfully updated job: {job.title} (ID: {jobId})")
            
            # Invalidate cache
            await cache_service.invalidate_job_caches()
            print("🗑️ Invalidated job search caches after updating job")
            
            return JobResponse(
                success=True,
                jobId=jobId,
                errors=None
            )
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error updating job {jobId}: {str(e)}")
            return JobResponse(
                success=False,
                jobId=None,
                errors=[f"Failed to update job: {str(e)}"]
            )
        finally:
            await db.close()
    
    @strawberry.field
    async def create_resume(
        self,
        input: CreateResumeInput
    ) -> ResumeResponse:
        """Create a new resume - handles the resume builder functionality"""
        try:
            # For now, simulate resume creation with basic validation
            import uuid
            resume_id = str(uuid.uuid4())
            
            # Basic validation
            errors = []
            if not input.personalInfo.fullName.strip():
                errors.append("Full name is required")
            if not input.personalInfo.email.strip():
                errors.append("Email is required")
            
            # Validate email format
            if input.personalInfo.email:
                import re
                email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                if not re.match(email_pattern, input.personalInfo.email):
                    errors.append("Please enter a valid email address")
            
            # Validate experience data if provided
            if input.experience:
                for exp in input.experience:
                    if not exp.company.strip():
                        errors.append("Company name is required for work experience")
                    if not exp.position.strip():
                        errors.append("Position is required for work experience")
            
            if errors:
                return ResumeResponse(
                    success=False,
                    errors=errors
                )
            
            # Simulate successful creation with data logging
            print(f"Creating resume: {input.title}")
            print(f"Personal info: {input.personalInfo.fullName} ({input.personalInfo.email})")
            print(f"Experience entries: {len(input.experience or [])}")
            print(f"Education entries: {len(input.education or [])}")
            print(f"Skills: {len(input.skills or [])}")
            
            return ResumeResponse(
                success=True,
                resume_id=resume_id,
                message=f"Resume '{input.title}' created successfully",
                errors=None
            )
            
        except Exception as e:
            return ResumeResponse(
                success=False,
                errors=[f"Failed to create resume: {str(e)}"]
            )
    
    @strawberry.field
    async def update_resume(
        self,
        resume_id: str,
        input: CreateResumeInput
    ) -> ResumeResponse:
        """Update an existing resume"""
        try:
            # Basic validation
            errors = []
            if not input.personalInfo.fullName.strip():
                errors.append("Full name is required")
            if not input.personalInfo.email.strip():
                errors.append("Email is required")
            
            if errors:
                return ResumeResponse(
                    success=False,
                    errors=errors
                )
            
            # Simulate successful update
            return ResumeResponse(
                success=True,
                resume_id=resume_id,
                message=f"Resume '{input.title}' updated successfully",
                errors=None
            )
            
        except Exception as e:
            return ResumeResponse(
                success=False,
                errors=[f"Failed to update resume: {str(e)}"]
            )
    
    @strawberry.field
    async def update_user_profile(
        self,
        input: UpdateUserProfileInput
    ) -> UserResponse:
        """Update user profile - demo implementation"""
        try:
            # Basic validation
            errors = []
            
            if input.yearsOfExperience is not None and input.yearsOfExperience < 0:
                errors.append("Years of experience cannot be negative")
            
            if input.careerLevel and input.careerLevel not in ['entry', 'mid', 'senior', 'lead', 'executive']:
                errors.append("Invalid career level")
            
            if input.jobSearchStatus and input.jobSearchStatus not in ['actively_looking', 'passively_looking', 'not_looking']:
                errors.append("Invalid job search status")
            
            if input.preferredWorkType and input.preferredWorkType not in ['remote', 'on_site', 'hybrid']:
                errors.append("Invalid preferred work type")
            
            if errors:
                return UserResponse(
                    success=False,
                    errors=errors
                )
            
            # Simulate successful update - create updated user object
            updated_user = User(
                id="demo-user-id",
                email="test@example.com",
                username="testuser",
                fullName=input.fullName or "Test User",
                bio=input.bio,
                currentJobTitle=input.currentJobTitle,
                yearsOfExperience=input.yearsOfExperience,
                industry=input.industry,
                careerLevel=input.careerLevel,
                jobSearchStatus=input.jobSearchStatus,
                preferredWorkType=input.preferredWorkType
            )
            
            print(f"Updating user profile: {input.fullName}")
            print(f"Job title: {input.currentJobTitle}")
            print(f"Experience: {input.yearsOfExperience} years")
            print(f"Industry: {input.industry}")
            
            return UserResponse(
                success=True,
                user=updated_user,
                errors=None
            )
            
        except Exception as e:
            return UserResponse(
                success=False,
                errors=[f"Failed to update profile: {str(e)}"]
            )
    
    @strawberry.field
    async def create_application(
        self,
        input: CreateApplicationInput
    ) -> ApplicationResponse:
        """Create a job application - demo implementation"""
        try:
            # Basic validation
            errors = []
            if not input.jobId.strip():
                errors.append("Job ID is required")
            
            if errors:
                return ApplicationResponse(
                    success=False,
                    errors=errors
                )
            
            # Simulate successful application creation
            import uuid
            from datetime import datetime
            
            application_id = str(uuid.uuid4())
            
            # Get the job being applied to
            query_instance = Query()
            job = await query_instance.job(input.jobId)
            
            # Create application object
            application = JobApplication(
                id=application_id,
                userId="demo-user-id",
                jobId=input.jobId,
                status="applied",
                appliedDate=datetime.now(),
                lastUpdated=datetime.now(),
                coverLetter=input.coverLetter,
                notes=input.notes,
                job=job
            )
            
            print(f"Creating application for job: {input.jobId}")
            print(f"Cover letter length: {len(input.coverLetter or '')}")
            print(f"Notes: {input.notes}")
            
            return ApplicationResponse(
                success=True,
                application_id=application_id,
                application=application,
                errors=None
            )
            
        except Exception as e:
            return ApplicationResponse(
                success=False,
                errors=[f"Failed to create application: {str(e)}"]
            )
    
    @strawberry.field
    async def update_application(
        self,
        application_id: str,
        input: UpdateApplicationInput
    ) -> ApplicationResponse:
        """Update a job application - demo implementation"""
        try:
            # Basic validation
            errors = []
            if not application_id.strip():
                errors.append("Application ID is required")
            
            if input.status and input.status not in ['applied', 'screening', 'interview', 'offer', 'rejected', 'withdrawn']:
                errors.append("Invalid application status")
            
            if errors:
                return ApplicationResponse(
                    success=False,
                    errors=errors
                )
            
            # Simulate successful update
            from datetime import datetime
            
            # Get existing application (mock)
            query_instance = Query()
            existing_application = await query_instance.application(application_id)
            
            if not existing_application:
                return ApplicationResponse(
                    success=False,
                    errors=["Application not found"]
                )
            
            # Update application
            updated_application = JobApplication(
                id=application_id,
                userId=existing_application.userId,
                jobId=existing_application.jobId,
                status=input.status or existing_application.status,
                appliedDate=existing_application.appliedDate,
                lastUpdated=datetime.now(),
                coverLetter=input.coverLetter or existing_application.coverLetter,
                notes=input.notes or existing_application.notes,
                job=existing_application.job
            )
            
            print(f"Updating application: {application_id}")
            print(f"New status: {input.status}")
            
            return ApplicationResponse(
                success=True,
                application_id=application_id,
                application=updated_application,
                errors=None
            )
            
        except Exception as e:
            return ApplicationResponse(
                success=False,
                errors=[f"Failed to update application: {str(e)}"]
            )
    
    @strawberry.field
    async def save_job(
        self,
        input: SaveJobInput
    ) -> SavedJobResponse:
        """Save a job - demo implementation"""
        try:
            # Basic validation
            errors = []
            if not input.jobId.strip():
                errors.append("Job ID is required")
            
            if errors:
                return SavedJobResponse(
                    success=False,
                    errors=errors
                )
            
            # Simulate successful job save
            import uuid
            from datetime import datetime
            
            saved_job_id = str(uuid.uuid4())
            
            # Get the job being saved
            query_instance = Query()
            job = await query_instance.job(input.jobId)
            
            # Create saved job object
            saved_job = SavedJob(
                id=saved_job_id,
                userId="demo-user-id",
                jobId=input.jobId,
                savedDate=datetime.now(),
                notes=input.notes,
                job=job
            )
            
            print(f"Saving job: {input.jobId}")
            print(f"Notes: {input.notes}")
            
            return SavedJobResponse(
                success=True,
                saved_job_id=saved_job_id,
                saved_job=saved_job,
                errors=None
            )
            
        except Exception as e:
            return SavedJobResponse(
                success=False,
                errors=[f"Failed to save job: {str(e)}"]
            )
    
    @strawberry.field
    async def unsave_job(
        self,
        job_id: str
    ) -> SavedJobResponse:
        """Unsave a job - demo implementation"""
        try:
            # Basic validation
            if not job_id.strip():
                return SavedJobResponse(
                    success=False,
                    errors=["Job ID is required"]
                )
            
            # Simulate successful job unsave
            print(f"Unsaving job: {job_id}")
            
            return SavedJobResponse(
                success=True,
                saved_job_id=None,
                saved_job=None,
                errors=None
            )
            
        except Exception as e:
            return SavedJobResponse(
                success=False,
                errors=[f"Failed to unsave job: {str(e)}"]
            )
    
    @strawberry.field
    async def secure_login(
        self,
        username: str,
        password: str
    ) -> SecureAuthResponse:
        """Secure login with HttpOnly cookies - demo implementation"""
        try:
            # Basic validation
            errors = []
            if not username.strip():
                errors.append("Username is required")
            if not password.strip():
                errors.append("Password is required")
            
            if errors:
                return SecureAuthResponse(
                    success=False,
                    errors=errors
                )
            
            # Simulate authentication
            demo_user = User(
                id="demo-user-id",
                email="test@example.com",
                username=username,
                fullName="Test User",
                bio="Demo user with secure authentication",
                currentJobTitle="Software Developer",
                yearsOfExperience=5,
                industry="Technology",
                careerLevel="mid",
                jobSearchStatus="actively_looking",
                preferredWorkType="hybrid"
            )
            
            print(f"🔐 Secure login for user: {username}")
            print("🍪 Setting HttpOnly authentication cookie (demo)")
            
            # In production, this would:
            # 1. Validate username/password against database
            # 2. Generate secure JWT token
            # 3. Set HttpOnly cookie with the token
            # 4. Set secure cookie attributes (Secure, SameSite, etc.)
            
            return SecureAuthResponse(
                success=True,
                user=demo_user,
                message=f"Secure login successful for {username}"
            )
            
        except Exception as e:
            return SecureAuthResponse(
                success=False,
                errors=[f"Secure login failed: {str(e)}"]
            )
    
    @strawberry.field
    async def secure_logout(self) -> SecureAuthResponse:
        """Secure logout with HttpOnly cookie cleanup - demo implementation"""
        try:
            print("🚪 Secure logout requested")
            print("🗑️ Clearing HttpOnly authentication cookie (demo)")
            
            # In production, this would:
            # 1. Clear the HttpOnly authentication cookie
            # 2. Invalidate the session on the server
            # 3. Add the token to a blacklist if needed
            
            return SecureAuthResponse(
                success=True,
                message="Secure logout successful"
            )
            
        except Exception as e:
            return SecureAuthResponse(
                success=False,
                errors=[f"Secure logout failed: {str(e)}"]
            )
    
    @strawberry.field
    async def refresh_token(self) -> SecureAuthResponse:
        """Refresh authentication token using HttpOnly cookies - demo implementation"""
        try:
            print("🔄 Token refresh requested")
            print("🍪 Validating and refreshing HttpOnly cookie (demo)")
            
            # In production, this would:
            # 1. Validate the current HttpOnly cookie
            # 2. Generate a new JWT token
            # 3. Update the HttpOnly cookie with the new token
            # 4. Return updated user information
            
            demo_user = User(
                id="demo-user-id",
                email="test@example.com",
                username="testuser",
                fullName="Test User",
                bio="Demo user with refreshed authentication",
                currentJobTitle="Software Developer",
                yearsOfExperience=5,
                industry="Technology",
                careerLevel="mid",
                jobSearchStatus="actively_looking",
                preferredWorkType="hybrid"
            )
            
            return SecureAuthResponse(
                success=True,
                user=demo_user,
                message="Token refresh successful"
            )
            
        except Exception as e:
            return SecureAuthResponse(
                success=False,
                errors=[f"Token refresh failed: {str(e)}"]
            )


# Create main schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)