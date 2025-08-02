#!/usr/bin/env python3
"""
Sample Data Validation Script for JobQuest Navigator v2
Validates data integrity and consistency for demonstration purposes
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func

from app.core.database import get_async_db_session
from app.models.user import User, UserPreference, ActivityLog
from app.models.job import Job, Company, Skill, JobApplication, SavedJob, JobSkill


class DataValidator:
    """Validate sample data integrity and consistency"""
    
    def __init__(self):
        self.validation_results = {
            'passed': [],
            'warnings': [],
            'errors': [],
            'stats': {}
        }
    
    async def validate_all_data(self) -> Dict[str, Any]:
        """Run comprehensive data validation"""
        print("🔍 Starting comprehensive data validation...")
        
        async with get_async_db_session() as db:
            # Basic counts and statistics
            await self._validate_basic_counts(db)
            
            # Referential integrity checks
            await self._validate_referential_integrity(db)
            
            # Data consistency checks
            await self._validate_data_consistency(db)
            
            # Business logic validation
            await self._validate_business_logic(db)
            
            # Sample data specific checks
            await self._validate_sample_data_quality(db)
        
        return self._generate_validation_report()
    
    async def _validate_basic_counts(self, db: AsyncSession):
        """Validate basic data counts and statistics"""
        print("📊 Checking basic data counts...")
        
        # Count all entities
        counts = {}
        
        entities = [
            ('users', User),
            ('companies', Company),
            ('skills', Skill),
            ('jobs', Job),
            ('job_applications', JobApplication),
            ('saved_jobs', SavedJob),
            ('activity_logs', ActivityLog),
            ('user_preferences', UserPreference)
        ]
        
        for entity_name, entity_class in entities:
            result = await db.execute(select(func.count(entity_class.id)))
            count = result.scalar()
            counts[entity_name] = count
            
            if count > 0:
                self.validation_results['passed'].append(f"✅ {entity_name.replace('_', ' ').title()}: {count} records")
            else:
                self.validation_results['warnings'].append(f"⚠️ {entity_name.replace('_', ' ').title()}: No records found")
        
        self.validation_results['stats'].update(counts)
        
        # Validate minimum expected counts for demo
        if counts['users'] < 3:
            self.validation_results['warnings'].append("⚠️ Fewer than 3 users - consider adding more for better demo")
        
        if counts['companies'] < 5:
            self.validation_results['warnings'].append("⚠️ Fewer than 5 companies - consider adding more for diversity")
        
        if counts['jobs'] < 10:
            self.validation_results['warnings'].append("⚠️ Fewer than 10 jobs - consider adding more for realistic demo")
    
    async def _validate_referential_integrity(self, db: AsyncSession):
        """Validate foreign key relationships"""
        print("🔗 Checking referential integrity...")
        
        # Check orphaned job applications
        query = text("""
            SELECT COUNT(*) FROM job_applications ja
            LEFT JOIN users u ON ja.user_id = u.id
            LEFT JOIN jobs j ON ja.job_id = j.id
            WHERE u.id IS NULL OR j.id IS NULL
        """)
        result = await db.execute(query)
        orphaned_applications = result.scalar()
        
        if orphaned_applications == 0:
            self.validation_results['passed'].append("✅ All job applications have valid user and job references")
        else:
            self.validation_results['errors'].append(f"❌ {orphaned_applications} orphaned job applications found")
        
        # Check orphaned saved jobs
        query = text("""
            SELECT COUNT(*) FROM saved_jobs sj
            LEFT JOIN users u ON sj.user_id = u.id
            LEFT JOIN jobs j ON sj.job_id = j.id
            WHERE u.id IS NULL OR j.id IS NULL
        """)
        result = await db.execute(query)
        orphaned_saved_jobs = result.scalar()
        
        if orphaned_saved_jobs == 0:
            self.validation_results['passed'].append("✅ All saved jobs have valid user and job references")
        else:
            self.validation_results['errors'].append(f"❌ {orphaned_saved_jobs} orphaned saved jobs found")
        
        # Check orphaned jobs (missing company)
        query = text("""
            SELECT COUNT(*) FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.id
            WHERE c.id IS NULL
        """)
        result = await db.execute(query)
        orphaned_jobs = result.scalar()
        
        if orphaned_jobs == 0:
            self.validation_results['passed'].append("✅ All jobs have valid company references")
        else:
            self.validation_results['errors'].append(f"❌ {orphaned_jobs} jobs with missing company references")
        
        # Check orphaned user preferences
        query = text("""
            SELECT COUNT(*) FROM user_preferences up
            LEFT JOIN users u ON up.user_id = u.id
            WHERE u.id IS NULL
        """)
        result = await db.execute(query)
        orphaned_preferences = result.scalar()
        
        if orphaned_preferences == 0:
            self.validation_results['passed'].append("✅ All user preferences have valid user references")
        else:
            self.validation_results['errors'].append(f"❌ {orphaned_preferences} orphaned user preferences found")
        
        # Check orphaned activity logs
        query = text("""
            SELECT COUNT(*) FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE u.id IS NULL
        """)
        result = await db.execute(query)
        orphaned_activities = result.scalar()
        
        if orphaned_activities == 0:
            self.validation_results['passed'].append("✅ All activity logs have valid user references")
        else:
            self.validation_results['errors'].append(f"❌ {orphaned_activities} orphaned activity logs found")
    
    async def _validate_data_consistency(self, db: AsyncSession):
        """Validate data consistency rules"""
        print("⚖️ Checking data consistency...")
        
        # Check salary consistency (min <= max)
        query = text("""
            SELECT COUNT(*) FROM jobs 
            WHERE salary_min IS NOT NULL 
              AND salary_max IS NOT NULL 
              AND salary_min > salary_max
        """)
        result = await db.execute(query)
        invalid_salaries = result.scalar()
        
        if invalid_salaries == 0:
            self.validation_results['passed'].append("✅ All job salaries have valid min/max ranges")
        else:
            self.validation_results['errors'].append(f"❌ {invalid_salaries} jobs with invalid salary ranges (min > max)")
        
        # Check date consistency (posted_date <= expires_date)
        query = text("""
            SELECT COUNT(*) FROM jobs 
            WHERE posted_date IS NOT NULL 
              AND expires_date IS NOT NULL 
              AND posted_date > expires_date
        """)
        result = await db.execute(query)
        invalid_dates = result.scalar()
        
        if invalid_dates == 0:
            self.validation_results['passed'].append("✅ All job dates are consistent (posted <= expires)")
        else:
            self.validation_results['errors'].append(f"❌ {invalid_dates} jobs with invalid date ranges")
        
        # Check application date consistency (applied_date <= last_updated)
        query = text("""
            SELECT COUNT(*) FROM job_applications 
            WHERE applied_date IS NOT NULL 
              AND last_updated IS NOT NULL 
              AND applied_date > last_updated
        """)
        result = await db.execute(query)
        invalid_app_dates = result.scalar()
        
        if invalid_app_dates == 0:
            self.validation_results['passed'].append("✅ All application dates are consistent")
        else:
            self.validation_results['errors'].append(f"❌ {invalid_app_dates} applications with invalid date ranges")
        
        # Check email format for users
        query = text("""
            SELECT COUNT(*) FROM users 
            WHERE email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
        """)
        result = await db.execute(query)
        invalid_emails = result.scalar()
        
        if invalid_emails == 0:
            self.validation_results['passed'].append("✅ All user emails have valid format")
        else:
            self.validation_results['warnings'].append(f"⚠️ {invalid_emails} users with potentially invalid email format")
    
    async def _validate_business_logic(self, db: AsyncSession):
        """Validate business logic constraints"""
        print("🏢 Checking business logic...")
        
        # Check for duplicate applications (same user, same job)
        query = text("""
            SELECT user_id, job_id, COUNT(*) as app_count
            FROM job_applications 
            GROUP BY user_id, job_id 
            HAVING COUNT(*) > 1
        """)
        result = await db.execute(query)
        duplicate_applications = result.fetchall()
        
        if not duplicate_applications:
            self.validation_results['passed'].append("✅ No duplicate job applications found")
        else:
            self.validation_results['warnings'].append(f"⚠️ {len(duplicate_applications)} cases of duplicate applications found")
        
        # Check for users with no preferences
        query = text("""
            SELECT COUNT(*) FROM users u
            LEFT JOIN user_preferences up ON u.id = up.user_id
            WHERE up.id IS NULL
        """)
        result = await db.execute(query)
        users_no_preferences = result.scalar()
        
        if users_no_preferences == 0:
            self.validation_results['passed'].append("✅ All users have preferences configured")
        else:
            self.validation_results['warnings'].append(f"⚠️ {users_no_preferences} users without preferences")
        
        # Check application status distribution
        query = text("""
            SELECT status, COUNT(*) as count
            FROM job_applications 
            GROUP BY status
        """)
        result = await db.execute(query)
        status_distribution = dict(result.fetchall())
        
        total_applications = sum(status_distribution.values())
        if total_applications > 0:
            # Check for realistic distribution
            pending_ratio = status_distribution.get('pending', 0) / total_applications
            rejected_ratio = status_distribution.get('rejected', 0) / total_applications
            
            if pending_ratio > 0.8:
                self.validation_results['warnings'].append("⚠️ Very high ratio of pending applications - consider updating some statuses")
            
            if rejected_ratio > 0.6:
                self.validation_results['warnings'].append("⚠️ Very high rejection ratio - might be discouraging for demo")
            
            self.validation_results['stats']['application_status_distribution'] = status_distribution
            self.validation_results['passed'].append(f"✅ Application status distribution analyzed ({total_applications} total)")
    
    async def _validate_sample_data_quality(self, db: AsyncSession):
        """Validate sample data specific quality metrics"""
        print("🎯 Checking sample data quality...")
        
        # Check for sample data markers
        query = text("""
            SELECT COUNT(*) FROM users 
            WHERE email LIKE '%@demo.jobquest.com'
        """)
        result = await db.execute(query)
        demo_users = result.scalar()
        
        if demo_users > 0:
            self.validation_results['passed'].append(f"✅ {demo_users} demo users identified")
            self.validation_results['stats']['demo_users'] = demo_users
        
        # Check user persona distribution
        query = text("""
            SELECT career_level, COUNT(*) as count
            FROM users 
            WHERE email LIKE '%@demo.jobquest.com'
            GROUP BY career_level
        """)
        result = await db.execute(query)
        career_distribution = dict(result.fetchall())
        
        if career_distribution:
            self.validation_results['stats']['career_level_distribution'] = career_distribution
            self.validation_results['passed'].append("✅ Career level distribution analyzed")
        
        # Check company diversity
        query = text("""
            SELECT industry, COUNT(*) as count
            FROM companies 
            GROUP BY industry
        """)
        result = await db.execute(query)
        industry_distribution = dict(result.fetchall())
        
        if len(industry_distribution) >= 5:
            self.validation_results['passed'].append(f"✅ Good industry diversity: {len(industry_distribution)} different industries")
        else:
            self.validation_results['warnings'].append(f"⚠️ Limited industry diversity: only {len(industry_distribution)} industries")
        
        self.validation_results['stats']['industry_distribution'] = industry_distribution
        
        # Check job title diversity
        query = text("""
            SELECT title, COUNT(*) as count
            FROM jobs 
            GROUP BY title
            ORDER BY count DESC
            LIMIT 10
        """)
        result = await db.execute(query)
        job_title_distribution = dict(result.fetchall())
        
        if job_title_distribution:
            self.validation_results['stats']['top_job_titles'] = job_title_distribution
            self.validation_results['passed'].append(f"✅ Job title diversity: {len(job_title_distribution)} different titles in top 10")
    
    async def validate_dashboard_data(self) -> Dict[str, Any]:
        """Validate dashboard-specific data for demo purposes"""
        print("📊 Validating dashboard data...")
        
        async with get_async_db_session() as db:
            dashboard_validation = {
                'passed': [],
                'warnings': [],
                'errors': [],
                'stats': {}
            }
            
            # Check if each user has sufficient data for meaningful dashboard
            query = text("""
                SELECT 
                    u.id,
                    u.email,
                    COUNT(DISTINCT ja.id) as applications,
                    COUNT(DISTINCT sj.id) as saved_jobs,
                    COUNT(DISTINCT al.id) as activities
                FROM users u
                LEFT JOIN job_applications ja ON u.id = ja.user_id
                LEFT JOIN saved_jobs sj ON u.id = sj.user_id
                LEFT JOIN activity_logs al ON u.id = al.user_id
                WHERE u.email LIKE '%@demo.jobquest.com'
                GROUP BY u.id, u.email
            """)
            
            result = await db.execute(query)
            user_dashboard_data = result.fetchall()
            
            users_with_good_data = 0
            for user_data in user_dashboard_data:
                user_id, email, applications, saved_jobs, activities = user_data
                
                if applications >= 3 and saved_jobs >= 2 and activities >= 5:
                    users_with_good_data += 1
                elif applications == 0 and saved_jobs == 0:
                    dashboard_validation['warnings'].append(f"⚠️ User {email} has no applications or saved jobs")
            
            if users_with_good_data >= len(user_dashboard_data) * 0.8:
                dashboard_validation['passed'].append(f"✅ {users_with_good_data}/{len(user_dashboard_data)} users have sufficient dashboard data")
            else:
                dashboard_validation['warnings'].append(f"⚠️ Only {users_with_good_data}/{len(user_dashboard_data)} users have sufficient dashboard data")
            
            dashboard_validation['stats']['users_with_dashboard_data'] = users_with_good_data
            dashboard_validation['stats']['total_demo_users'] = len(user_dashboard_data)
            
            return dashboard_validation
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_passed = len(self.validation_results['passed'])
        total_warnings = len(self.validation_results['warnings'])
        total_errors = len(self.validation_results['errors'])
        
        success_rate = total_passed / (total_passed + total_warnings + total_errors) * 100 if (total_passed + total_warnings + total_errors) > 0 else 100
        
        report = {
            'summary': {
                'success_rate': round(success_rate, 1),
                'total_checks': total_passed + total_warnings + total_errors,
                'passed': total_passed,
                'warnings': total_warnings,
                'errors': total_errors
            },
            'results': self.validation_results,
            'recommendation': self._get_recommendation(total_errors, total_warnings)
        }
        
        return report
    
    def _get_recommendation(self, errors: int, warnings: int) -> str:
        """Get recommendation based on validation results"""
        if errors > 0:
            return "❌ Critical errors found. Please fix before using for demo."
        elif warnings > 3:
            return "⚠️ Multiple warnings found. Consider addressing for better demo quality."
        elif warnings > 0:
            return "⚠️ Minor warnings found. Demo should work well but consider improvements."
        else:
            return "✅ All validations passed. Data is ready for demonstration."


async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate sample data for JobQuest Navigator v2')
    parser.add_argument('--dashboard-only', action='store_true', help='Validate only dashboard-specific data')
    parser.add_argument('--detailed', action='store_true', help='Show detailed statistics')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    try:
        validator = DataValidator()
        
        if args.dashboard_only:
            results = await validator.validate_dashboard_data()
        else:
            results = await validator.validate_all_data()
            
            # Also check dashboard data
            dashboard_results = await validator.validate_dashboard_data()
            results['dashboard_validation'] = dashboard_results
        
        if args.json:
            import json
            print(json.dumps(results, indent=2, default=str))
        else:
            # Pretty print results
            print("\n" + "="*60)
            print("📋 VALIDATION REPORT")
            print("="*60)
            
            if 'summary' in results:
                summary = results['summary']
                print(f"Success Rate: {summary['success_rate']}%")
                print(f"Total Checks: {summary['total_checks']}")
                print(f"✅ Passed: {summary['passed']}")
                print(f"⚠️ Warnings: {summary['warnings']}")
                print(f"❌ Errors: {summary['errors']}")
                print(f"\n{results['recommendation']}")
            
            if args.detailed and 'stats' in results.get('results', {}):
                print("\n📊 DETAILED STATISTICS:")
                print("-" * 40)
                stats = results['results']['stats']
                for key, value in stats.items():
                    if isinstance(value, dict):
                        print(f"\n{key.replace('_', ' ').title()}:")
                        for k, v in value.items():
                            print(f"  {k}: {v}")
                    else:
                        print(f"{key.replace('_', ' ').title()}: {value}")
            
            # Show all results
            for category in ['passed', 'warnings', 'errors']:
                if category in results.get('results', {}) and results['results'][category]:
                    print(f"\n{category.upper()}:")
                    for item in results['results'][category]:
                        print(f"  {item}")
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())