"""
Management command to populate test job applications for demo purposes.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime, timedelta
import random

from jobs.models import Job, JobApplication
from core.models import Company, Location

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate test job applications for demo purposes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate job applications...'))
        
        # Get or create test user
        test_user, _ = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True
            }
        )
        
        # Create some test jobs if they don't exist
        self.create_test_jobs()
        
        # Create job applications
        self.create_job_applications(test_user)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated job applications!'))

    def create_test_jobs(self):
        """Create test jobs for applications."""
        # Get or create test companies and locations
        companies_data = [
            {'name': 'TechCorp Inc.', 'description': 'Leading technology company'},
            {'name': 'DataSoft LLC', 'description': 'Data analytics and software company'},
            {'name': 'CloudSolutions Ltd.', 'description': 'Cloud computing services'},
            {'name': 'StartupXYZ', 'description': 'Innovative startup company'},
            {'name': 'Enterprise Systems', 'description': 'Enterprise software solutions'}
        ]
        
        locations_data = [
            {'city': 'San Francisco', 'state': 'CA', 'country': 'US'},
            {'city': 'New York', 'state': 'NY', 'country': 'US'},
            {'city': 'Seattle', 'state': 'WA', 'country': 'US'},
            {'city': 'Austin', 'state': 'TX', 'country': 'US'},
            {'city': 'Boston', 'state': 'MA', 'country': 'US'}
        ]
        
        # Create companies
        companies = []
        for comp_data in companies_data:
            company, created = Company.objects.get_or_create(
                name=comp_data['name'],
                defaults={
                    'slug': slugify(comp_data['name']),
                    'description': comp_data['description'],
                    'website': f"https://www.{comp_data['name'].lower().replace(' ', '').replace('.', '')}.com",
                    'company_size': random.choice(['startup', 'small', 'medium', 'large']),
                    'industry': random.choice(['technology', 'finance', 'healthcare', 'education'])
                }
            )
            companies.append(company)
            if created:
                self.stdout.write(f'Created company: {company.name}')
        
        # Create locations
        locations = []
        for loc_data in locations_data:
            location, created = Location.objects.get_or_create(
                city=loc_data['city'],
                state=loc_data['state'],
                country=loc_data['country'],
                defaults={
                    'name': f"{loc_data['city']}, {loc_data['state']}",
                    'country_code': 'US',
                    'latitude': random.uniform(25.0, 49.0),
                    'longitude': random.uniform(-125.0, -66.0)
                }
            )
            locations.append(location)
            if created:
                self.stdout.write(f'Created location: {location.display_name}')
        
        # Create jobs
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'description': 'We are looking for an experienced Python developer to join our backend team.',
                'requirements': 'Python, Django, REST APIs, PostgreSQL, 5+ years experience',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 120000,
                'salary_max': 160000
            },
            {
                'title': 'Frontend React Developer',
                'description': 'Join our frontend team to build amazing user experiences with React.',
                'requirements': 'React, JavaScript, TypeScript, CSS, HTML, 3+ years experience',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 90000,
                'salary_max': 130000
            },
            {
                'title': 'Data Scientist',
                'description': 'Analyze large datasets and build machine learning models.',
                'requirements': 'Python, Machine Learning, Statistics, SQL, Pandas, NumPy',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 110000,
                'salary_max': 150000
            },
            {
                'title': 'DevOps Engineer',
                'description': 'Manage cloud infrastructure and deployment pipelines.',
                'requirements': 'AWS, Docker, Kubernetes, CI/CD, Infrastructure as Code',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 130000,
                'salary_max': 170000
            },
            {
                'title': 'Junior Full Stack Developer',
                'description': 'Entry-level position for full stack development.',
                'requirements': 'JavaScript, React, Node.js, Basic database knowledge',
                'experience_level': 'junior',
                'job_type': 'full_time',
                'remote_type': 'on_site',
                'salary_min': 70000,
                'salary_max': 90000
            },
            {
                'title': 'Product Manager',
                'description': 'Lead product development and strategy.',
                'requirements': 'Product management experience, Agile, Analytics',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 140000,
                'salary_max': 180000
            }
        ]
        
        for i, job_data in enumerate(jobs_data):
            company = companies[i % len(companies)]
            location = locations[i % len(locations)]
            
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=company,
                defaults={
                    'location': location,
                    'description': job_data['description'],
                    'requirements': job_data['requirements'],
                    'experience_level': job_data['experience_level'],
                    'job_type': job_data['job_type'],
                    'remote_type': job_data['remote_type'],
                    'salary_min': job_data['salary_min'],
                    'salary_max': job_data['salary_max'],
                    'posted_date': timezone.now() - timedelta(days=random.randint(1, 30)),
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created job: {job.title} at {job.company.name}')

    def create_job_applications(self, user):
        """Create test job applications."""
        jobs = list(Job.objects.filter(is_active=True)[:4])  # Get first 4 jobs
        
        statuses = ['applied', 'screening', 'interview', 'rejected']
        
        application_notes = [
            "Applied through company website. Resume and cover letter submitted.",
            "Initial phone screening completed. Positive feedback from recruiter.",
            "Technical interview scheduled for next week. Need to prepare algorithms.",
            "Unfortunately, they decided to go with another candidate. Feedback received.",
            "Coding challenge completed and submitted on time.",
            "Final round interview with team lead completed.",
            "Waiting for feedback from the hiring manager.",
        ]
        
        for i, job in enumerate(jobs):
            # Check if application already exists
            if JobApplication.objects.filter(user=user, job=job).exists():
                continue
                
            status = statuses[i % len(statuses)]
            applied_date = timezone.now() - timedelta(days=random.randint(5, 45))
            
            # Create more detailed notes based on status
            if status == 'applied':
                notes = "Application submitted. Waiting for initial response."
            elif status == 'screening':
                notes = "Phone screening completed. HR interview went well. Next step: technical interview."
            elif status == 'interview':
                notes = "Technical interview completed. Presented solution to coding challenge. Waiting for final decision."
            elif status == 'rejected':
                notes = "Application was not successful. Good experience overall. Will apply to similar roles."
            else:
                notes = random.choice(application_notes)
            
            application = JobApplication.objects.create(
                user=user,
                job=job,
                status=status,
                applied_date=applied_date,
                notes=notes,
                cover_letter=f"Dear Hiring Manager,\n\nI am excited to apply for the {job.title} position at {job.company.name}. With my background in software development and passion for technology, I believe I would be a great fit for your team.\n\nBest regards,\n{user.first_name} {user.last_name}"
            )
            
            self.stdout.write(f'Created application: {application.job.title} - {application.status}')