# JobQuest Navigator - Unified Database Schema Design

## Overview

This document defines the unified database schema for JobQuest Navigator, consolidating all epic requirements into a cohesive, scalable database architecture. The design is based on the architecture analysis findings and aims to eliminate data fragmentation while supporting all epic functionalities.

## Design Principles

1. **Single Source of Truth**: Eliminate duplicate entities across epics
2. **Normalized Design**: Reduce data redundancy while maintaining performance
3. **Scalable Relationships**: Support future epic additions and feature expansions
4. **Data Integrity**: Enforce referential integrity and business rules
5. **Performance Optimized**: Include appropriate indexes and query optimization
6. **Migration Friendly**: Support gradual migration from existing implementations

## Core Entity Relationship Overview

The unified schema consists of 9 main entity groups:
1. **User Management** - User accounts and profiles
2. **Location Management** - Geographic data normalization
3. **Company Management** - Company information and locations
4. **Job Management** - Job postings and applications (Epic 1)
5. **Skills Management** - Skills and proficiency tracking (Epic 4)
6. **Resume Management** - Resume versions and content (Epic 2)
7. **AI Suggestions** - AI-powered recommendations (Epic 3)
8. **Certification Management** - Certification tracking (Epic 4)
9. **Company Research** - Research and interview prep (Epic 6)

## Core Models

### 1. User Management

#### User Model
```python
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True)
    profile_picture = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Career preferences
    career_level = models.CharField(max_length=50, choices=CAREER_LEVELS, blank=True)
    preferred_salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    preferred_salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    preferred_remote = models.BooleanField(default=False)
```

