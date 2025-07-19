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
        remoteType: Optional[str] = None
    ) -> List[Job]:
        """Get job listings with filtering - demo implementation"""
        import uuid
        from datetime import datetime, timedelta
        
        # Create mock company
        demo_company = Company(
            id=str(uuid.uuid4()),
            name="TechCorp Inc",
            description="Leading technology company",
            industry="Technology",
            companySize="medium",
            foundedYear=2015
        )
        
        # Create mock jobs
        mock_jobs = [
            Job(
                id=str(uuid.uuid4()),
                title="Senior Software Engineer",
                description="We are looking for a talented Senior Software Engineer to join our growing team. You will be responsible for developing high-quality software solutions using modern technologies.",
                requirements="5+ years of experience with React, Node.js, and Python. Strong problem-solving skills and ability to work in a collaborative environment.",
                benefits="Competitive salary, health insurance, flexible working hours, remote work options.",
                locationText="Los Angeles, CA",
                salaryMin=90000.0,
                salaryMax=130000.0,
                salaryCurrency="USD",
                salaryPeriod="yearly",
                jobType="full_time",
                contractType="permanent",
                experienceLevel="senior",
                remoteType="hybrid",
                userInput=True,
                source="user_input",
                postedDate=datetime.now() - timedelta(days=2),
                company=demo_company,
                isSaved=False,
                isApplied=False
            ),
            Job(
                id=str(uuid.uuid4()),
                title="Frontend Developer",
                description="Join our frontend team to build amazing user experiences. Work with React, TypeScript, and modern CSS frameworks.",
                requirements="3+ years of frontend development experience. Proficiency in React, TypeScript, HTML, and CSS.",
                benefits="Health insurance, dental coverage, 401k matching, professional development budget.",
                locationText="Remote",
                salaryMin=70000.0,
                salaryMax=95000.0,
                salaryCurrency="USD",
                salaryPeriod="yearly",
                jobType="full_time",
                contractType="permanent",
                experienceLevel="mid",
                remoteType="remote",
                userInput=True,
                source="user_input",
                postedDate=datetime.now() - timedelta(days=5),
                company=demo_company,
                isSaved=True,
                isApplied=False
            ),
            Job(
                id=str(uuid.uuid4()),
                title="Full Stack Developer",
                description="Build end-to-end web applications using modern full-stack technologies. Work on both frontend and backend systems.",
                requirements="4+ years of full-stack development. Experience with React, Node.js, PostgreSQL, and cloud platforms.",
                benefits="Flexible PTO, stock options, learning stipend, home office setup allowance.",
                locationText="San Francisco, CA",
                salaryMin=85000.0,
                salaryMax=120000.0,
                salaryCurrency="USD",
                salaryPeriod="yearly",
                jobType="full_time",
                contractType="permanent",
                experienceLevel="mid",
                remoteType="on_site",
                userInput=True,
                source="user_input",
                postedDate=datetime.now() - timedelta(days=1),
                company=demo_company,
                isSaved=False,
                isApplied=True
            )
        ]
        
        # Apply filters
        filtered_jobs = mock_jobs
        
        if search:
            search_lower = search.lower()
            filtered_jobs = [job for job in filtered_jobs 
                           if search_lower in job.title.lower() or 
                              search_lower in job.description.lower()]
        
        if location:
            location_lower = location.lower()
            filtered_jobs = [job for job in filtered_jobs 
                           if job.locationText and location_lower in job.locationText.lower()]
        
        if jobType:
            filtered_jobs = [job for job in filtered_jobs if job.jobType == jobType]
        
        if experienceLevel:
            filtered_jobs = [job for job in filtered_jobs if job.experienceLevel == experienceLevel]
        
        if remoteType:
            filtered_jobs = [job for job in filtered_jobs if job.remoteType == remoteType]
        
        # Apply pagination
        start = offset or 0
        end = start + (limit or 20)
        
        return filtered_jobs[start:end]
    
    @strawberry.field
    async def job(self, id: str) -> Optional[Job]:
        """Get a specific job by ID - demo implementation"""
        # For demo, return the first job from the jobs query
        jobs = await self.jobs(limit=1)
        return jobs[0] if jobs else None


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
class CreateJobInput:
    """Input for creating a user job position."""
    title: str
    company_name: str
    location_text: str
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    salary_period: str = "yearly"
    job_type: str = "full_time"
    contract_type: str = "permanent"
    experience_level: Optional[str] = None
    remote_type: str = "on_site"

@strawberry.type
class JobResponse:
    """Response for job creation"""
    success: bool
    job_id: Optional[str] = None
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
        input: CreateJobInput
    ) -> JobResponse:
        """Create a new job - simplified implementation for demo"""
        # For demo purposes, always return success with a mock job ID
        # In production, this would create actual job in database
        import uuid
        job_id = str(uuid.uuid4())
        
        return JobResponse(
            success=True,
            job_id=job_id,
            errors=None
        )
    
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


# Create main schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)