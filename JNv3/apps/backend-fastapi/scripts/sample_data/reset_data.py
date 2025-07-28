#!/usr/bin/env python3
"""
Sample Data Reset Script for JobQuest Navigator v2
Safely removes sample data while preserving real user data
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from app.core.database import get_async_db_session
from app.models.user import User, UserPreference, ActivityLog
from app.models.job import Job, Company, Skill, JobApplication, SavedJob, JobSkill


class SampleDataReset:
    """Reset and clean sample data"""
    
    def __init__(self):
        self.sample_data_markers = [
            '@demo.jobquest.com',  # Sample user emails
            'user_input = true',   # User-created jobs
            'Demo user for testing'  # Sample user bios
        ]
    
    async def reset_all_data(self, confirm: bool = False) -> Dict[str, int]:
        """Remove all sample data"""
        if not confirm:
            print("⚠️  This will permanently delete sample data!")
            print("   Use --confirm flag to proceed")
            return {}
        
        print("🧹 Starting sample data cleanup...")
        
        async with get_async_db_session() as db:
            stats = {
                'activity_logs': 0,
                'saved_jobs': 0,
                'job_skills': 0,
                'job_applications': 0,
                'jobs': 0,
                'user_preferences': 0,
                'users': 0,
                'companies': 0,
                'skills': 0
            }
            
            # Step 1: Remove activity logs for sample users
            print("📈 Removing activity logs...")
            stats['activity_logs'] = await self._remove_sample_activity_logs(db)
            
            # Step 2: Remove saved jobs for sample users
            print("❤️ Removing saved jobs...")
            stats['saved_jobs'] = await self._remove_sample_saved_jobs(db)
            
            # Step 3: Remove job skills relationships
            print("🔗 Removing job-skill relationships...")
            stats['job_skills'] = await self._remove_sample_job_skills(db)
            
            # Step 4: Remove job applications for sample users
            print("📝 Removing job applications...")
            stats['job_applications'] = await self._remove_sample_job_applications(db)
            
            # Step 5: Remove sample jobs
            print("💼 Removing sample jobs...")
            stats['jobs'] = await self._remove_sample_jobs(db)
            
            # Step 6: Remove user preferences for sample users
            print("⚙️ Removing user preferences...")
            stats['user_preferences'] = await self._remove_sample_user_preferences(db)
            
            # Step 7: Remove sample users
            print("👥 Removing sample users...")
            stats['users'] = await self._remove_sample_users(db)
            
            # Step 8: Remove sample companies
            print("🏢 Removing sample companies...")
            stats['companies'] = await self._remove_sample_companies(db)
            
            # Step 9: Remove sample skills (optional, with caution)
            print("📊 Removing sample skills...")
            stats['skills'] = await self._remove_sample_skills(db)
            
            await db.commit()
        
        print("✅ Sample data cleanup completed!")
        return stats
    
    async def _remove_sample_activity_logs(self, db: AsyncSession) -> int:
        """Remove activity logs for sample users"""
        # Get sample user IDs
        sample_user_ids = await self._get_sample_user_ids(db)
        
        if not sample_user_ids:
            return 0
        
        # Delete activity logs for sample users
        query = text("""
            DELETE FROM activity_logs 
            WHERE user_id = ANY(:user_ids)
        """)
        
        result = await db.execute(query, {"user_ids": sample_user_ids})
        return result.rowcount
    
    async def _remove_sample_saved_jobs(self, db: AsyncSession) -> int:
        """Remove saved jobs for sample users"""
        sample_user_ids = await self._get_sample_user_ids(db)
        
        if not sample_user_ids:
            return 0
        
        query = text("""
            DELETE FROM saved_jobs 
            WHERE user_id = ANY(:user_ids)
        """)
        
        result = await db.execute(query, {"user_ids": sample_user_ids})
        return result.rowcount
    
    async def _remove_sample_job_skills(self, db: AsyncSession) -> int:
        """Remove job-skill relationships for sample jobs"""
        sample_job_ids = await self._get_sample_job_ids(db)
        
        if not sample_job_ids:
            return 0
        
        query = text("""
            DELETE FROM job_skills 
            WHERE job_id = ANY(:job_ids)
        """)
        
        result = await db.execute(query, {"job_ids": sample_job_ids})
        return result.rowcount
    
    async def _remove_sample_job_applications(self, db: AsyncSession) -> int:
        """Remove job applications for sample users"""
        sample_user_ids = await self._get_sample_user_ids(db)
        
        if not sample_user_ids:
            return 0
        
        query = text("""
            DELETE FROM job_applications 
            WHERE user_id = ANY(:user_ids)
        """)
        
        result = await db.execute(query, {"user_ids": sample_user_ids})
        return result.rowcount
    
    async def _remove_sample_jobs(self, db: AsyncSession) -> int:
        """Remove sample jobs (user_input = true)"""
        query = text("""
            DELETE FROM jobs 
            WHERE user_input = true OR source = 'user_input'
        """)
        
        result = await db.execute(query)
        return result.rowcount
    
    async def _remove_sample_user_preferences(self, db: AsyncSession) -> int:
        """Remove user preferences for sample users"""
        sample_user_ids = await self._get_sample_user_ids(db)
        
        if not sample_user_ids:
            return 0
        
        query = text("""
            DELETE FROM user_preferences 
            WHERE user_id = ANY(:user_ids)
        """)
        
        result = await db.execute(query, {"user_ids": sample_user_ids})
        return result.rowcount
    
    async def _remove_sample_users(self, db: AsyncSession) -> int:
        """Remove sample users (identified by email domain)"""
        query = text("""
            DELETE FROM users 
            WHERE email LIKE '%@demo.jobquest.com' 
               OR bio LIKE '%Demo user for testing%'
               OR full_name LIKE 'Test User%'
        """)
        
        result = await db.execute(query)
        return result.rowcount
    
    async def _remove_sample_companies(self, db: AsyncSession) -> int:
        """Remove sample companies"""
        # Get sample company names from config or common patterns
        sample_company_patterns = [
            'TechForward%', 'StartupVenture%', 'GlobalTech%', 'DataDriven%',
            'CloudNative%', 'MobileFirst%', 'EcoTech%', 'HealthTech%',
            'AIFuture%', 'CyberSafe%', 'EdTech%', 'GameDev%',
            'FinanceFlow%', 'RetailTech%', 'AutoTech%'
        ]
        
        total_deleted = 0
        for pattern in sample_company_patterns:
            query = text("DELETE FROM companies WHERE name LIKE :pattern")
            result = await db.execute(query, {"pattern": pattern})
            total_deleted += result.rowcount
        
        return total_deleted
    
    async def _remove_sample_skills(self, db: AsyncSession) -> int:
        """Remove sample skills (with caution - only unused ones)"""
        # Only remove skills that are not referenced by any job_skills or user_skills
        query = text("""
            DELETE FROM skills 
            WHERE id NOT IN (
                SELECT DISTINCT skill_id FROM job_skills 
                UNION 
                SELECT DISTINCT skill_id FROM user_skills WHERE EXISTS (SELECT 1 FROM user_skills)
            )
            AND description LIKE '%Professional skill in%'
        """)
        
        result = await db.execute(query)
        return result.rowcount
    
    async def _get_sample_user_ids(self, db: AsyncSession) -> List[str]:
        """Get list of sample user IDs"""
        query = text("""
            SELECT id::text FROM users 
            WHERE email LIKE '%@demo.jobquest.com' 
               OR bio LIKE '%Demo user for testing%'
               OR full_name LIKE 'Test User%'
        """)
        
        result = await db.execute(query)
        return [row[0] for row in result.fetchall()]
    
    async def _get_sample_job_ids(self, db: AsyncSession) -> List[str]:
        """Get list of sample job IDs"""
        query = text("""
            SELECT id::text FROM jobs 
            WHERE user_input = true OR source = 'user_input'
        """)
        
        result = await db.execute(query)
        return [row[0] for row in result.fetchall()]
    
    async def reset_specific_category(self, category: str, confirm: bool = False) -> int:
        """Reset specific category of sample data"""
        if not confirm:
            print(f"⚠️  This will permanently delete sample {category}!")
            print("   Use --confirm flag to proceed")
            return 0
        
        async with get_async_db_session() as db:
            if category == 'users':
                count = await self._remove_sample_users(db)
            elif category == 'companies':
                count = await self._remove_sample_companies(db)
            elif category == 'jobs':
                count = await self._remove_sample_jobs(db)
            elif category == 'applications':
                count = await self._remove_sample_job_applications(db)
            elif category == 'saved_jobs':
                count = await self._remove_sample_saved_jobs(db)
            elif category == 'skills':
                count = await self._remove_sample_skills(db)
            else:
                print(f"❌ Unknown category: {category}")
                return 0
            
            await db.commit()
            print(f"✅ Removed {count} sample {category}")
            return count
    
    async def show_sample_data_count(self) -> Dict[str, int]:
        """Show count of sample data without deleting"""
        print("📊 Sample Data Count:")
        print("=" * 40)
        
        async with get_async_db_session() as db:
            counts = {}
            
            # Count sample users
            query = text("""
                SELECT COUNT(*) FROM users 
                WHERE email LIKE '%@demo.jobquest.com' 
                   OR bio LIKE '%Demo user for testing%'
            """)
            result = await db.execute(query)
            counts['sample_users'] = result.scalar()
            
            # Count sample companies
            sample_company_patterns = [
                'TechForward%', 'StartupVenture%', 'GlobalTech%', 'DataDriven%'
            ]
            total_companies = 0
            for pattern in sample_company_patterns:
                query = text("SELECT COUNT(*) FROM companies WHERE name LIKE :pattern")
                result = await db.execute(query, {"pattern": pattern})
                total_companies += result.scalar()
            counts['sample_companies'] = total_companies
            
            # Count sample jobs
            query = text("SELECT COUNT(*) FROM jobs WHERE user_input = true")
            result = await db.execute(query)
            counts['sample_jobs'] = result.scalar()
            
            # Count sample applications
            sample_user_ids = await self._get_sample_user_ids(db)
            if sample_user_ids:
                query = text("SELECT COUNT(*) FROM job_applications WHERE user_id = ANY(:user_ids)")
                result = await db.execute(query, {"user_ids": sample_user_ids})
                counts['sample_applications'] = result.scalar()
            else:
                counts['sample_applications'] = 0
            
            for category, count in counts.items():
                print(f"  {category.replace('_', ' ').title()}: {count}")
            
            print("=" * 40)
            return counts


async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Reset sample data for JobQuest Navigator v2')
    parser.add_argument('--confirm', action='store_true', help='Confirm deletion of sample data')
    parser.add_argument('--category', type=str, 
                       choices=['users', 'companies', 'jobs', 'applications', 'saved_jobs', 'skills'],
                       help='Reset specific category only')
    parser.add_argument('--show-count', action='store_true', help='Show count of sample data without deleting')
    
    args = parser.parse_args()
    
    reset_tool = SampleDataReset()
    
    if args.show_count:
        await reset_tool.show_sample_data_count()
        return
    
    try:
        if args.category:
            count = await reset_tool.reset_specific_category(args.category, args.confirm)
            if count > 0:
                print(f"🎉 Successfully removed {count} sample {args.category}")
        else:
            stats = await reset_tool.reset_all_data(args.confirm)
            if stats:
                print("\n📊 Deletion Summary:")
                print("=" * 40)
                for category, count in stats.items():
                    if count > 0:
                        print(f"  {category.replace('_', ' ').title()}: {count}")
                print("=" * 40)
                print("🎉 Sample data reset completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during data reset: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())