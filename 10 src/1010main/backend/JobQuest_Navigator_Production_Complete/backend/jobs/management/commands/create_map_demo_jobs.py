"""
Management command to create demo jobs for map visualization with different locations.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime, timedelta
import random

from jobs.models import Job
from core.models import Company, Location

class Command(BaseCommand):
    help = 'Create demo jobs for map visualization with various locations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating map demo jobs...'))
        
        # Create locations for major tech cities
        locations_data = [
            {'city': 'San Francisco', 'state': 'CA', 'country': 'United States', 'lat': 37.7749, 'lng': -122.4194},
            {'city': 'New York', 'state': 'NY', 'country': 'United States', 'lat': 40.7128, 'lng': -74.0060},
            {'city': 'Seattle', 'state': 'WA', 'country': 'United States', 'lat': 47.6062, 'lng': -122.3321},
            {'city': 'Austin', 'state': 'TX', 'country': 'United States', 'lat': 30.2672, 'lng': -97.7431},
            {'city': 'Boston', 'state': 'MA', 'country': 'United States', 'lat': 42.3601, 'lng': -71.0589},
            {'city': 'Denver', 'state': 'CO', 'country': 'United States', 'lat': 39.7392, 'lng': -104.9903},
            {'city': 'Los Angeles', 'state': 'CA', 'country': 'United States', 'lat': 34.0522, 'lng': -118.2437},
            {'city': 'Chicago', 'state': 'IL', 'country': 'United States', 'lat': 41.8781, 'lng': -87.6298},
        ]
        
        # Create companies
        companies_data = [
            {'name': 'Google', 'industry': 'technology', 'size': 'enterprise'},
            {'name': 'Microsoft', 'industry': 'technology', 'size': 'enterprise'},
            {'name': 'Amazon', 'industry': 'technology', 'size': 'enterprise'},
            {'name': 'Apple', 'industry': 'technology', 'size': 'enterprise'},
            {'name': 'Netflix', 'industry': 'entertainment', 'size': 'large'},
            {'name': 'Uber', 'industry': 'technology', 'size': 'large'},
            {'name': 'Airbnb', 'industry': 'technology', 'size': 'large'},
            {'name': 'Stripe', 'industry': 'fintech', 'size': 'medium'},
        ]
        
        # Create jobs data
        jobs_data = [
            {'title': 'Senior Software Engineer', 'level': 'senior', 'type': 'full_time', 'remote': 'hybrid', 'min_sal': 140000, 'max_sal': 200000},
            {'title': 'Frontend Developer', 'level': 'mid', 'type': 'full_time', 'remote': 'remote', 'min_sal': 90000, 'max_sal': 130000},
            {'title': 'Backend Engineer', 'level': 'mid', 'type': 'full_time', 'remote': 'hybrid', 'min_sal': 100000, 'max_sal': 150000},
            {'title': 'Data Scientist', 'level': 'senior', 'type': 'full_time', 'remote': 'hybrid', 'min_sal': 120000, 'max_sal': 170000},
            {'title': 'DevOps Engineer', 'level': 'senior', 'type': 'full_time', 'remote': 'remote', 'min_sal': 130000, 'max_sal': 180000},
            {'title': 'Product Manager', 'level': 'senior', 'type': 'full_time', 'remote': 'hybrid', 'min_sal': 150000, 'max_sal': 220000},
            {'title': 'UI/UX Designer', 'level': 'mid', 'type': 'full_time', 'remote': 'remote', 'min_sal': 80000, 'max_sal': 120000},
            {'title': 'Machine Learning Engineer', 'level': 'senior', 'type': 'full_time', 'remote': 'hybrid', 'min_sal': 160000, 'max_sal': 230000},
            {'title': 'Full Stack Developer', 'level': 'mid', 'type': 'full_time', 'remote': 'remote', 'min_sal': 95000, 'max_sal': 140000},
            {'title': 'Security Engineer', 'level': 'senior', 'type': 'full_time', 'remote': 'hybrid', 'min_sal': 135000, 'max_sal': 190000},
        ]
        
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
                    'latitude': loc_data['lat'],
                    'longitude': loc_data['lng'],
                    'google_place_id': f"demo_{slugify(loc_data['city'])}_{slugify(loc_data['state'])}"
                }
            )
            locations.append(location)
            if created:
                self.stdout.write(f'Created location: {location.name}')
        
        # Create companies
        companies = []
        for comp_data in companies_data:
            company, created = Company.objects.get_or_create(
                name=comp_data['name'],
                defaults={
                    'slug': slugify(comp_data['name']),
                    'description': f"{comp_data['name']} is a leading {comp_data['industry']} company.",
                    'website': f"https://www.{comp_data['name'].lower()}.com",
                    'company_size': comp_data['size'],
                    'industry': comp_data['industry'],
                    'headquarters': random.choice(locations)
                }
            )
            companies.append(company)
            if created:
                self.stdout.write(f'Created company: {company.name}')
        
        # Create jobs
        jobs_created = 0
        for _ in range(20):  # Create 20 jobs
            job_data = random.choice(jobs_data)
            company = random.choice(companies)
            location = random.choice(locations)
            
            # Check if similar job already exists
            if Job.objects.filter(title=job_data['title'], company=company, location=location).exists():
                continue
            
            job = Job.objects.create(
                title=job_data['title'],
                company=company,
                location=location,
                description=f"We are looking for a talented {job_data['title']} to join our {company.name} team in {location.city}. This is an exciting opportunity to work with cutting-edge technology and make a real impact.",
                requirements=f"• {random.choice(['5+', '3+', '7+'])} years of experience\n• Strong programming skills\n• Team collaboration\n• Problem-solving abilities",
                benefits="• Competitive salary\n• Health insurance\n• 401k matching\n• Flexible work hours\n• Professional development",
                experience_level=job_data['level'],
                job_type=job_data['type'],
                remote_type=job_data['remote'],
                salary_min=job_data['min_sal'],
                salary_max=job_data['max_sal'],
                salary_currency='USD',
                salary_period='yearly',
                posted_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                is_active=True
            )
            
            jobs_created += 1
            self.stdout.write(f'Created job: {job.title} at {job.company.name} in {job.location.city}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {jobs_created} demo jobs for map visualization!'))