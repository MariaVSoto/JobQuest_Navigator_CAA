"""
Factory classes for creating test data using Factory Boy.
Provides realistic test data generation for all models.
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory import Faker, SubFactory, LazyAttribute, LazyFunction
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid
import random
import json

# Import models (these would be your actual model imports)
# from app.models.user import User
# from app.models.job import Job, JobApplication
# from app.models.resume import Resume

# For now, we'll create mock model classes for the factories
class MockUser:
    pass

class MockJob:
    pass

class MockJobApplication:
    pass

class MockResume:
    pass


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory with common configuration."""
    
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"
    
    id = LazyFunction(lambda: str(uuid.uuid4()))
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)


class UserFactory(BaseFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = MockUser  # Replace with actual User model
    
    # Basic Info
    email = Faker('email')
    cognito_sub = LazyFunction(lambda: str(uuid.uuid4()))
    cognito_username = Faker('user_name')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    phone = Faker('phone_number')
    
    # Profile Info
    bio = Faker('text', max_nb_chars=200)
    location = Faker('city')
    website = Faker('url')
    linkedin_url = LazyAttribute(lambda obj: f"https://linkedin.com/in/{obj.first_name.lower()}-{obj.last_name.lower()}")
    github_url = LazyAttribute(lambda obj: f"https://github.com/{obj.first_name.lower()}{obj.last_name.lower()}")
    
    # Career Info
    experience_level = Faker('random_element', elements=['entry', 'junior', 'mid', 'senior', 'lead', 'executive'])
    current_job_title = Faker('job')
    current_company = Faker('company')
    years_of_experience = Faker('random_int', min=0, max=20)
    
    # Preferences
    preferred_salary_min = Faker('random_int', min=40000, max=80000)
    preferred_salary_max = LazyAttribute(lambda obj: obj.preferred_salary_min + random.randint(20000, 80000))
    remote_preference = Faker('random_element', elements=['remote', 'hybrid', 'onsite', 'flexible'])
    willing_to_relocate = Faker('boolean')
    
    # Skills (as JSON)
    skills = LazyFunction(lambda: json.dumps([
        'Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL', 
        'AWS', 'Docker', 'Git', 'Agile', 'REST APIs'
    ][:random.randint(3, 8)]))
    
    # Certifications
    certifications = LazyFunction(lambda: json.dumps([
        'AWS Certified Developer',
        'Google Cloud Professional',
        'Certified Scrum Master',
        'CompTIA Security+'
    ][:random.randint(0, 3)]))
    
    # Status
    is_active = True
    is_admin = False
    is_verified = True
    last_login = LazyFunction(lambda: datetime.utcnow() - timedelta(days=random.randint(0, 30)))
    
    # Privacy Settings
    profile_visibility = Faker('random_element', elements=['public', 'private', 'contacts_only'])
    email_notifications = True
    job_alerts = True


class AdminUserFactory(UserFactory):
    """Factory for creating admin users."""
    is_admin = True
    email = 'admin@jobquest.com'
    first_name = 'Admin'
    last_name = 'User'


class JobFactory(BaseFactory):
    """Factory for creating Job instances."""
    
    class Meta:
        model = MockJob  # Replace with actual Job model
    
    # Basic Info
    title = Faker('job')
    description = Faker('text', max_nb_chars=1000)
    company = Faker('company')
    department = Faker('random_element', elements=[
        'Engineering', 'Product', 'Design', 'Marketing', 
        'Sales', 'Operations', 'Finance', 'HR'
    ])
    
    # Location
    location = Faker('city')
    country = Faker('country')
    remote_ok = Faker('boolean', chance_of_getting_true=60)
    hybrid_ok = Faker('boolean', chance_of_getting_true=40)
    
    # Job Details
    job_type = Faker('random_element', elements=['full_time', 'part_time', 'contract', 'internship', 'temporary'])
    experience_level = Faker('random_element', elements=['entry', 'junior', 'mid', 'senior', 'lead', 'executive'])
    education_level = Faker('random_element', elements=[
        'high_school', 'associates', 'bachelors', 'masters', 'phd', 'bootcamp', 'certification'
    ])
    
    # Compensation
    salary_min = Faker('random_int', min=40000, max=120000)
    salary_max = LazyAttribute(lambda obj: obj.salary_min + random.randint(10000, 50000))
    salary_currency = 'USD'
    equity_min = Faker('random_element', elements=[None, 0.01, 0.05, 0.1, 0.25, 0.5])
    equity_max = LazyAttribute(lambda obj: obj.equity_min + 0.1 if obj.equity_min else None)
    
    # Requirements
    skills_required = LazyFunction(lambda: json.dumps([
        'Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL', 
        'AWS', 'Docker', 'Kubernetes', 'MongoDB', 'GraphQL'
    ][:random.randint(3, 7)]))
    
    skills_preferred = LazyFunction(lambda: json.dumps([
        'TypeScript', 'Vue.js', 'Redis', 'Elasticsearch', 
        'Terraform', 'Jenkins', 'Microservices'
    ][:random.randint(0, 4)]))
    
    languages_required = LazyFunction(lambda: json.dumps(['English']))
    languages_preferred = LazyFunction(lambda: json.dumps([
        'Spanish', 'French', 'German', 'Mandarin'
    ][:random.randint(0, 2)]))
    
    # Benefits
    benefits = LazyFunction(lambda: json.dumps([
        'Health Insurance', '401k Match', 'Unlimited PTO', 
        'Stock Options', 'Remote Work', 'Learning Budget',
        'Gym Membership', 'Dental Insurance', 'Vision Insurance'
    ][:random.randint(3, 7)]))
    
    # Application Process
    application_deadline = LazyFunction(
        lambda: datetime.utcnow() + timedelta(days=random.randint(7, 60))
    )
    application_url = Faker('url')
    contact_email = Faker('email')
    
    # Status
    status = Faker('random_element', elements=['draft', 'published', 'closed', 'cancelled'])
    is_featured = Faker('boolean', chance_of_getting_true=20)
    view_count = Faker('random_int', min=0, max=1000)
    application_count = Faker('random_int', min=0, max=50)
    
    # SEO and Analytics
    slug = LazyAttribute(lambda obj: f"{obj.title.lower().replace(' ', '-')}-{random.randint(1000, 9999)}")
    tags = LazyFunction(lambda: json.dumps([
        'startup', 'fintech', 'saas', 'enterprise', 'ai', 'blockchain'
    ][:random.randint(1, 3)]))
    
    # Relations
    created_by_id = SubFactory(UserFactory)
    company_id = LazyFunction(lambda: str(uuid.uuid4()))


class RemoteJobFactory(JobFactory):
    """Factory for remote jobs."""
    remote_ok = True
    location = 'Remote'


class SeniorJobFactory(JobFactory):
    """Factory for senior-level jobs."""
    experience_level = 'senior'
    salary_min = Faker('random_int', min=100000, max=150000)
    salary_max = LazyAttribute(lambda obj: obj.salary_min + random.randint(20000, 50000))


class JobApplicationFactory(BaseFactory):
    """Factory for creating JobApplication instances."""
    
    class Meta:
        model = MockJobApplication  # Replace with actual JobApplication model
    
    # Relations
    user_id = SubFactory(UserFactory)
    job_id = SubFactory(JobFactory)
    resume_id = LazyFunction(lambda: str(uuid.uuid4()))
    
    # Application Details
    status = Faker('random_element', elements=[
        'draft', 'submitted', 'under_review', 'interview_scheduled',
        'interviewed', 'offer_made', 'accepted', 'rejected', 'withdrawn'
    ])
    
    cover_letter = Faker('text', max_nb_chars=500)
    custom_resume = Faker('boolean', chance_of_getting_true=30)
    
    # Application Responses
    question_responses = LazyFunction(lambda: json.dumps({
        "Why are you interested in this role?": Faker('text', max_nb_chars=200).generate(),
        "What makes you a good fit?": Faker('text', max_nb_chars=200).generate(),
        "Salary expectations?": f"${random.randint(70, 150)}k - ${random.randint(150, 200)}k"
    }))
    
    # Timeline
    submitted_at = LazyFunction(lambda: datetime.utcnow() - timedelta(days=random.randint(0, 30)))
    last_updated_at = LazyFunction(datetime.utcnow)
    
    # Interview Process
    interview_rounds = Faker('random_int', min=0, max=5)
    current_round = Faker('random_int', min=0, max=5)
    next_interview_date = LazyFunction(
        lambda: datetime.utcnow() + timedelta(days=random.randint(1, 14))
        if random.choice([True, False]) else None
    )
    
    # Feedback and Notes
    recruiter_notes = Faker('text', max_nb_chars=300)
    candidate_notes = Faker('text', max_nb_chars=200)
    
    # Metrics
    response_time_hours = Faker('random_int', min=1, max=72)
    source = Faker('random_element', elements=[
        'direct_application', 'job_board', 'referral', 'recruiter', 'company_website'
    ])


class ResumeFactory(BaseFactory):
    """Factory for creating Resume instances."""
    
    class Meta:
        model = MockResume  # Replace with actual Resume model
    
    # Basic Info
    user_id = SubFactory(UserFactory)
    title = Faker('random_element', elements=[
        'Software Engineer Resume',
        'Product Manager Resume', 
        'Data Scientist Resume',
        'Frontend Developer Resume',
        'Full Stack Developer Resume'
    ])
    
    # Content Structure
    content = LazyFunction(lambda: json.dumps({
        "personal_info": {
            "name": f"{Faker('first_name').generate()} {Faker('last_name').generate()}",
            "email": Faker('email').generate(),
            "phone": Faker('phone_number').generate(),
            "location": Faker('city').generate(),
            "website": Faker('url').generate(),
            "linkedin": f"https://linkedin.com/in/{Faker('user_name').generate()}",
            "github": f"https://github.com/{Faker('user_name').generate()}"
        },
        "summary": Faker('text', max_nb_chars=200).generate(),
        "experience": [
            {
                "title": Faker('job').generate(),
                "company": Faker('company').generate(),
                "location": Faker('city').generate(),
                "start_date": (datetime.utcnow() - timedelta(days=random.randint(365, 1825))).strftime('%Y-%m-%d'),
                "end_date": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
                "description": Faker('text', max_nb_chars=300).generate(),
                "achievements": [
                    Faker('sentence').generate() for _ in range(random.randint(2, 4))
                ]
            } for _ in range(random.randint(2, 5))
        ],
        "education": [
            {
                "degree": Faker('random_element', 
                    elements=['BS Computer Science', 'MS Software Engineering', 'BA Business', 'PhD Computer Science']
                ).generate(),
                "school": Faker('random_element', 
                    elements=['Stanford University', 'MIT', 'UC Berkeley', 'Carnegie Mellon']
                ).generate(),
                "location": Faker('city').generate(),
                "graduation_date": (datetime.utcnow() - timedelta(days=random.randint(365, 3650))).strftime('%Y-%m-%d'),
                "gpa": round(random.uniform(3.0, 4.0), 2)
            } for _ in range(random.randint(1, 2))
        ],
        "skills": {
            "technical": [
                'Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL', 
                'AWS', 'Docker', 'Git', 'Linux', 'REST APIs'
            ][:random.randint(5, 10)],
            "soft": [
                'Leadership', 'Communication', 'Problem Solving', 
                'Team Collaboration', 'Project Management'
            ][:random.randint(3, 5)]
        },
        "projects": [
            {
                "name": Faker('catch_phrase').generate(),
                "description": Faker('text', max_nb_chars=200).generate(),
                "technologies": ['React', 'Node.js', 'PostgreSQL'][:random.randint(2, 4)],
                "url": Faker('url').generate(),
                "github": f"https://github.com/user/{Faker('slug').generate()}"
            } for _ in range(random.randint(2, 4))
        ],
        "certifications": [
            {
                "name": Faker('random_element', elements=[
                    'AWS Certified Developer',
                    'Google Cloud Professional',
                    'Certified Scrum Master',
                    'MongoDB Certified Developer'
                ]).generate(),
                "issuer": Faker('company').generate(),
                "date": (datetime.utcnow() - timedelta(days=random.randint(0, 730))).strftime('%Y-%m-%d'),
                "credential_id": Faker('uuid4').generate()
            } for _ in range(random.randint(0, 3))
        ],
        "languages": [
            {
                "language": "English",
                "proficiency": "Native"
            },
            {
                "language": Faker('random_element', elements=['Spanish', 'French', 'German', 'Mandarin']).generate(),
                "proficiency": Faker('random_element', elements=['Basic', 'Intermediate', 'Advanced']).generate()
            }
        ][:random.randint(1, 3)]
    }))
    
    # Metadata
    version = Faker('random_int', min=1, max=10)
    is_default = Faker('boolean', chance_of_getting_true=20)
    is_public = Faker('boolean', chance_of_getting_true=30)
    
    # File Info
    file_path = LazyAttribute(lambda obj: f"/resumes/{obj.user_id}/{obj.id}.pdf")
    file_size = Faker('random_int', min=100000, max=5000000)  # 100KB to 5MB
    file_type = 'application/pdf'
    
    # Analytics
    view_count = Faker('random_int', min=0, max=100)
    download_count = Faker('random_int', min=0, max=50)
    last_viewed_at = LazyFunction(
        lambda: datetime.utcnow() - timedelta(days=random.randint(0, 30))
        if random.choice([True, False]) else None
    )
    
    # AI Analysis
    ai_score = Faker('random_int', min=60, max=100)
    ai_suggestions = LazyFunction(lambda: json.dumps([
        "Add more quantified achievements",
        "Include relevant keywords for your target role",
        "Consider adding a professional summary",
        "Update contact information"
    ][:random.randint(1, 4)]))
    
    keywords_matched = LazyFunction(lambda: json.dumps([
        'Python', 'JavaScript', 'React', 'AWS', 'Agile'
    ][:random.randint(2, 5)]))
    
    # Status
    status = Faker('random_element', elements=['draft', 'active', 'archived'])


class CompanyFactory(BaseFactory):
    """Factory for creating Company instances."""
    
    class Meta:
        model = None  # Replace with actual Company model when available
    
    # Basic Info
    name = Faker('company')
    slug = LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-').replace(',', ''))
    description = Faker('text', max_nb_chars=500)
    
    # Contact Info
    website = Faker('url')
    email = Faker('company_email')
    phone = Faker('phone_number')
    
    # Location
    headquarters = Faker('city')
    country = Faker('country')
    locations = LazyFunction(lambda: json.dumps([
        Faker('city').generate() for _ in range(random.randint(1, 5))
    ]))
    
    # Company Details
    industry = Faker('random_element', elements=[
        'Technology', 'Finance', 'Healthcare', 'Education', 
        'Retail', 'Manufacturing', 'Consulting', 'Media'
    ])
    company_size = Faker('random_element', elements=[
        '1-10', '11-50', '51-200', '201-500', '501-1000', '1000+'
    ])
    founded_year = Faker('random_int', min=1950, max=2023)
    
    # Social Media
    linkedin_url = LazyAttribute(lambda obj: f"https://linkedin.com/company/{obj.slug}")
    twitter_url = LazyAttribute(lambda obj: f"https://twitter.com/{obj.slug}")
    github_url = LazyAttribute(lambda obj: f"https://github.com/{obj.slug}")
    
    # Company Culture
    values = LazyFunction(lambda: json.dumps([
        'Innovation', 'Integrity', 'Collaboration', 'Excellence'
    ][:random.randint(2, 4)]))
    
    benefits = LazyFunction(lambda: json.dumps([
        'Health Insurance', '401k Match', 'Unlimited PTO', 
        'Stock Options', 'Remote Work', 'Learning Budget'
    ][:random.randint(3, 6)]))
    
    # Ratings
    glassdoor_rating = Faker('random_element', elements=[None, 3.2, 3.8, 4.1, 4.5, 4.8])
    indeed_rating = Faker('random_element', elements=[None, 3.5, 4.0, 4.2, 4.6, 4.9])
    
    # Status
    is_verified = Faker('boolean', chance_of_getting_true=70)
    is_hiring = Faker('boolean', chance_of_getting_true=80)
    logo_url = LazyAttribute(lambda obj: f"https://logo.clearbit.com/{obj.website}")


# Utility functions for batch creation
def create_user_with_resumes(session, num_resumes=3):
    """Create a user with multiple resumes."""
    user = UserFactory.create()
    resumes = ResumeFactory.create_batch(num_resumes, user_id=user.id)
    return user, resumes


def create_job_with_applications(session, num_applications=5):
    """Create a job with multiple applications."""
    job = JobFactory.create()
    applications = JobApplicationFactory.create_batch(num_applications, job_id=job.id)
    return job, applications


def create_complete_user_profile(session):
    """Create a user with complete profile data."""
    user = UserFactory.create(
        bio=Faker('text', max_nb_chars=300).generate(),
        skills=json.dumps([
            'Python', 'Django', 'React', 'PostgreSQL', 'AWS', 
            'Docker', 'Kubernetes', 'Git', 'Agile', 'REST APIs'
        ]),
        certifications=json.dumps([
            'AWS Certified Solutions Architect',
            'Google Cloud Professional Developer',
            'Certified Kubernetes Administrator'
        ])
    )
    
    # Create resumes
    resumes = ResumeFactory.create_batch(2, user_id=user.id)
    
    # Create job applications
    jobs = JobFactory.create_batch(3)
    applications = [
        JobApplicationFactory.create(user_id=user.id, job_id=job.id)
        for job in jobs
    ]
    
    return {
        'user': user,
        'resumes': resumes,
        'applications': applications,
        'jobs': jobs
    }


# Test data sets
class TestDataSets:
    """Predefined test data sets for common scenarios."""
    
    @staticmethod
    def create_job_search_scenario(session):
        """Create a complete job search scenario."""
        # Create companies
        companies = CompanyFactory.create_batch(5)
        
        # Create jobs for each company
        jobs = []
        for company in companies:
            company_jobs = JobFactory.create_batch(
                random.randint(1, 4),
                company=company.name
            )
            jobs.extend(company_jobs)
        
        # Create job seekers
        users = UserFactory.create_batch(10)
        
        # Create applications (some users apply to multiple jobs)
        applications = []
        for user in users:
            user_jobs = random.sample(jobs, random.randint(1, 5))
            for job in user_jobs:
                application = JobApplicationFactory.create(
                    user_id=user.id,
                    job_id=job.id
                )
                applications.append(application)
        
        return {
            'companies': companies,
            'jobs': jobs,
            'users': users,
            'applications': applications
        }