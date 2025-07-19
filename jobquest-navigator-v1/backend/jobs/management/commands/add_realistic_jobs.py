"""
Django management command to add realistic programmer jobs for testing.
Creates 5 realistic programmer jobs in Los Angeles with current data.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

from core.models import Company, Location
from jobs.models import Job


class Command(BaseCommand):
    help = 'Add realistic programmer jobs in Los Angeles for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of jobs to create (default: 5)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing jobs before adding new ones',
        )
    
    def handle(self, *args, **options):
        count = options['count']
        clear_existing = options['clear']
        
        if clear_existing:
            self.stdout.write('Clearing existing jobs...')
            Job.objects.all().delete()
            Company.objects.all().delete()
            Location.objects.all().delete()
        
        self.stdout.write(f'Creating {count} realistic programmer jobs in Los Angeles...')
        
        # Create Los Angeles location
        la_location, _ = Location.objects.get_or_create(
            city='Los Angeles',
            state='CA',
            country='USA',
            defaults={
                'name': 'Los Angeles',
                'country_code': 'US',
                'latitude': Decimal('34.0522'),
                'longitude': Decimal('-118.2437'),
                'google_formatted_address': 'Los Angeles, CA, USA'
            }
        )
        
        # Real tech companies in LA
        companies_data = [
            {
                'name': 'SpaceX',
                'description': 'Space exploration technologies company founded by Elon Musk',
                'website': 'https://spacex.com',
                'industry': 'Aerospace',
                'company_size': '5000-10000'
            },
            {
                'name': 'Snap Inc.',
                'description': 'Technology company behind Snapchat and AR innovations',
                'website': 'https://snap.com',
                'industry': 'Social Media',
                'company_size': '1000-5000'
            },
            {
                'name': 'Riot Games',
                'description': 'Video game developer and esports company behind League of Legends',
                'website': 'https://riotgames.com',
                'industry': 'Gaming',
                'company_size': '1000-5000'
            },
            {
                'name': 'Dollar Shave Club',
                'description': 'E-commerce subscription service for personal grooming products',
                'website': 'https://dollarshaveclub.com',
                'industry': 'E-commerce',
                'company_size': '500-1000'
            },
            {
                'name': 'Bird',
                'description': 'Electric scooter sharing company revolutionizing urban transportation',
                'website': 'https://bird.co',
                'industry': 'Transportation',
                'company_size': '500-1000'
            }
        ]
        
        # Realistic job data
        jobs_data = [
            {
                'title': 'Senior Full Stack Developer',
                'description': 'Join our engineering team to build scalable web applications using React, Node.js, and Python. You will work on high-impact features that serve millions of users worldwide. Experience with cloud platforms (AWS/GCP) and containerization is highly valued.',
                'requirements': 'BS in Computer Science or equivalent, 5+ years experience, React, Node.js, Python, AWS, Docker',
                'benefits': 'Competitive salary, equity, health insurance, 401k matching, flexible work schedule, learning budget',
                'salary_min': Decimal('130000'),
                'salary_max': Decimal('180000'),
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid'
            },
            {
                'title': 'Frontend Engineer - React Specialist',
                'description': 'We are seeking a passionate Frontend Engineer to join our product team. You will be responsible for creating beautiful, responsive user interfaces and ensuring excellent user experience across our platform. Work with modern JavaScript frameworks and cutting-edge tools.',
                'requirements': 'Strong JavaScript/TypeScript skills, 3+ years React experience, CSS3, HTML5, Redux/Context API',
                'benefits': 'Stock options, comprehensive health coverage, unlimited PTO, free meals, gym membership',
                'salary_min': Decimal('110000'),
                'salary_max': Decimal('150000'),
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote'
            },
            {
                'title': 'Backend Developer - Python/Django',
                'description': 'Build and maintain robust backend systems that power our mobile and web applications. Work with large-scale distributed systems, databases, and API development. Opportunity to work on machine learning infrastructure and data processing pipelines.',
                'requirements': 'Python expertise, Django/Flask framework, PostgreSQL/MySQL, REST APIs, microservices architecture',
                'benefits': 'Competitive compensation, equity package, professional development fund, work from home stipend',
                'salary_min': Decimal('120000'),
                'salary_max': Decimal('160000'),
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid'
            },
            {
                'title': 'DevOps Engineer - Cloud Infrastructure',
                'description': 'Lead our infrastructure automation and deployment processes. Design and implement CI/CD pipelines, manage cloud resources, and ensure system reliability. Work with Kubernetes, Docker, and modern monitoring tools to support our growing platform.',
                'requirements': 'AWS/GCP expertise, Kubernetes, Docker, Terraform, Jenkins/GitLab CI, monitoring tools (Prometheus, Grafana)',
                'benefits': 'Excellent salary, equity, health/dental/vision, parental leave, conference attendance budget',
                'salary_min': Decimal('140000'),
                'salary_max': Decimal('190000'),
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'on_site'
            },
            {
                'title': 'Mobile Developer - iOS/Android',
                'description': 'Develop native mobile applications for iOS and Android platforms. Collaborate with design and backend teams to create seamless user experiences. Experience with cross-platform frameworks like React Native or Flutter is a plus.',
                'requirements': 'iOS (Swift) or Android (Kotlin/Java) experience, mobile app architecture, REST API integration, App Store/Play Store deployment',
                'benefits': 'Competitive base salary, performance bonuses, health benefits, flexible hours, professional development',
                'salary_min': Decimal('115000'),
                'salary_max': Decimal('155000'),
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid'
            }
        ]
        
        # Create companies and jobs
        for i in range(min(count, len(jobs_data))):
            company_data = companies_data[i % len(companies_data)]
            job_data = jobs_data[i]
            
            # Create or get company
            company, created = Company.objects.get_or_create(
                name=company_data['name'],
                defaults={
                    'description': company_data['description'],
                    'website': company_data['website'],
                    'industry': company_data['industry'],
                    'company_size': company_data['company_size'],
                    'headquarters': la_location
                }
            )
            
            if created:
                self.stdout.write(f'Created company: {company.name}')
            
            # Create job
            posted_date = timezone.now() - timedelta(days=random.randint(1, 14))
            expires_date = posted_date + timedelta(days=30)
            
            job = Job.objects.create(
                title=job_data['title'],
                company=company,
                location=la_location,
                description=job_data['description'],
                requirements=job_data['requirements'],
                benefits=job_data['benefits'],
                salary_min=job_data['salary_min'],
                salary_max=job_data['salary_max'],
                salary_currency='USD',
                salary_period='annual',
                job_type=job_data['job_type'],
                experience_level=job_data['experience_level'],
                remote_type=job_data['remote_type'],
                source='manual',
                external_url=company_data['website'] + '/careers',
                is_active=True,
                posted_date=posted_date,
                expires_date=expires_date
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created job: {job.title} at {company.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} programmer jobs in Los Angeles!')
        )