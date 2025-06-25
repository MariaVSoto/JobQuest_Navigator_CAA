"""
Management command to populate initial skills and certifications data.
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from skills.models import (
    SkillCategory, Skill, Certification, LearningPath
)


class Command(BaseCommand):
    help = 'Populate initial skills and certifications data for demo purposes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate skills data...'))
        
        # Create skill categories
        self.create_skill_categories()
        
        # Create skills
        self.create_skills()
        
        # Create certifications
        self.create_certifications()
        
        # Create learning paths
        self.create_learning_paths()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated skills data!'))

    def create_skill_categories(self):
        """Create skill categories."""
        categories = [
            {
                'name': 'Programming Languages',
                'description': 'Software programming and scripting languages',
                'icon': 'code',
                'color': '#007bff'
            },
            {
                'name': 'Web Development',
                'description': 'Frontend and backend web development technologies',
                'icon': 'globe',
                'color': '#28a745'
            },
            {
                'name': 'Data Science',
                'description': 'Data analysis, machine learning, and analytics',
                'icon': 'chart-bar',
                'color': '#6f42c1'
            },
            {
                'name': 'Cloud Computing',
                'description': 'Cloud platforms and services',
                'icon': 'cloud',
                'color': '#17a2b8'
            },
            {
                'name': 'DevOps',
                'description': 'Development operations and automation',
                'icon': 'tools',
                'color': '#fd7e14'
            },
            {
                'name': 'Mobile Development',
                'description': 'iOS and Android app development',
                'icon': 'mobile-alt',
                'color': '#e83e8c'
            },
            {
                'name': 'Database',
                'description': 'Database management and design',
                'icon': 'database',
                'color': '#6c757d'
            },
            {
                'name': 'Soft Skills',
                'description': 'Communication and interpersonal skills',
                'icon': 'users',
                'color': '#ffc107'
            }
        ]
        
        for cat_data in categories:
            category, created = SkillCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'color': cat_data['color']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

    def create_skills(self):
        """Create skills."""
        skills_data = [
            # Programming Languages
            {
                'name': 'Python',
                'category': 'Programming Languages',
                'description': 'High-level programming language for web development, data science, and automation',
                'aliases': ['Python3', 'Python 3'],
                'market_demand': 'very_high',
                'average_salary': 95000,
                'growth_rate': 15.5,
                'learning_time_hours': 200,
                'difficulty_level': 'intermediate',
                'is_trending': True,
                'popularity_score': 95.0
            },
            {
                'name': 'JavaScript',
                'category': 'Programming Languages',
                'description': 'Dynamic programming language for web development',
                'aliases': ['JS', 'ECMAScript'],
                'market_demand': 'very_high',
                'average_salary': 85000,
                'growth_rate': 12.3,
                'learning_time_hours': 150,
                'difficulty_level': 'intermediate',
                'is_trending': True,
                'popularity_score': 92.0
            },
            {
                'name': 'Java',
                'category': 'Programming Languages',
                'description': 'Object-oriented programming language for enterprise applications',
                'aliases': ['Java SE', 'Java EE'],
                'market_demand': 'high',
                'average_salary': 88000,
                'growth_rate': 8.2,
                'learning_time_hours': 250,
                'difficulty_level': 'intermediate',
                'is_trending': False,
                'popularity_score': 85.0
            },
            
            # Web Development
            {
                'name': 'React',
                'category': 'Web Development',
                'description': 'JavaScript library for building user interfaces',
                'aliases': ['ReactJS', 'React.js'],
                'market_demand': 'very_high',
                'average_salary': 92000,
                'growth_rate': 18.7,
                'learning_time_hours': 120,
                'difficulty_level': 'intermediate',
                'is_trending': True,
                'popularity_score': 89.0
            },
            {
                'name': 'Node.js',
                'category': 'Web Development',
                'description': 'JavaScript runtime for server-side development',
                'aliases': ['NodeJS', 'Node'],
                'market_demand': 'high',
                'average_salary': 87000,
                'growth_rate': 14.2,
                'learning_time_hours': 100,
                'difficulty_level': 'intermediate',
                'is_trending': True,
                'popularity_score': 82.0
            },
            {
                'name': 'Django',
                'category': 'Web Development',
                'description': 'High-level Python web framework',
                'aliases': ['Django Framework'],
                'market_demand': 'high',
                'average_salary': 91000,
                'growth_rate': 11.5,
                'learning_time_hours': 80,
                'difficulty_level': 'intermediate',
                'is_trending': False,
                'popularity_score': 75.0
            },
            
            # Data Science
            {
                'name': 'Machine Learning',
                'category': 'Data Science',
                'description': 'Algorithms and statistical models for data analysis',
                'aliases': ['ML', 'AI'],
                'market_demand': 'very_high',
                'average_salary': 115000,
                'growth_rate': 22.1,
                'learning_time_hours': 300,
                'difficulty_level': 'advanced',
                'is_trending': True,
                'popularity_score': 94.0
            },
            {
                'name': 'SQL',
                'category': 'Database',
                'description': 'Structured Query Language for database management',
                'aliases': ['MySQL', 'PostgreSQL'],
                'market_demand': 'very_high',
                'average_salary': 78000,
                'growth_rate': 9.8,
                'learning_time_hours': 60,
                'difficulty_level': 'beginner',
                'is_trending': False,
                'popularity_score': 91.0
            },
            
            # Cloud Computing
            {
                'name': 'AWS',
                'category': 'Cloud Computing',
                'description': 'Amazon Web Services cloud platform',
                'aliases': ['Amazon Web Services'],
                'market_demand': 'very_high',
                'average_salary': 105000,
                'growth_rate': 19.3,
                'learning_time_hours': 180,
                'difficulty_level': 'intermediate',
                'is_trending': True,
                'popularity_score': 88.0
            },
            
            # Soft Skills
            {
                'name': 'Project Management',
                'category': 'Soft Skills',
                'description': 'Planning and managing project timelines and resources',
                'aliases': ['PM', 'Project Planning'],
                'market_demand': 'high',
                'average_salary': 85000,
                'growth_rate': 7.5,
                'learning_time_hours': 100,
                'difficulty_level': 'intermediate',
                'is_trending': False,
                'popularity_score': 79.0,
                'is_technical': False
            }
        ]
        
        for skill_data in skills_data:
            category = SkillCategory.objects.get(name=skill_data['category'])
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults={
                    'slug': slugify(skill_data['name']),
                    'category': category,
                    'description': skill_data['description'],
                    'aliases': skill_data['aliases'],
                    'market_demand': skill_data['market_demand'],
                    'average_salary': skill_data['average_salary'],
                    'growth_rate': skill_data['growth_rate'],
                    'learning_time_hours': skill_data['learning_time_hours'],
                    'difficulty_level': skill_data['difficulty_level'],
                    'is_trending': skill_data['is_trending'],
                    'is_technical': skill_data.get('is_technical', True),
                    'popularity_score': skill_data['popularity_score']
                }
            )
            if created:
                self.stdout.write(f'Created skill: {skill.name}')

    def create_certifications(self):
        """Create certifications."""
        certifications = [
            {
                'name': 'AWS Certified Solutions Architect',
                'issuing_organization': 'Amazon Web Services',
                'description': 'Validates expertise in designing distributed systems on AWS',
                'difficulty_level': 'advanced',
                'is_lifetime': False,
                'validity_years': 3,
                'cost_usd': 150.00,
                'preparation_time_hours': 120,
                'pass_rate': 72.0,
                'salary_boost_percentage': 15.0,
                'market_demand': 'very_high',
                'official_url': 'https://aws.amazon.com/certification/',
                'popularity_score': 90.0
            },
            {
                'name': 'Certified Kubernetes Administrator (CKA)',
                'issuing_organization': 'Cloud Native Computing Foundation',
                'description': 'Validates skills in Kubernetes administration',
                'difficulty_level': 'advanced',
                'is_lifetime': False,
                'validity_years': 3,
                'cost_usd': 395.00,
                'preparation_time_hours': 150,
                'pass_rate': 66.0,
                'salary_boost_percentage': 18.0,
                'market_demand': 'very_high',
                'official_url': 'https://www.cncf.io/certification/cka/',
                'popularity_score': 85.0
            },
            {
                'name': 'Google Cloud Professional Data Engineer',
                'issuing_organization': 'Google Cloud',
                'description': 'Validates ability to design and build data processing systems',
                'difficulty_level': 'advanced',
                'is_lifetime': False,
                'validity_years': 2,
                'cost_usd': 200.00,
                'preparation_time_hours': 100,
                'pass_rate': 68.0,
                'salary_boost_percentage': 20.0,
                'market_demand': 'very_high',
                'official_url': 'https://cloud.google.com/certification/',
                'popularity_score': 82.0
            },
            {
                'name': 'CompTIA Security+',
                'issuing_organization': 'CompTIA',
                'description': 'Validates baseline cybersecurity skills',
                'difficulty_level': 'intermediate',
                'is_lifetime': False,
                'validity_years': 3,
                'cost_usd': 370.00,
                'preparation_time_hours': 80,
                'pass_rate': 83.0,
                'salary_boost_percentage': 12.0,
                'market_demand': 'high',
                'official_url': 'https://www.comptia.org/certifications/security',
                'popularity_score': 78.0
            },
            {
                'name': 'PMP - Project Management Professional',
                'issuing_organization': 'Project Management Institute',
                'description': 'Validates project management knowledge and experience',
                'difficulty_level': 'advanced',
                'is_lifetime': False,
                'validity_years': 3,
                'cost_usd': 555.00,
                'preparation_time_hours': 200,
                'pass_rate': 61.0,
                'salary_boost_percentage': 22.0,
                'market_demand': 'high',
                'official_url': 'https://www.pmi.org/certifications/project-management-pmp',
                'popularity_score': 76.0
            }
        ]
        
        for cert_data in certifications:
            certification, created = Certification.objects.get_or_create(
                name=cert_data['name'],
                issuing_organization=cert_data['issuing_organization'],
                defaults=cert_data
            )
            if created:
                self.stdout.write(f'Created certification: {certification.name}')

    def create_learning_paths(self):
        """Create learning paths."""
        learning_paths = [
            {
                'name': 'Full Stack Web Developer',
                'description': 'Complete path to become a full-stack web developer',
                'target_role': 'Full Stack Developer',
                'difficulty_level': 'intermediate',
                'estimated_duration_weeks': 24,
                'hours_per_week': 15,
                'career_outcomes': [
                    'Web Developer position',
                    'Full Stack Engineer role',
                    'Freelance web development'
                ],
                'salary_range_min': 75000,
                'salary_range_max': 120000,
                'learning_resources': [
                    {
                        'type': 'course',
                        'title': 'HTML/CSS Fundamentals',
                        'url': 'https://example.com',
                        'duration_hours': 40
                    },
                    {
                        'type': 'course',
                        'title': 'JavaScript Mastery',
                        'url': 'https://example.com',
                        'duration_hours': 60
                    },
                    {
                        'type': 'course',
                        'title': 'React Development',
                        'url': 'https://example.com',
                        'duration_hours': 50
                    }
                ],
                'milestones': [
                    {
                        'week': 4,
                        'title': 'Complete HTML/CSS basics'
                    },
                    {
                        'week': 8,
                        'title': 'Build first JavaScript project'
                    },
                    {
                        'week': 16,
                        'title': 'Deploy full React application'
                    },
                    {
                        'week': 24,
                        'title': 'Complete full-stack project'
                    }
                ],
                'is_featured': True,
                'popularity_score': 92.0,
                'success_rate': 78.0
            },
            {
                'name': 'Data Science Specialist',
                'description': 'Comprehensive data science and machine learning path',
                'target_role': 'Data Scientist',
                'difficulty_level': 'advanced',
                'estimated_duration_weeks': 32,
                'hours_per_week': 12,
                'career_outcomes': [
                    'Data Scientist position',
                    'ML Engineer role',
                    'Data Analyst advancement'
                ],
                'salary_range_min': 95000,
                'salary_range_max': 150000,
                'learning_resources': [
                    {
                        'type': 'course',
                        'title': 'Python for Data Science',
                        'url': 'https://example.com',
                        'duration_hours': 50
                    },
                    {
                        'type': 'course',
                        'title': 'Machine Learning Fundamentals',
                        'url': 'https://example.com',
                        'duration_hours': 80
                    }
                ],
                'milestones': [
                    {
                        'week': 8,
                        'title': 'Complete Python fundamentals'
                    },
                    {
                        'week': 16,
                        'title': 'Build first ML model'
                    },
                    {
                        'week': 24,
                        'title': 'Complete data visualization project'
                    },
                    {
                        'week': 32,
                        'title': 'Deploy ML model to production'
                    }
                ],
                'is_featured': True,
                'popularity_score': 88.0,
                'success_rate': 71.0
            },
            {
                'name': 'Cloud Engineer Pathway',
                'description': 'Become a certified cloud infrastructure engineer',
                'target_role': 'Cloud Engineer',
                'difficulty_level': 'intermediate',
                'estimated_duration_weeks': 20,
                'hours_per_week': 10,
                'career_outcomes': [
                    'Cloud Engineer position',
                    'DevOps Engineer role',
                    'Solutions Architect path'
                ],
                'salary_range_min': 85000,
                'salary_range_max': 130000,
                'learning_resources': [
                    {
                        'type': 'course',
                        'title': 'AWS Fundamentals',
                        'url': 'https://example.com',
                        'duration_hours': 40
                    },
                    {
                        'type': 'certification',
                        'title': 'AWS Solutions Architect',
                        'preparation_hours': 100
                    }
                ],
                'milestones': [
                    {
                        'week': 5,
                        'title': 'Complete AWS basics'
                    },
                    {
                        'week': 10,
                        'title': 'Deploy first cloud application'
                    },
                    {
                        'week': 15,
                        'title': 'Design cloud architecture'
                    },
                    {
                        'week': 20,
                        'title': 'Pass AWS certification'
                    }
                ],
                'is_featured': True,
                'popularity_score': 85.0,
                'success_rate': 82.0
            }
        ]
        
        for path_data in learning_paths:
            path, created = LearningPath.objects.get_or_create(
                name=path_data['name'],
                defaults=path_data
            )
            if created:
                self.stdout.write(f'Created learning path: {path.name}')
                
                # Add target skills
                if path.name == 'Full Stack Web Developer':
                    skills = Skill.objects.filter(name__in=['JavaScript', 'React', 'Node.js', 'Python'])
                    path.target_skills.set(skills)
                elif path.name == 'Data Science Specialist':
                    skills = Skill.objects.filter(name__in=['Python', 'Machine Learning', 'SQL'])
                    path.target_skills.set(skills)
                elif path.name == 'Cloud Engineer Pathway':
                    skills = Skill.objects.filter(name__in=['AWS'])
                    path.target_skills.set(skills)