#### UserProfile Model (Extended user information)
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    years_experience = models.PositiveIntegerField(null=True)
    current_position = models.CharField(max_length=200, blank=True)
    current_company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True)
    education_level = models.CharField(max_length=50, choices=EDUCATION_LEVELS, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 2. Location Management

#### Location Model
```python
class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    timezone = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['city', 'state', 'country']
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['latitude', 'longitude']),
        ]
```

### 3. Company Management

#### Company Model
```python
class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, choices=COMPANY_SIZES, blank=True)
    founded_year = models.PositiveIntegerField(null=True)
    headquarters = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    
    # Company research data (Epic 6)
    culture_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    work_life_balance = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    salary_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    career_opportunities = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['industry']),
            models.Index(fields=['size']),
        ]
```

#### CompanyLocation Model (Multiple office locations)
```python
class CompanyLocation(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='locations')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    is_headquarters = models.BooleanField(default=False)
    office_type = models.CharField(max_length=50, choices=OFFICE_TYPES, default='office')
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['company', 'location']
```

### 4. Job Management (Epic 1)

#### Job Model
```python
class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    external_id = models.CharField(max_length=100, blank=True)  # From external APIs
    title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    
    # Salary information
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    salary_period = models.CharField(max_length=20, choices=SALARY_PERIODS, default='yearly')
    
    # Job details
    job_type = models.CharField(max_length=50, choices=JOB_TYPES, default='full_time')
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVELS)
    remote_type = models.CharField(max_length=50, choices=REMOTE_TYPES, default='on_site')
    
    # External source information
    source = models.CharField(max_length=50, default='adzuna')  # adzuna, linkedin, etc.
    external_url = models.URLField(blank=True)
    
    # Status and dates
    is_active = models.BooleanField(default=True)
    posted_date = models.DateTimeField()
    expires_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['company']),
            models.Index(fields=['location']),
            models.Index(fields=['job_type']),
            models.Index(fields=['experience_level']),
            models.Index(fields=['posted_date']),
            models.Index(fields=['is_active']),
        ]
```

#### JobApplication Model
```python
class JobApplication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    resume_version = models.ForeignKey('ResumeVersion', on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=50, choices=APPLICATION_STATUSES, default='applied')
    applied_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Application tracking
    cover_letter = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'job']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['applied_date']),
        ]
```

### 5. Skills Management (Epic 4)

#### Skill Model
```python
class Skill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50, choices=SKILL_CATEGORIES)
    description = models.TextField(blank=True)
    
    # Skill metadata
    is_technical = models.BooleanField(default=True)
    popularity_score = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_technical']),
        ]
```

#### UserSkill Model (User's skills and proficiency)
```python
class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    years_experience = models.PositiveIntegerField(null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'skill']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['proficiency_level']),
        ]
```

#### JobSkill Model (Skills required for jobs)
```python
class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='required_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    is_required = models.BooleanField(default=True)  # vs nice-to-have
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, blank=True)
    
    class Meta:
        unique_together = ['job', 'skill']
```

### 6. Resume Management (Epic 2)

#### Resume Model
```python
class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    name = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    
    # Resume metadata
    target_position = models.CharField(max_length=200, blank=True)
    target_industry = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_primary']),
        ]
```

#### ResumeVersion Model
```python
class ResumeVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    
    # File information
    file_path = models.CharField(max_length=512)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=50)
    
    # Version details
    comment = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)
    
    # Extracted content (for AI processing)
    extracted_text = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['resume', 'version_number']
        indexes = [
            models.Index(fields=['resume', 'is_current']),
            models.Index(fields=['created_at']),
        ]
```

#### ResumeSkill Model (Skills extracted from resume)
```python
class ResumeSkill(models.Model):
    resume_version = models.ForeignKey(ResumeVersion, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4, null=True)  # AI extraction confidence
    context = models.TextField(blank=True)  # Where in resume this skill was found
    
    class Meta:
        unique_together = ['resume_version', 'skill']
```

### 7. AI Suggestions (Epic 3)

#### AISuggestion Model
```python
class AISuggestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    resume_version = models.ForeignKey(ResumeVersion, on_delete=models.CASCADE, related_name='suggestions')
    suggestion_type = models.CharField(max_length=50, choices=SUGGESTION_TYPES)
    
    # Suggestion content
    title = models.CharField(max_length=200)
    description = models.TextField()
    original_text = models.TextField(blank=True)  # Original text being improved
    suggested_text = models.TextField(blank=True)  # AI suggested improvement
    
    # AI metadata
    ai_model = models.CharField(max_length=50, default='gpt-3.5-turbo')
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4, null=True)
    processing_time = models.DecimalField(max_digits=8, decimal_places=3, null=True)  # seconds
    
    # Status
    status = models.CharField(max_length=20, choices=SUGGESTION_STATUSES, default='pending')
    is_applied = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['resume_version']),
            models.Index(fields=['suggestion_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
```

#### SuggestionFeedback Model
```python
class SuggestionFeedback(models.Model):
    suggestion = models.OneToOneField(AISuggestion, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Feedback ratings
    helpfulness_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 scale
    accuracy_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    
    # Feedback text
    comments = models.TextField(blank=True)
    
    # Feedback metadata
    time_to_feedback = models.DurationField(null=True)  # Time from suggestion to feedback
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['helpfulness_rating']),
            models.Index(fields=['accuracy_rating']),
        ]
```

### 8. Certification Management (Epic 4)

#### Certification Model
```python
class Certification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    provider = models.CharField(max_length=100)  # AWS, Google, Microsoft, etc.
    description = models.TextField(blank=True)
    
    # Certification details
    category = models.CharField(max_length=50, choices=CERT_CATEGORIES)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    estimated_study_hours = models.PositiveIntegerField(null=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Validity
    validity_period_months = models.PositiveIntegerField(null=True)  # null = lifetime
    
    # URLs and resources
    official_url = models.URLField(blank=True)
    study_guide_url = models.URLField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['provider']),
            models.Index(fields=['category']),
            models.Index(fields=['difficulty_level']),
        ]
```

#### SkillCertification Model (Skills that certifications validate)
```python
class SkillCertification(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='certifications')
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE, related_name='skills')
    relevance_score = models.PositiveIntegerField(default=100)  # 0-100 how relevant this cert is to skill
    
    class Meta:
        unique_together = ['skill', 'certification']
```

#### CertificationProgress Model
```python
class CertificationProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certification_progress')
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=CERT_PROGRESS_STATUSES, default='interested')
    progress_percentage = models.PositiveIntegerField(default=0)  # 0-100
    
    # Dates
    started_date = models.DateTimeField(null=True, blank=True)
    target_completion_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Study tracking
    study_hours_logged = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'certification']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['target_completion_date']),
        ]
```

### 9. Company Research (Epic 6)

#### CompanyResearch Model
```python
class CompanyResearch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_research')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='research_data')
    
    # Research data
    research_notes = models.TextField(blank=True)
    pros = models.TextField(blank=True)
    cons = models.TextField(blank=True)
    
    # Ratings (user's personal ratings)
    culture_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True)
    work_life_balance_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True)
    compensation_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True)
    growth_opportunities_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True)
    
    # Research status
    research_status = models.CharField(max_length=20, choices=RESEARCH_STATUSES, default='in_progress')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'company']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['research_status']),
        ]
```

#### InterviewPrep Model
```python
class InterviewPrep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_prep')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='interview_prep')
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Interview details
    interview_type = models.CharField(max_length=50, choices=INTERVIEW_TYPES)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    
    # Preparation materials
    questions_prepared = models.TextField(blank=True)
    answers_prepared = models.TextField(blank=True)
    research_notes = models.TextField(blank=True)
    
    # Status tracking
    prep_status = models.CharField(max_length=20, choices=PREP_STATUSES, default='planning')
    confidence_level = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['prep_status']),
        ]
```

## Choice Field Definitions

```python
# User choices
CAREER_LEVELS = [
    ('entry', 'Entry Level'),
    ('junior', 'Junior'),
    ('mid', 'Mid Level'),
    ('senior', 'Senior'),
    ('lead', 'Lead'),
    ('manager', 'Manager'),
    ('director', 'Director'),
    ('executive', 'Executive'),
]

EDUCATION_LEVELS = [
    ('high_school', 'High School'),
    ('associate', 'Associate Degree'),
    ('bachelor', 'Bachelor\'s Degree'),
    ('master', 'Master\'s Degree'),
    ('phd', 'PhD'),
    ('bootcamp', 'Bootcamp'),
    ('self_taught', 'Self-Taught'),
]

# Company choices
COMPANY_SIZES = [
    ('startup', '1-10 employees'),
    ('small', '11-50 employees'),
    ('medium', '51-200 employees'),
    ('large', '201-1000 employees'),
    ('enterprise', '1000+ employees'),
]

OFFICE_TYPES = [
    ('headquarters', 'Headquarters'),
    ('office', 'Office'),
    ('coworking', 'Coworking Space'),
    ('remote', 'Remote Hub'),
]

# Job choices
JOB_TYPES = [
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('contract', 'Contract'),
    ('freelance', 'Freelance'),
    ('internship', 'Internship'),
]

EXPERIENCE_LEVELS = [
    ('entry', 'Entry Level'),
    ('junior', 'Junior'),
    ('mid', 'Mid Level'),
    ('senior', 'Senior'),
    ('lead', 'Lead'),
    ('manager', 'Manager'),
]

REMOTE_TYPES = [
    ('on_site', 'On-site'),
    ('remote', 'Remote'),
    ('hybrid', 'Hybrid'),
]

SALARY_PERIODS = [
    ('hourly', 'Hourly'),
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly'),
]

APPLICATION_STATUSES = [
    ('applied', 'Applied'),
    ('screening', 'Screening'),
    ('interview', 'Interview'),
    ('offer', 'Offer'),
    ('rejected', 'Rejected'),
    ('withdrawn', 'Withdrawn'),
]

# Skill choices
SKILL_CATEGORIES = [
    ('programming', 'Programming'),
    ('framework', 'Framework'),
    ('database', 'Database'),
    ('cloud', 'Cloud'),
    ('devops', 'DevOps'),
    ('design', 'Design'),
    ('management', 'Management'),
    ('communication', 'Communication'),
    ('language', 'Language'),
    ('other', 'Other'),
]

PROFICIENCY_LEVELS = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ('expert', 'Expert'),
]

# AI Suggestion choices
SUGGESTION_TYPES = [
    ('content_improvement', 'Content Improvement'),
    ('formatting', 'Formatting'),
    ('keyword_optimization', 'Keyword Optimization'),
    ('skill_highlighting', 'Skill Highlighting'),
    ('job_matching', 'Job Matching'),
    ('section_reorder', 'Section Reordering'),
]

SUGGESTION_STATUSES = [
    ('pending', 'Pending Review'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('applied', 'Applied'),
]

# Certification choices
CERT_CATEGORIES = [
    ('cloud', 'Cloud Computing'),
    ('security', 'Security'),
    ('data', 'Data & Analytics'),
    ('development', 'Software Development'),
    ('project_management', 'Project Management'),
    ('design', 'Design'),
    ('marketing', 'Marketing'),
    ('other', 'Other'),
]

DIFFICULTY_LEVELS = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ('expert', 'Expert'),
]

CERT_PROGRESS_STATUSES = [
    ('interested', 'Interested'),
    ('planning', 'Planning'),
    ('studying', 'Studying'),
    ('scheduled', 'Exam Scheduled'),
    ('completed', 'Completed'),
    ('expired', 'Expired'),
    ('abandoned', 'Abandoned'),
]

# Company Research choices
RESEARCH_STATUSES = [
    ('planning', 'Planning'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('on_hold', 'On Hold'),
]

INTERVIEW_TYPES = [
    ('phone', 'Phone Screen'),
    ('video', 'Video Interview'),
    ('technical', 'Technical Interview'),
    ('behavioral', 'Behavioral Interview'),
    ('panel', 'Panel Interview'),
    ('on_site', 'On-site Interview'),
    ('final', 'Final Interview'),
]

PREP_STATUSES = [
    ('planning', 'Planning'),
    ('researching', 'Researching'),
    ('practicing', 'Practicing'),
    ('ready', 'Ready'),
    ('completed', 'Completed'),
]
```

## Database Indexes Strategy

### Primary Indexes (Automatic)
- All primary keys (UUID fields)
- Unique constraints and unique_together fields

### Performance Indexes
```python
# User-related queries
models.Index(fields=['user', 'created_at'])  # User activity timeline
models.Index(fields=['user', 'status'])      # User's items by status

# Search and filtering
models.Index(fields=['name'])                # Name-based searches
models.Index(fields=['title'])               # Job/resume title searches
models.Index(fields=['category'])            # Category filtering
models.Index(fields=['location'])            # Location-based queries

# Date-based queries
models.Index(fields=['created_at'])          # Chronological ordering
models.Index(fields=['updated_at'])          # Recently updated items
models.Index(fields=['posted_date'])         # Job posting dates

# Status and type filtering
models.Index(fields=['status'])              # Status-based filtering
models.Index(fields=['is_active'])           # Active/inactive filtering
models.Index(fields=['job_type'])            # Job type filtering

# Geolocation queries
models.Index(fields=['latitude', 'longitude'])  # Geospatial queries
```

## Migration Strategy

### Phase 1: Core Models Migration
1. **User and Authentication**
   - Migrate from Epic 2's user system
   - Extend with profile information
   - Maintain existing JWT authentication

2. **Location and Company**
   - Create new location normalization
   - Consolidate company data from all epics
   - Geocode existing location strings

### Phase 2: Epic-Specific Migrations
1. **Epic 1 (Jobs)** - Migrate CSV data to Job model
2. **Epic 2 (Resumes)** - Direct migration (minimal changes)
3. **Epic 3 (AI Suggestions)** - Create suggestion and feedback tables

### Phase 3: New Epic Implementation
1. **Epic 4 (Certifications)** - Implement skill and certification models
2. **Epic 6 (Company Research)** - Implement research and interview prep models

## Key Benefits

1. **Unified User Experience**: Single user account across all epics
2. **Data Consistency**: Normalized company and location data
3. **Cross-Epic Features**: Skills from resumes inform job matching and certifications
4. **Scalable Architecture**: UUID primary keys and proper indexing
5. **Migration Friendly**: Clear path from current implementations

## Performance Considerations

### Strategic Indexing
- User-based queries (most common access pattern)
- Location-based searches for jobs
- Skill and certification lookups
- Date-based filtering and sorting

### Query Optimization
- Eager loading for related objects
- Database-level constraints for data integrity
- Caching strategies for frequently accessed data

## Security Features

1. **User Data Isolation**: All user data filtered by user_id
2. **File Access Control**: S3 presigned URLs for secure file access
3. **Audit Trails**: Track changes for critical models
4. **Row-Level Security**: Users can only access their own data

## Conclusion

This unified database schema provides comprehensive coverage for all 5 epic requirements while maintaining scalability, performance, and data integrity. The design eliminates current data fragmentation and provides a solid foundation for the frontend-backend separation architecture.

---

**Design Date:** December 19, 2024  
**Designer:** AI Database Architect  
**Next Steps:** Proceed with Task 3 - Django Project Structure Setup 