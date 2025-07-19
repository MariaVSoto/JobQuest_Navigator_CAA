"""
Django management command to import 50 Toronto job listings into the database.
This command creates realistic job data for the Toronto area with proper companies and locations.

Usage:
    python manage.py import_toronto_jobs
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from jobs.models import Job, Category, Skill, JobSkill
from core.models import Company, Location
import uuid
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Import 50 realistic Toronto job listings into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing Toronto jobs before importing',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing Toronto jobs...')
            # Clear existing Toronto jobs
            toronto_locations = Location.objects.filter(city='Toronto')
            Job.objects.filter(location__in=toronto_locations).delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing Toronto jobs'))

        self.stdout.write('Creating Toronto location...')
        toronto_location = self.create_toronto_location()
        
        self.stdout.write('Creating categories...')
        categories = self.create_categories()
        
        self.stdout.write('Creating skills...')
        skills = self.create_skills()
        
        self.stdout.write('Creating companies...')
        companies = self.create_toronto_companies(toronto_location)
        
        self.stdout.write('Creating job listings...')
        jobs = self.create_toronto_jobs(companies, toronto_location, categories, skills)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported {len(jobs)} Toronto job listings!'
            )
        )

    def create_toronto_location(self):
        """Create or get Toronto location."""
        location, created = Location.objects.get_or_create(
            city='Toronto',
            state='Ontario',
            country='Canada',
            defaults={
                'latitude': Decimal('43.6532'),
                'longitude': Decimal('-79.3832'),
                'timezone': 'America/Toronto'
            }
        )
        if created:
            self.stdout.write(f'Created location: {location}')
        else:
            self.stdout.write(f'Using existing location: {location}')
        return location

    def create_categories(self):
        """Create job categories if they don't exist."""
        category_data = [
            ('Software Development', 'it-jobs'),
            ('Marketing', 'marketing-pr-jobs'),
            ('Sales', 'sales-jobs'),
            ('Finance', 'accounting-finance-jobs'),
            ('Design', 'creative-design-jobs'),
            ('Data Science', 'data-science-jobs'),
            ('Product Management', 'management-jobs'),
            ('Customer Success', 'customer-services-jobs'),
            ('Management', 'management-executive-jobs'),
        ]
        
        categories = {}
        for name, adzuna_tag in category_data:
            try:
                category, created = Category.objects.get_or_create(
                    name=name,
                    defaults={'adzuna_tag': adzuna_tag}
                )
                categories[name] = category
                if created:
                    self.stdout.write(f'Created category: {name}')
                else:
                    self.stdout.write(f'Using existing category: {name}')
            except Exception as e:
                # If there's a duplicate adzuna_tag, get the category by name only
                category, created = Category.objects.get_or_create(name=name)
                categories[name] = category
                self.stdout.write(f'Using existing category (resolved conflict): {name}')
        
        return categories

    def create_skills(self):
        """Create skills if they don't exist."""
        skill_data = [
            # Programming Languages
            ('Python', 'programming'), ('JavaScript', 'programming'), ('Java', 'programming'),
            ('TypeScript', 'programming'), ('C#', 'programming'), ('Go', 'programming'),
            ('SQL', 'programming'), ('PHP', 'programming'),
            
            # Frameworks & Libraries
            ('React', 'framework'), ('Vue.js', 'framework'), ('Angular', 'framework'),
            ('Django', 'framework'), ('Flask', 'framework'), ('Node.js', 'framework'),
            ('Express.js', 'framework'), ('.NET', 'framework'),
            
            # Databases
            ('PostgreSQL', 'database'), ('MySQL', 'database'), ('MongoDB', 'database'),
            ('Redis', 'database'),
            
            # Cloud & DevOps
            ('AWS', 'cloud'), ('Azure', 'cloud'), ('Docker', 'devops'),
            ('Kubernetes', 'devops'), ('Git', 'devops'),
            
            # Design & Marketing
            ('Figma', 'design'), ('Photoshop', 'design'), ('Google Analytics', 'other'),
            ('SEO', 'other'), ('Content Marketing', 'communication'),
            
            # Business Skills
            ('Project Management', 'management'), ('Agile', 'management'),
            ('Scrum', 'management'), ('Communication', 'communication'),
            
            # Additional Skills for comprehensive job coverage
            ('System Design', 'programming'), ('Microservices', 'framework'),
            ('Leadership', 'management'), ('Database Optimization', 'database'),
            ('Backup & Recovery', 'database'), ('Technical Writing', 'communication'),
            ('Documentation', 'communication'), ('API Documentation', 'communication'),
            ('User Guides', 'communication'), ('Azure', 'cloud'),
            ('Cloud Architecture', 'cloud'), ('Terraform', 'devops'),
            ('Consulting', 'communication'), ('Team Leadership', 'management'),
            ('Tableau', 'other'), ('Statistics', 'other'),
            ('Networking', 'other'), ('Cisco', 'other'),
            ('Network Security', 'other'), ('Troubleshooting', 'other'),
            ('Legal', 'other'), ('Technology Law', 'other'),
            ('Compliance', 'management'), ('Contract Negotiation', 'communication'),
            ('HR Management', 'management'), ('Employee Relations', 'management'),
            ('Performance Management', 'management'), ('Coaching', 'management'),
            ('Brand Design', 'design'), ('Adobe Creative Suite', 'design'),
            ('Typography', 'design'), ('Visual Identity', 'design'),
            ('CI/CD', 'devops'), ('Infrastructure as Code', 'devops'),
            ('Technical Sales', 'communication'), ('Solution Architecture', 'programming'),
            ('Presentation', 'communication'), ('Customer Relations', 'communication'),
            ('PPC', 'other'), ('Facebook Ads', 'other'),
            ('Google Ads', 'other'), ('Analytics', 'other'),
            ('ROI Optimization', 'other'), ('Risk Management', 'management'),
            ('Financial Regulations', 'other'), ('Audit', 'other'),
            ('Machine Learning', 'programming'), ('Deep Learning', 'programming'),
            ('Research', 'other'), ('Publications', 'other'),
            ('Engineering Leadership', 'management'), ('Technical Strategy', 'management'),
            ('Mentoring', 'management'), ('Power BI', 'other'),
            ('ETL', 'programming'), ('Data Warehousing', 'database'),
            ('Technical Support', 'other'), ('API Integration', 'programming'),
            ('Problem Solving', 'other'), ('Financial Analysis', 'other'),
            ('Cash Management', 'other'), ('Risk Assessment', 'other'),
            ('Excel', 'other'), ('User Research', 'other'),
            ('Usability Testing', 'other'), ('Survey Design', 'other'),
            ('Swift', 'programming'), ('iOS', 'programming'),
            ('Objective-C', 'programming'), ('Kotlin', 'programming'),
            ('Android', 'programming'), ('Test Automation', 'programming'),
            ('Selenium', 'framework'), ('API Testing', 'programming'),
            ('Monitoring', 'devops'), ('TensorFlow', 'framework'),
            ('Content Writing', 'communication'), ('Social Media', 'other'),
            ('Business Analysis', 'other'), ('Process Mapping', 'other'),
            ('Security', 'other'), ('Penetration Testing', 'other'),
            ('Cryptography', 'other'), ('Operations Management', 'management'),
            ('Process Improvement', 'management'), ('Partnership Development', 'communication'),
            ('Negotiation', 'communication'), ('CRM', 'other'),
            ('Lead Generation', 'other'), ('Financial Modeling', 'other'),
            ('Customer Success', 'communication'), ('Customer Service', 'communication'),
            ('Technical Troubleshooting', 'other'),
        ]
        
        skills = {}
        for name, category in skill_data:
            skill, created = Skill.objects.get_or_create(
                name=name,
                defaults={
                    'slug': name.lower().replace(' ', '-').replace('.', '').replace('#', 'sharp'),
                    'category': category,
                    'is_technical': category in ['programming', 'framework', 'database', 'cloud', 'devops'],
                    'popularity_score': random.randint(50, 100)
                }
            )
            skills[name] = skill
            if created:
                self.stdout.write(f'Created skill: {name}')
        
        return skills

    def create_toronto_companies(self, toronto_location):
        """Create Toronto-based companies."""
        company_data = [
            # Tech Companies
            {
                'name': 'Shopify',
                'industry': 'E-commerce',
                'company_size': 'enterprise',
                'description': 'Leading e-commerce platform helping businesses sell online',
                'website': 'https://shopify.com',
            },
            {
                'name': 'Wealthsimple',
                'industry': 'FinTech',
                'company_size': 'large',
                'description': 'Modern investing and financial planning platform',
                'website': 'https://wealthsimple.com',
            },
            {
                'name': 'Ritual',
                'industry': 'Food Tech',
                'company_size': 'medium',
                'description': 'Food ordering and team lunch platform',
                'website': 'https://ritual.co',
            },
            {
                'name': 'Top Hat',
                'industry': 'EdTech',
                'company_size': 'medium',
                'description': 'Educational technology platform for higher education',
                'website': 'https://tophat.com',
            },
            {
                'name': 'Paymi',
                'industry': 'FinTech',
                'company_size': 'small',
                'description': 'Digital payment solutions for businesses',
                'website': 'https://paymi.com',
            },
            # Traditional Companies with Tech Teams
            {
                'name': 'Royal Bank of Canada',
                'industry': 'Banking',
                'company_size': 'enterprise',
                'description': 'One of Canada\'s largest banks with growing tech division',
                'website': 'https://rbc.com',
            },
            {
                'name': 'Scotiabank',
                'industry': 'Banking',
                'company_size': 'enterprise',
                'description': 'Major Canadian bank investing heavily in digital transformation',
                'website': 'https://scotiabank.com',
            },
            {
                'name': 'Rogers Communications',
                'industry': 'Telecommunications',
                'company_size': 'enterprise',
                'description': 'Leading telecommunications and media company',
                'website': 'https://rogers.com',
            },
            # Consulting & Agencies
            {
                'name': 'Accenture Toronto',
                'industry': 'Consulting',
                'company_size': 'enterprise',
                'description': 'Global consulting firm with major Toronto operations',
                'website': 'https://accenture.com',
            },
            {
                'name': 'Deloitte Digital',
                'industry': 'Consulting',
                'company_size': 'enterprise',
                'description': 'Digital transformation consulting and development',
                'website': 'https://deloitte.com',
            },
            # Startups & Scale-ups
            {
                'name': 'Coinsquare',
                'industry': 'Cryptocurrency',
                'company_size': 'medium',
                'description': 'Canadian cryptocurrency trading platform',
                'website': 'https://coinsquare.com',
            },
            {
                'name': 'Freshbooks',
                'industry': 'SaaS',
                'company_size': 'large',
                'description': 'Cloud-based accounting software for small businesses',
                'website': 'https://freshbooks.com',
            },
            {
                'name': 'Symend',
                'industry': 'AI/SaaS',
                'company_size': 'medium',
                'description': 'AI-powered customer engagement platform',
                'website': 'https://symend.com',
            },
            {
                'name': 'TouchBistro',
                'industry': 'Restaurant Tech',
                'company_size': 'medium',
                'description': 'Point-of-sale system for restaurants',
                'website': 'https://touchbistro.com',
            },
            {
                'name': 'Wave Financial',
                'industry': 'FinTech',
                'company_size': 'medium',
                'description': 'Free accounting software for small businesses',
                'website': 'https://waveapps.com',
            },
        ]
        
        companies = []
        for company_info in company_data:
            company, created = Company.objects.get_or_create(
                name=company_info['name'],
                defaults={
                    'slug': company_info['name'].lower().replace(' ', '-').replace('.', ''),
                    'industry': company_info['industry'],
                    'company_size': company_info['company_size'],
                    'description': company_info['description'],
                    'website': company_info['website'],
                    'headquarters': toronto_location,
                }
            )
            if created:
                company.locations.add(toronto_location)
                self.stdout.write(f'Created company: {company.name}')
            companies.append(company)
        
        return companies

    def create_toronto_jobs(self, companies, toronto_location, categories, skills):
        """Create 50 diverse job listings in Toronto."""
        job_data = [
            # Senior Software Engineer roles
            {
                'title': 'Senior Full Stack Developer',
                'company': 'Shopify',
                'category': 'Software Development',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 120000,
                'salary_max': 160000,
                'required_skills': ['JavaScript', 'React', 'Node.js', 'PostgreSQL', 'AWS'],
                'description': 'Join our platform team to build scalable e-commerce solutions used by millions of merchants worldwide. You\'ll work on high-impact features that directly influence merchant success.',
                'requirements': 'Bachelor\'s degree in Computer Science or equivalent experience. 5+ years of full-stack development experience with modern JavaScript frameworks.',
            },
            {
                'title': 'Senior Python Developer',
                'company': 'Wealthsimple',
                'category': 'Software Development',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 115000,
                'salary_max': 150000,
                'required_skills': ['Python', 'Django', 'PostgreSQL', 'AWS', 'Docker'],
                'description': 'Build and maintain the backend systems that power our investment platform. Work on portfolio management, trading systems, and regulatory compliance features.',
                'requirements': '4+ years of Python development experience. Experience with financial systems preferred. Strong understanding of API design and database optimization.',
            },
            {
                'title': 'Frontend Engineer - React',
                'company': 'Top Hat',
                'category': 'Software Development',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 85000,
                'salary_max': 110000,
                'required_skills': ['React', 'TypeScript', 'JavaScript', 'Git'],
                'description': 'Create engaging user interfaces for our educational platform used by students and professors worldwide. Focus on accessibility and performance.',
                'requirements': '3+ years of React development experience. TypeScript experience preferred. Passion for education technology.',
            },
            
            # Backend/Infrastructure roles
            {
                'title': 'DevOps Engineer',
                'company': 'Ritual',
                'category': 'Software Development',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 95000,
                'salary_max': 125000,
                'required_skills': ['AWS', 'Docker', 'Kubernetes', 'Python', 'Git'],
                'description': 'Manage and scale our cloud infrastructure to support millions of food orders. Implement CI/CD pipelines and monitoring solutions.',
                'requirements': '3+ years of DevOps experience. Strong AWS and container orchestration skills. Experience with monitoring and alerting systems.',
            },
            {
                'title': 'Backend Engineer - Go',
                'company': 'Coinsquare',
                'category': 'Software Development',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'on_site',
                'salary_min': 100000,
                'salary_max': 130000,
                'required_skills': ['Go', 'PostgreSQL', 'Redis', 'Docker', 'Git'],
                'description': 'Build high-performance trading systems and APIs for cryptocurrency exchange. Focus on security, scalability, and low latency.',
                'requirements': '3+ years of backend development experience. Go programming experience required. Knowledge of cryptocurrency markets is a plus.',
            },
            
            # Data Science & Analytics
            {
                'title': 'Data Scientist',
                'company': 'Royal Bank of Canada',
                'category': 'Data Science',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 95000,
                'salary_max': 120000,
                'required_skills': ['Python', 'SQL', 'Machine Learning', 'AWS'],
                'description': 'Apply machine learning to improve customer experience and risk management. Work with large datasets to derive actionable insights.',
                'requirements': 'Master\'s degree in Data Science, Statistics, or related field. 3+ years of data science experience. Strong Python and SQL skills.',
            },
            {
                'title': 'Senior Data Engineer',
                'company': 'Freshbooks',
                'category': 'Data Science',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 110000,
                'salary_max': 140000,
                'required_skills': ['Python', 'SQL', 'AWS', 'Docker', 'Kubernetes'],
                'description': 'Design and build data pipelines that power our analytics and machine learning platforms. Work with terabytes of financial data.',
                'requirements': '5+ years of data engineering experience. Strong experience with cloud data platforms and ETL processes.',
            },
            
            # Product & Design
            {
                'title': 'Senior Product Designer',
                'company': 'TouchBistro',
                'category': 'Design',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 85000,
                'salary_max': 110000,
                'required_skills': ['Figma', 'User Research', 'Prototyping'],
                'description': 'Lead design for our restaurant POS system used by thousands of restaurants. Focus on creating intuitive interfaces for fast-paced environments.',
                'requirements': '5+ years of product design experience. Experience with B2B software design. Strong portfolio showcasing UX/UI design skills.',
            },
            {
                'title': 'UX Designer',
                'company': 'Wave Financial',
                'category': 'Design',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 70000,
                'salary_max': 90000,
                'required_skills': ['Figma', 'User Research', 'Prototyping'],
                'description': 'Design user experiences for our accounting software used by small business owners. Simplify complex financial workflows.',
                'requirements': '3+ years of UX design experience. Experience with financial or accounting software preferred.',
            },
            
            # Product Management
            {
                'title': 'Senior Product Manager',
                'company': 'Symend',
                'category': 'Product Management',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 120000,
                'salary_max': 150000,
                'required_skills': ['Product Strategy', 'Analytics', 'Agile', 'Communication'],
                'description': 'Drive product strategy for our AI-powered customer engagement platform. Work closely with engineering and data science teams.',
                'requirements': '5+ years of product management experience. Experience with AI/ML products preferred. Strong analytical and communication skills.',
            },
            {
                'title': 'Product Manager - Growth',
                'company': 'Paymi',
                'category': 'Product Management',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 95000,
                'salary_max': 120000,
                'required_skills': ['Product Strategy', 'Analytics', 'A/B Testing', 'SQL'],
                'description': 'Lead growth initiatives for our digital payment platform. Use data to identify opportunities and drive user acquisition.',
                'requirements': '3+ years of product management experience. Strong analytical skills and experience with growth metrics.',
            },
            
            # Marketing & Sales
            {
                'title': 'Digital Marketing Manager',
                'company': 'Freshbooks',
                'category': 'Marketing',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 70000,
                'salary_max': 90000,
                'required_skills': ['Google Analytics', 'SEO', 'Content Marketing', 'PPC'],
                'description': 'Lead digital marketing campaigns to drive customer acquisition for our accounting software. Manage SEO, PPC, and content strategies.',
                'requirements': '3+ years of digital marketing experience. Strong understanding of SaaS marketing metrics and funnel optimization.',
            },
            {
                'title': 'Sales Development Representative',
                'company': 'Accenture Toronto',
                'category': 'Sales',
                'experience_level': 'entry',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 50000,
                'salary_max': 65000,
                'required_skills': ['Communication', 'CRM', 'Lead Generation'],
                'description': 'Generate qualified leads for our consulting services. Work with enterprise clients to identify technology transformation opportunities.',
                'requirements': 'Bachelor\'s degree preferred. 1-2 years of sales experience. Strong communication and interpersonal skills.',
            },
            
            # Finance & Analytics
            {
                'title': 'Financial Analyst',
                'company': 'Scotiabank',
                'category': 'Finance',
                'experience_level': 'entry',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 60000,
                'salary_max': 75000,
                'required_skills': ['Excel', 'SQL', 'Financial Modeling', 'Communication'],
                'description': 'Support financial planning and analysis for our digital banking initiatives. Create models and reports for executive decision-making.',
                'requirements': 'Bachelor\'s degree in Finance, Economics, or related field. Strong Excel and analytical skills. CFA designation preferred.',
            },
            {
                'title': 'Senior Financial Analyst',
                'company': 'Rogers Communications',
                'category': 'Finance',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'on_site',
                'salary_min': 85000,
                'salary_max': 105000,
                'required_skills': ['Excel', 'SQL', 'Financial Modeling', 'Project Management'],
                'description': 'Lead financial analysis for major technology investments and business transformation initiatives.',
                'requirements': '5+ years of financial analysis experience. Experience in telecommunications or technology sectors preferred.',
            },
            
            # Junior/Entry Level Positions
            {
                'title': 'Junior Software Developer',
                'company': 'Deloitte Digital',
                'category': 'Software Development',
                'experience_level': 'junior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 65000,
                'salary_max': 80000,
                'required_skills': ['JavaScript', 'React', 'Java', 'Git'],
                'description': 'Join our development team working on digital transformation projects for enterprise clients. Great opportunity for career growth.',
                'requirements': 'Bachelor\'s degree in Computer Science or related field. 1-2 years of development experience or strong internship background.',
            },
            {
                'title': 'Frontend Developer Intern',
                'company': 'Ritual',
                'category': 'Software Development',
                'experience_level': 'entry',
                'job_type': 'internship',
                'remote_type': 'hybrid',
                'salary_min': 45000,
                'salary_max': 55000,
                'required_skills': ['React', 'JavaScript', 'HTML/CSS', 'Git'],
                'description': 'Summer internship working on our mobile-first food ordering platform. Mentorship from senior developers included.',
                'requirements': 'Currently pursuing degree in Computer Science or related field. Portfolio of web development projects required.',
            },
            
            # Customer Success & Support
            {
                'title': 'Customer Success Manager',
                'company': 'Top Hat',
                'category': 'Customer Success',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 65000,
                'salary_max': 80000,
                'required_skills': ['Communication', 'CRM', 'Customer Success', 'Analytics'],
                'description': 'Help educational institutions maximize value from our platform. Build relationships with professors and administrators.',
                'requirements': '3+ years of customer success experience. Experience in education technology preferred. Strong communication skills.',
            },
            {
                'title': 'Technical Support Specialist',
                'company': 'TouchBistro',
                'category': 'Customer Success',
                'experience_level': 'entry',
                'job_type': 'full_time',
                'remote_type': 'on_site',
                'salary_min': 45000,
                'salary_max': 55000,
                'required_skills': ['Communication', 'Technical Troubleshooting', 'Customer Service'],
                'description': 'Provide technical support to restaurant owners using our POS system. Help resolve issues and provide training.',
                'requirements': '1-2 years of technical support experience. Strong problem-solving skills and patience with customers.',
            },
            
            # Additional Tech Roles
            {
                'title': 'Mobile Developer - iOS',
                'company': 'Wealthsimple',
                'category': 'Software Development',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 100000,
                'salary_max': 125000,
                'required_skills': ['Swift', 'iOS', 'Objective-C', 'Git'],
                'description': 'Build and maintain our iOS app used by hundreds of thousands of investors. Focus on performance and user experience.',
                'requirements': '3+ years of iOS development experience. Published apps in the App Store. Experience with financial apps preferred.',
            },
            {
                'title': 'Android Developer',
                'company': 'Paymi',
                'category': 'Software Development',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 95000,
                'salary_max': 120000,
                'required_skills': ['Kotlin', 'Android', 'Java', 'Git'],
                'description': 'Develop our Android payment app with focus on security and user experience. Work with payment processing and encryption.',
                'requirements': '3+ years of Android development experience. Knowledge of payment processing and security best practices.',
            },
            {
                'title': 'QA Engineer',
                'company': 'Symend',
                'category': 'Software Development',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 75000,
                'salary_max': 95000,
                'required_skills': ['Test Automation', 'Python', 'Selenium', 'API Testing'],
                'description': 'Design and implement automated testing for our AI platform. Ensure quality across web applications and APIs.',
                'requirements': '3+ years of QA engineering experience. Strong automation skills and attention to detail.',
            },
            {
                'title': 'Site Reliability Engineer',
                'company': 'Coinsquare',
                'category': 'Software Development',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'on_site',
                'salary_min': 110000,
                'salary_max': 140000,
                'required_skills': ['AWS', 'Kubernetes', 'Python', 'Monitoring', 'Git'],
                'description': 'Ensure high availability and performance of our cryptocurrency trading platform. Design and implement monitoring and alerting.',
                'requirements': '4+ years of SRE experience. Strong knowledge of distributed systems and high-availability architectures.',
            },
            {
                'title': 'Machine Learning Engineer',
                'company': 'Royal Bank of Canada',
                'category': 'Data Science',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 120000,
                'salary_max': 150000,
                'required_skills': ['Python', 'TensorFlow', 'AWS', 'Machine Learning', 'SQL'],
                'description': 'Build and deploy machine learning models for fraud detection and risk assessment. Work with large-scale financial datasets.',
                'requirements': '4+ years of ML engineering experience. Strong background in statistics and machine learning algorithms.',
            },
            {
                'title': 'Content Marketing Specialist',
                'company': 'Wave Financial',
                'category': 'Marketing',
                'experience_level': 'entry',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 50000,
                'salary_max': 65000,
                'required_skills': ['Content Writing', 'SEO', 'Social Media', 'Analytics'],
                'description': 'Create educational content for small business owners about accounting and finance. Manage blog and social media presence.',
                'requirements': '1-2 years of content marketing experience. Strong writing skills and understanding of small business challenges.',
            },
            {
                'title': 'Business Analyst',
                'company': 'Accenture Toronto',
                'category': 'Product Management',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 75000,
                'salary_max': 95000,
                'required_skills': ['Business Analysis', 'SQL', 'Excel', 'Process Mapping'],
                'description': 'Analyze business requirements and design solutions for digital transformation projects. Work with enterprise clients.',
                'requirements': '3+ years of business analysis experience. Strong analytical and communication skills. Consulting experience preferred.',
            },
            {
                'title': 'Security Engineer',
                'company': 'Shopify',
                'category': 'Software Development',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 125000,
                'salary_max': 160000,
                'required_skills': ['Security', 'Python', 'AWS', 'Penetration Testing', 'Cryptography'],
                'description': 'Protect our platform and merchants from security threats. Design and implement security controls and monitoring.',
                'requirements': '5+ years of security engineering experience. Security certifications (CISSP, CEH) preferred.',
            },
            {
                'title': 'Operations Manager',
                'company': 'Freshbooks',
                'category': 'Management',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'on_site',
                'salary_min': 90000,
                'salary_max': 115000,
                'required_skills': ['Operations Management', 'Process Improvement', 'Analytics', 'Leadership'],
                'description': 'Lead operational initiatives to improve efficiency and customer satisfaction. Manage cross-functional improvement projects.',
                'requirements': '5+ years of operations management experience. Experience in SaaS or technology companies preferred.',
            },
            {
                'title': 'Partnership Manager',
                'company': 'Ritual',
                'category': 'Sales',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 80000,
                'salary_max': 100000,
                'required_skills': ['Partnership Development', 'Negotiation', 'Communication', 'CRM'],
                'description': 'Develop and manage partnerships with restaurants and corporate clients. Drive business development initiatives.',
                'requirements': '3+ years of partnership or business development experience. Experience in food tech or marketplace businesses preferred.',
            },
            # Additional 20 jobs to reach 50 total
            {
                'title': 'Senior Software Architect',
                'company': 'Shopify',
                'category': 'Software Development',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 140000,
                'salary_max': 180000,
                'required_skills': ['System Design', 'Microservices', 'AWS', 'Kubernetes', 'Leadership'],
                'description': 'Lead architectural decisions for our platform serving millions of merchants. Design scalable, resilient systems.',
                'requirements': '8+ years of software architecture experience. Strong background in distributed systems and microservices.',
            },
            {
                'title': 'Database Administrator',
                'company': 'Royal Bank of Canada',
                'category': 'Software Development',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'on_site',
                'salary_min': 85000,
                'salary_max': 110000,
                'required_skills': ['PostgreSQL', 'MySQL', 'Database Optimization', 'Backup & Recovery'],
                'description': 'Manage and optimize database systems supporting our banking applications. Ensure high availability and performance.',
                'requirements': '4+ years of database administration experience. Experience with high-volume financial systems.',
            },
            {
                'title': 'Technical Writer',
                'company': 'Top Hat',
                'category': 'Design',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 65000,
                'salary_max': 80000,
                'required_skills': ['Technical Writing', 'Documentation', 'API Documentation', 'User Guides'],
                'description': 'Create comprehensive documentation for our educational platform. Write API docs, user guides, and developer resources.',
                'requirements': '3+ years of technical writing experience. Experience with educational technology preferred.',
            },
            {
                'title': 'Cloud Solutions Architect',
                'company': 'Accenture Toronto',
                'category': 'Software Development',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 120000,
                'salary_max': 150000,
                'required_skills': ['AWS', 'Azure', 'Cloud Architecture', 'Terraform', 'Consulting'],
                'description': 'Design cloud solutions for enterprise clients. Lead cloud migration and transformation projects.',
                'requirements': '6+ years of cloud architecture experience. AWS/Azure certifications required. Consulting experience preferred.',
            },
            {
                'title': 'Scrum Master',
                'company': 'Wealthsimple',
                'category': 'Product Management',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 85000,
                'salary_max': 105000,
                'required_skills': ['Scrum', 'Agile', 'Project Management', 'Team Leadership'],
                'description': 'Facilitate agile development processes for our engineering teams. Coach teams on agile best practices.',
                'requirements': '3+ years of Scrum Master experience. Certified Scrum Master (CSM) preferred. FinTech experience a plus.',
            },
            {
                'title': 'Data Analyst',
                'company': 'TouchBistro',
                'category': 'Data Science',
                'experience_level': 'entry',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 55000,
                'salary_max': 70000,
                'required_skills': ['SQL', 'Excel', 'Tableau', 'Python', 'Statistics'],
                'description': 'Analyze restaurant operations data to provide insights for product development and customer success.',
                'requirements': '1-2 years of data analysis experience. Strong SQL and visualization skills. Restaurant industry knowledge helpful.',
            },
            {
                'title': 'Network Engineer',
                'company': 'Rogers Communications',
                'category': 'Software Development',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'on_site',
                'salary_min': 80000,
                'salary_max': 100000,
                'required_skills': ['Networking', 'Cisco', 'Network Security', 'Troubleshooting'],
                'description': 'Design and maintain network infrastructure supporting our telecommunications services.',
                'requirements': '4+ years of network engineering experience. Cisco certifications preferred. Telecom experience required.',
            },
            {
                'title': 'Legal Counsel - Technology',
                'company': 'Coinsquare',
                'category': 'Management',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'on_site',
                'salary_min': 130000,
                'salary_max': 160000,
                'required_skills': ['Legal', 'Technology Law', 'Compliance', 'Contract Negotiation'],
                'description': 'Provide legal guidance on cryptocurrency regulations and technology compliance matters.',
                'requirements': 'Law degree and 5+ years of technology law experience. Cryptocurrency/blockchain knowledge required.',
            },
            {
                'title': 'HR Business Partner',
                'company': 'Freshbooks',
                'category': 'Management',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 75000,
                'salary_max': 95000,
                'required_skills': ['HR Management', 'Employee Relations', 'Performance Management', 'Coaching'],
                'description': 'Partner with leadership teams to drive HR strategy and support employee development.',
                'requirements': '4+ years of HR business partner experience. Experience in fast-growing SaaS companies preferred.',
            },
            {
                'title': 'Brand Designer',
                'company': 'Ritual',
                'category': 'Design',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 70000,
                'salary_max': 90000,
                'required_skills': ['Brand Design', 'Adobe Creative Suite', 'Typography', 'Visual Identity'],
                'description': 'Develop and maintain brand identity across all touchpoints. Create marketing materials and brand guidelines.',
                'requirements': '3+ years of brand design experience. Strong portfolio showcasing brand identity work.',
            },
            {
                'title': 'Platform Engineer',
                'company': 'Symend',
                'category': 'Software Development',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 115000,
                'salary_max': 145000,
                'required_skills': ['Kubernetes', 'Docker', 'AWS', 'CI/CD', 'Infrastructure as Code'],
                'description': 'Build and maintain platform infrastructure that enables rapid application development and deployment.',
                'requirements': '5+ years of platform engineering experience. Strong background in container orchestration and cloud platforms.',
            },
            {
                'title': 'Sales Engineer',
                'company': 'Deloitte Digital',
                'category': 'Sales',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 90000,
                'salary_max': 115000,
                'required_skills': ['Technical Sales', 'Solution Architecture', 'Presentation', 'Customer Relations'],
                'description': 'Support sales process by providing technical expertise and solution design for enterprise clients.',
                'requirements': '3+ years of technical sales or solution architecture experience. Strong presentation and communication skills.',
            },
            {
                'title': 'Performance Marketing Manager',
                'company': 'Paymi',
                'category': 'Marketing',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 80000,
                'salary_max': 100000,
                'required_skills': ['PPC', 'Facebook Ads', 'Google Ads', 'Analytics', 'ROI Optimization'],
                'description': 'Manage paid advertising campaigns across digital channels. Optimize for customer acquisition and ROI.',
                'requirements': '4+ years of performance marketing experience. Strong analytical skills and experience with FinTech products.',
            },
            {
                'title': 'Compliance Officer',
                'company': 'Wave Financial',
                'category': 'Finance',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 80000,
                'salary_max': 100000,
                'required_skills': ['Compliance', 'Risk Management', 'Financial Regulations', 'Audit'],
                'description': 'Ensure compliance with financial regulations and maintain risk management frameworks.',
                'requirements': '4+ years of compliance experience in financial services. Knowledge of Canadian financial regulations required.',
            },
            {
                'title': 'Research Scientist - AI',
                'company': 'Royal Bank of Canada',
                'category': 'Data Science',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 130000,
                'salary_max': 170000,
                'required_skills': ['Machine Learning', 'Deep Learning', 'Python', 'Research', 'Publications'],
                'description': 'Conduct cutting-edge AI research for financial applications. Publish research and implement production systems.',
                'requirements': 'PhD in Computer Science, AI, or related field. 3+ years of AI research experience. Published papers preferred.',
            },
            {
                'title': 'Engineering Manager',
                'company': 'Shopify',
                'category': 'Management',
                'experience_level': 'senior',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 150000,
                'salary_max': 190000,
                'required_skills': ['Engineering Leadership', 'Team Management', 'Technical Strategy', 'Mentoring'],
                'description': 'Lead a team of senior engineers building core platform capabilities. Drive technical strategy and team growth.',
                'requirements': '6+ years of engineering experience with 3+ years in leadership roles. Experience scaling engineering teams.',
            },
            {
                'title': 'Business Intelligence Developer',
                'company': 'Scotiabank',
                'category': 'Data Science',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 85000,
                'salary_max': 105000,
                'required_skills': ['SQL', 'Tableau', 'Power BI', 'ETL', 'Data Warehousing'],
                'description': 'Develop business intelligence solutions and dashboards for banking operations and customer analytics.',
                'requirements': '3+ years of BI development experience. Strong SQL skills and experience with enterprise BI tools.',
            },
            {
                'title': 'Customer Success Engineer',
                'company': 'Top Hat',
                'category': 'Customer Success',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'remote',
                'salary_min': 75000,
                'salary_max': 95000,
                'required_skills': ['Technical Support', 'API Integration', 'Customer Success', 'Problem Solving'],
                'description': 'Help educational institutions integrate and optimize their use of our platform. Provide technical guidance.',
                'requirements': '3+ years of technical customer success experience. Background in education technology preferred.',
            },
            {
                'title': 'Treasury Analyst',
                'company': 'Wealthsimple',
                'category': 'Finance',
                'experience_level': 'entry',
                'job_type': 'full_time',
                'remote_type': 'on_site',
                'salary_min': 65000,
                'salary_max': 80000,
                'required_skills': ['Financial Analysis', 'Cash Management', 'Risk Assessment', 'Excel'],
                'description': 'Support treasury operations including cash management, liquidity planning, and financial risk assessment.',
                'requirements': 'Bachelor\'s degree in Finance or related field. 1-2 years of treasury or financial analysis experience.',
            },
            {
                'title': 'UX Researcher',
                'company': 'TouchBistro',
                'category': 'Design',
                'experience_level': 'mid',
                'job_type': 'full_time',
                'remote_type': 'hybrid',
                'salary_min': 80000,
                'salary_max': 100000,
                'required_skills': ['User Research', 'Usability Testing', 'Data Analysis', 'Survey Design'],
                'description': 'Conduct user research to inform product decisions for our restaurant POS system. Plan and execute usability studies.',
                'requirements': '3+ years of UX research experience. Experience with B2B software research preferred.',
            },
        ]
        
        jobs = []
        for i, job_info in enumerate(job_data[:50]):  # Ensure exactly 50 jobs
            # Find company
            company = next((c for c in companies if c.name == job_info['company']), companies[0])
            
            # Create job
            job = Job.objects.create(
                title=job_info['title'],
                company=company,
                location=toronto_location,
                category=categories.get(job_info['category']),
                description=job_info['description'],
                requirements=job_info['requirements'],
                salary_min=job_info['salary_min'],
                salary_max=job_info['salary_max'],
                salary_currency='CAD',
                salary_period='yearly',
                job_type=job_info['job_type'],
                experience_level=job_info['experience_level'],
                remote_type=job_info['remote_type'],
                source='manual',
                is_active=True,
                posted_date=timezone.now() - timedelta(days=random.randint(1, 30)),
            )
            
            # Add required skills
            for skill_name in job_info.get('required_skills', []):
                if skill_name in skills:
                    JobSkill.objects.create(
                        job=job,
                        skill=skills[skill_name],
                        is_required=True,
                        proficiency_level=random.choice(['intermediate', 'advanced'])
                    )
            
            jobs.append(job)
            self.stdout.write(f'Created job: {job.title} at {job.company.name}')
        
        return jobs