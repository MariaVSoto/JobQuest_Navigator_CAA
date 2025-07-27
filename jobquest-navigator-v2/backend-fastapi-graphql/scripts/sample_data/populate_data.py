#!/usr/bin/env python3
"""
Sample Data Population Script for JobQuest Navigator v2
Generates realistic demo data based on user personas and company profiles
"""

import asyncio
import json
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker

from app.core.database import get_async_db_session
from app.models.user import User, UserPreference, ActivityLog
from app.models.job import Job, Company, Skill, JobApplication, SavedJob, JobSkill


class SampleDataGenerator:
    """Generate realistic sample data for demo purposes"""
    
    def __init__(self, config_path: str = None):
        self.fake = Faker()
        self.config_path = config_path or Path(__file__).parent / "config.json"
        self.config = self._load_config()
        self.generated_ids = {
            'users': [],
            'companies': [],
            'skills': [],
            'jobs': [],
            'applications': [],
            'saved_jobs': []
        }
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    async def populate_all_data(self, num_users: int = 5) -> Dict[str, int]:
        """Generate all sample data"""
        print("🚀 Starting sample data generation...")
        
        async with get_async_db_session() as db:
            stats = {
                'users': 0,
                'companies': 0,
                'skills': 0,
                'jobs': 0,
                'applications': 0,
                'saved_jobs': 0,
                'activities': 0
            }
            
            # Step 1: Create skills
            print("📊 Creating skills...")
            await self._create_skills(db)
            stats['skills'] = len(self.generated_ids['skills'])
            
            # Step 2: Create companies
            print("🏢 Creating companies...")
            await self._create_companies(db)
            stats['companies'] = len(self.generated_ids['companies'])
            
            # Step 3: Create users with personas
            print("👥 Creating users...")
            await self._create_users(db, num_users)
            stats['users'] = len(self.generated_ids['users'])
            
            # Step 4: Create jobs
            print("💼 Creating jobs...")
            await self._create_jobs(db)
            stats['jobs'] = len(self.generated_ids['jobs'])
            
            # Step 5: Create applications and saved jobs
            print("📝 Creating applications and saved jobs...")
            await self._create_applications_and_saves(db)
            stats['applications'] = len(self.generated_ids['applications'])
            stats['saved_jobs'] = len(self.generated_ids['saved_jobs'])
            
            # Step 6: Create activity logs
            print("📈 Creating activity logs...")
            await self._create_activity_logs(db)
            stats['activities'] = await self._count_activities(db)
            
            await db.commit()
            
        print("✅ Sample data generation completed!")
        return stats
    
    async def _create_skills(self, db: AsyncSession):
        """Create skills from configuration"""
        skills_data = self.config['sample_data_config']['skills_database']
        
        for skill_name in skills_data:
            skill = Skill(
                id=uuid.uuid4(),
                name=skill_name,
                slug=skill_name.lower().replace(' ', '-'),
                category=self._categorize_skill(skill_name),
                description=f"Professional skill in {skill_name}",
                is_technical=self._is_technical_skill(skill_name),
                popularity_score=random.randint(50, 100)
            )
            db.add(skill)
            self.generated_ids['skills'].append(str(skill.id))
        
        await db.flush()
        print(f"  ✅ Created {len(skills_data)} skills")
    
    async def _create_companies(self, db: AsyncSession):
        """Create companies from configuration"""
        companies_data = self.config['sample_data_config']['companies']
        
        for company_data in companies_data:
            company = Company(
                id=uuid.uuid4(),
                name=company_data['name'],
                slug=company_data['slug'],
                description=company_data['description'],
                website=company_data['website'],
                industry=company_data['industry'],
                company_size=company_data['company_size'],
                founded_year=company_data['founded_year'],
                email=f"contact@{company_data['slug']}.com",
                phone=self.fake.phone_number(),
                linkedin_url=f"https://linkedin.com/company/{company_data['slug']}",
                glassdoor_rating=round(random.uniform(3.5, 4.8), 1),
                glassdoor_review_count=random.randint(50, 500)
            )
            db.add(company)
            self.generated_ids['companies'].append(str(company.id))
        
        await db.flush()
        print(f"  ✅ Created {len(companies_data)} companies")
    
    async def _create_users(self, db: AsyncSession, num_users: int):
        """Create users based on personas"""
        personas = self.config['sample_data_config']['user_personas']
        surnames = self.config['sample_data_config']['surnames']
        
        for i in range(num_users):
            persona = random.choice(personas)
            surname = random.choice(surnames)
            
            # Generate user data based on persona
            full_name_template = random.choice(persona['full_name_templates'])
            full_name = full_name_template.format(surname=surname)
            email = persona['email_template'].format(index=i+1)
            
            # Parse first and last name
            name_parts = full_name.split(' ')
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else surname
            
            user = User(
                id=uuid.uuid4(),
                email=email,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                bio=persona['bio_template'].format(
                    industry=persona['industry'],
                    years_of_experience=persona.get('years_of_experience', 0),
                    previous_industry=persona.get('previous_industry', 'previous field')
                ),
                current_job_title=persona.get('current_job_title'),
                years_of_experience=persona.get('years_of_experience', 0),
                industry=persona['industry'],
                career_level=persona['career_level'],
                job_search_status=persona['job_search_status'],
                preferred_work_type=persona['preferred_work_type'],
                profile_picture=f"https://api.dicebear.com/7.x/personas/svg?seed={first_name}",
                is_active=True
            )
            
            db.add(user)
            self.generated_ids['users'].append(str(user.id))
            
            # Create user preferences
            preference = UserPreference(
                id=uuid.uuid4(),
                user_id=user.id,
                preferred_salary_min=random.randint(70000, 120000),
                preferred_salary_max=random.randint(120000, 200000),
                preferred_locations=random.sample(
                    self.config['sample_data_config']['locations'], 
                    random.randint(2, 4)
                ),
                preferred_work_types=[persona['preferred_work_type']],
                notification_email=True,
                notification_job_matches=True,
                notification_application_updates=True
            )
            db.add(preference)
        
        await db.flush()
        print(f"  ✅ Created {num_users} users with personas")
    
    async def _create_jobs(self, db: AsyncSession):
        """Create jobs based on company data and templates"""
        companies_data = self.config['sample_data_config']['companies']
        job_templates = self.config['sample_data_config']['job_templates']
        locations = self.config['sample_data_config']['locations']
        
        for company_data in companies_data:
            # Create 3-5 jobs per company
            num_jobs = random.randint(3, 5)
            
            for _ in range(num_jobs):
                job_type = random.choice(company_data['job_types'])
                location = random.choice(company_data['location_preferences'])
                
                # Get template for job type (fallback to Software Engineer)
                template_key = job_type if job_type in job_templates else 'Software Engineer'
                template = job_templates[template_key]
                
                # Determine experience level and salary
                experience_level = random.choice(['entry', 'mid', 'senior'])
                salary_range = template['salary_ranges'][experience_level]
                
                # Generate job content
                job = Job(
                    id=uuid.uuid4(),
                    title=job_type,
                    company_id=uuid.UUID([c for c in self.generated_ids['companies'] 
                                        if str(c) in [str(cid) for cid in self.generated_ids['companies']]][
                                       companies_data.index(company_data)]),
                    description=self._generate_job_description(template, company_data),
                    requirements=self._generate_job_requirements(template, experience_level),
                    benefits=self._generate_job_benefits(template, company_data),
                    location_text=location,
                    salary_min=salary_range['min'],
                    salary_max=salary_range['max'],
                    salary_currency='USD',
                    salary_period='yearly',
                    job_type=self._map_job_type(job_type),
                    contract_type='permanent',
                    experience_level=experience_level,
                    remote_type=self._determine_remote_type(location),
                    user_input=True,
                    source='user_input',
                    posted_date=self.fake.date_time_between(start_date='-30d', end_date='now'),
                    expires_date=self.fake.date_time_between(start_date='now', end_date='+60d'),
                    is_active=True
                )
                
                db.add(job)
                self.generated_ids['jobs'].append(str(job.id))
        
        await db.flush()
        print(f"  ✅ Created {len(self.generated_ids['jobs'])} jobs")
    
    async def _create_applications_and_saves(self, db: AsyncSession):
        """Create job applications and saved jobs based on persona behavior"""
        personas = self.config['sample_data_config']['user_personas']
        
        for user_id in self.generated_ids['users']:
            # Determine persona for this user (simplified approach)
            persona = random.choice(personas)
            behavior = persona['application_behavior']
            
            # Calculate number of applications for this user
            monthly_apps = behavior['applications_per_month']
            total_apps = random.randint(max(1, monthly_apps - 5), monthly_apps + 5)
            
            # Select random jobs for applications
            available_jobs = random.sample(
                self.generated_ids['jobs'], 
                min(total_apps, len(self.generated_ids['jobs']))
            )
            
            for job_id in available_jobs:
                # Determine application status based on persona behavior
                status = self._determine_application_status(behavior['typical_statuses'])
                
                application = JobApplication(
                    id=uuid.uuid4(),
                    user_id=uuid.UUID(user_id),
                    job_id=uuid.UUID(job_id),
                    status=status,
                    applied_date=self.fake.date_time_between(start_date='-90d', end_date='now'),
                    last_updated=self.fake.date_time_between(start_date='-30d', end_date='now'),
                    cover_letter=self._generate_cover_letter(),
                    notes=self._generate_application_notes(status)
                )
                
                db.add(application)
                self.generated_ids['applications'].append(str(application.id))
            
            # Create some saved jobs (not applied to)
            remaining_jobs = [j for j in self.generated_ids['jobs'] if j not in available_jobs]
            if remaining_jobs:
                num_saved = random.randint(2, 8)
                saved_jobs = random.sample(
                    remaining_jobs, 
                    min(num_saved, len(remaining_jobs))
                )
                
                for job_id in saved_jobs:
                    saved_job = SavedJob(
                        id=uuid.uuid4(),
                        user_id=uuid.UUID(user_id),
                        job_id=uuid.UUID(job_id),
                        saved_date=self.fake.date_time_between(start_date='-60d', end_date='now'),
                        notes=self._generate_saved_job_notes()
                    )
                    
                    db.add(saved_job)
                    self.generated_ids['saved_jobs'].append(str(saved_job.id))
        
        await db.flush()
        print(f"  ✅ Created {len(self.generated_ids['applications'])} applications and {len(self.generated_ids['saved_jobs'])} saved jobs")
    
    async def _create_activity_logs(self, db: AsyncSession):
        """Create activity logs for user actions"""
        activity_types = ['job_view', 'job_save', 'job_apply', 'profile_update', 'search']
        
        for user_id in self.generated_ids['users']:
            # Create 10-30 activities per user
            num_activities = random.randint(10, 30)
            
            for _ in range(num_activities):
                activity_type = random.choice(activity_types)
                related_job = random.choice(self.generated_ids['jobs']) if activity_type.startswith('job_') else None
                
                activity = ActivityLog(
                    id=uuid.uuid4(),
                    user_id=uuid.UUID(user_id),
                    activity_type=activity_type,
                    description=self._generate_activity_description(activity_type),
                    related_job_id=uuid.UUID(related_job) if related_job else None,
                    metadata=self._generate_activity_metadata(activity_type),
                    timestamp=self.fake.date_time_between(start_date='-90d', end_date='now')
                )
                
                db.add(activity)
        
        await db.flush()
        print(f"  ✅ Created activity logs")
    
    def _categorize_skill(self, skill_name: str) -> str:
        """Categorize a skill"""
        technical_keywords = ['javascript', 'python', 'java', 'react', 'node', 'sql', 'aws', 'docker']
        if any(keyword in skill_name.lower() for keyword in technical_keywords):
            return 'Technical'
        elif skill_name.lower() in ['communication', 'leadership', 'management', 'agile', 'scrum']:
            return 'Soft Skills'
        else:
            return 'Professional'
    
    def _is_technical_skill(self, skill_name: str) -> bool:
        """Determine if a skill is technical"""
        technical_keywords = ['javascript', 'python', 'java', 'typescript', 'react', 'node', 'angular', 'vue',
                             'html', 'css', 'sql', 'mongodb', 'redis', 'docker', 'kubernetes', 'aws', 'azure', 'gcp']
        return any(keyword in skill_name.lower() for keyword in technical_keywords)
    
    def _generate_job_description(self, template: Dict, company_data: Dict) -> str:
        """Generate job description from template"""
        product_types = ['web', 'mobile', 'enterprise', 'consumer', 'B2B', 'SaaS']
        return template['description_template'].format(
            product_type=random.choice(product_types)
        )
    
    def _generate_job_requirements(self, template: Dict, experience_level: str) -> str:
        """Generate job requirements from template"""
        languages = ['Python', 'JavaScript', 'Java', 'TypeScript']
        frameworks = ['React', 'Vue.js', 'Angular', 'Node.js', 'Django', 'FastAPI']
        additional_reqs = [
            'Experience with cloud platforms',
            'Knowledge of database design',
            'Familiarity with CI/CD pipelines',
            'Experience with testing frameworks'
        ]
        
        experience_text = f"{random.randint(1, 8)}+ years" if experience_level != 'entry' else "0-2 years"
        
        return template['requirements_template'].format(
            experience_level=experience_text,
            primary_language=random.choice(languages),
            secondary_language=random.choice([l for l in languages if l != random.choice(languages)]),
            framework=random.choice(frameworks),
            additional_requirement=random.choice(additional_reqs)
        )
    
    def _generate_job_benefits(self, template: Dict, company_data: Dict) -> str:
        """Generate job benefits from template"""
        company_benefits = [
            'Annual team retreats',
            'Learning stipend',
            'Latest equipment',
            'Catered meals',
            'Gym membership',
            'Mental health support'
        ]
        
        return template['benefits_template'].format(
            company_specific_benefit=random.choice(company_benefits)
        )
    
    def _map_job_type(self, job_title: str) -> str:
        """Map job title to job type"""
        if 'manager' in job_title.lower():
            return 'full_time'
        return 'full_time'
    
    def _determine_remote_type(self, location: str) -> str:
        """Determine remote type from location"""
        if location.lower() == 'remote':
            return 'remote'
        elif random.random() < 0.3:
            return 'hybrid'
        else:
            return 'onsite'
    
    def _determine_application_status(self, status_weights: Dict[str, float]) -> str:
        """Determine application status based on weights"""
        statuses = list(status_weights.keys())
        weights = list(status_weights.values())
        return random.choices(statuses, weights=weights)[0]
    
    def _generate_cover_letter(self) -> str:
        """Generate a sample cover letter"""
        templates = [
            "I am excited to apply for this position as it aligns perfectly with my career goals and technical expertise.",
            "With my background in software development and passion for innovation, I believe I would be a great fit for your team.",
            "I am particularly interested in this role because of the opportunity to work on cutting-edge technology.",
            "Having followed your company's growth, I am eager to contribute to your continued success."
        ]
        return random.choice(templates)
    
    def _generate_application_notes(self, status: str) -> str:
        """Generate application notes based on status"""
        notes_by_status = {
            'pending': 'Application submitted, waiting for response.',
            'rejected': 'Received rejection email. Good learning experience.',
            'interview': 'Scheduled for technical interview next week.',
            'offer': 'Received offer! Negotiating salary and start date.',
            'withdrawn': 'Decided to withdraw application due to better opportunity.'
        }
        return notes_by_status.get(status, 'Application in progress.')
    
    def _generate_saved_job_notes(self) -> str:
        """Generate notes for saved jobs"""
        notes = [
            'Interesting company culture, want to apply later.',
            'Good salary range, fits my skills well.',
            'Remote-friendly position, perfect for my situation.',
            'Growing company with good benefits.',
            'Will apply after completing current project.'
        ]
        return random.choice(notes)
    
    def _generate_activity_description(self, activity_type: str) -> str:
        """Generate activity description"""
        descriptions = {
            'job_view': 'Viewed job posting',
            'job_save': 'Saved job for later',
            'job_apply': 'Applied to job position',
            'profile_update': 'Updated profile information',
            'search': 'Performed job search'
        }
        return descriptions.get(activity_type, 'User activity')
    
    def _generate_activity_metadata(self, activity_type: str) -> Dict:
        """Generate activity metadata"""
        if activity_type == 'search':
            return {
                'search_query': random.choice(['python developer', 'react engineer', 'product manager', 'remote jobs']),
                'results_count': random.randint(5, 50)
            }
        return {}
    
    async def _count_activities(self, db: AsyncSession) -> int:
        """Count total activities created"""
        result = await db.execute("SELECT COUNT(*) FROM activity_logs")
        return result.scalar()


async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate sample data for JobQuest Navigator v2')
    parser.add_argument('--users', type=int, default=5, help='Number of users to create (default: 5)')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Preview what would be created without writing to database')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No data will be written to database")
        generator = SampleDataGenerator(args.config)
        print(f"📋 Would create data for {args.users} users based on configuration")
        print(f"📋 Configuration loaded from: {generator.config_path}")
        return
    
    try:
        generator = SampleDataGenerator(args.config)
        stats = await generator.populate_all_data(args.users)
        
        print("\n📊 Generation Summary:")
        print("=" * 40)
        for category, count in stats.items():
            print(f"  {category.capitalize()}: {count}")
        print("=" * 40)
        print("🎉 Sample data generation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during data generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())