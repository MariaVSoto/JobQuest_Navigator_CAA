#!/usr/bin/env python3
"""
Sample Data Management CLI for JobQuest Navigator v2
Unified interface for all sample data operations
"""

import asyncio
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from populate_data import SampleDataGenerator
from reset_data import SampleDataReset
from validate_data import DataValidator


class SampleDataManager:
    """Unified interface for sample data management"""
    
    def __init__(self):
        self.generator = SampleDataGenerator()
        self.reset_tool = SampleDataReset()
        self.validator = DataValidator()
    
    async def quick_setup(self, num_users: int = 5) -> bool:
        """Quick setup: generate and validate sample data"""
        print("🚀 Quick Setup: Generating and validating sample data...")
        
        try:
            # Generate data
            stats = await self.generator.populate_all_data(num_users)
            print(f"✅ Generated sample data: {stats}")
            
            # Validate data
            validation_results = await self.validator.validate_all_data()
            
            if validation_results['summary']['errors'] > 0:
                print("❌ Validation failed with errors:")
                for error in validation_results['results']['errors']:
                    print(f"  {error}")
                return False
            elif validation_results['summary']['warnings'] > 0:
                print("⚠️ Validation completed with warnings:")
                for warning in validation_results['results']['warnings']:
                    print(f"  {warning}")
            else:
                print("✅ All validations passed!")
            
            print(f"\n{validation_results['recommendation']}")
            return True
            
        except Exception as e:
            print(f"❌ Quick setup failed: {e}")
            return False
    
    async def status_check(self) -> dict:
        """Check current status of sample data"""
        print("📊 Checking sample data status...")
        
        try:
            counts = await self.reset_tool.show_sample_data_count()
            
            # Quick validation
            validation_results = await self.validator.validate_dashboard_data()
            
            status = {
                'data_counts': counts,
                'dashboard_ready': validation_results['stats'].get('users_with_dashboard_data', 0) > 0,
                'recommendation': 'Ready for demo' if sum(counts.values()) > 20 else 'Consider generating more data'
            }
            
            return status
            
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            return {}
    
    async def reset_and_regenerate(self, num_users: int = 5) -> bool:
        """Reset existing data and generate fresh sample data"""
        print("🔄 Reset and Regenerate: Cleaning and creating fresh sample data...")
        
        try:
            # Reset existing data
            print("🧹 Resetting existing sample data...")
            await self.reset_tool.reset_all_data(confirm=True)
            
            # Generate fresh data
            print("🆕 Generating fresh sample data...")
            stats = await self.generator.populate_all_data(num_users)
            
            # Validate new data
            print("🔍 Validating new data...")
            validation_results = await self.validator.validate_all_data()
            
            success = validation_results['summary']['errors'] == 0
            print(f"\n{validation_results['recommendation']}")
            
            return success
            
        except Exception as e:
            print(f"❌ Reset and regenerate failed: {e}")
            return False
    
    async def demo_prep(self) -> bool:
        """Prepare data specifically optimized for demo"""
        print("🎭 Demo Preparation: Optimizing sample data for demonstration...")
        
        try:
            # Check current state
            status = await self.status_check()
            
            if not status.get('dashboard_ready', False):
                print("📊 Dashboard not ready, generating optimized demo data...")
                success = await self.reset_and_regenerate(5)  # 5 users for focused demo
                if not success:
                    return False
            
            # Validate dashboard specifically
            dashboard_validation = await self.validator.validate_dashboard_data()
            
            if dashboard_validation['stats']['users_with_dashboard_data'] >= 4:
                print("✅ Demo preparation completed successfully!")
                print("📊 Dashboard has sufficient data for meaningful demonstration")
                return True
            else:
                print("⚠️ Demo preparation completed with warnings")
                print("📊 Some users may have limited dashboard data")
                return True
                
        except Exception as e:
            print(f"❌ Demo preparation failed: {e}")
            return False


async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sample Data Management for JobQuest Navigator v2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_sample_data.py quick-setup          # Generate and validate data (5 users)
  python manage_sample_data.py quick-setup --users 10  # Generate data for 10 users
  python manage_sample_data.py status               # Check current data status
  python manage_sample_data.py reset-regenerate     # Clean and regenerate all data
  python manage_sample_data.py demo-prep            # Optimize for demo presentation
  python manage_sample_data.py generate --users 8   # Just generate data
  python manage_sample_data.py validate             # Just validate existing data
  python manage_sample_data.py reset --confirm      # Just reset data
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Quick setup command
    quick_parser = subparsers.add_parser('quick-setup', help='Generate and validate sample data')
    quick_parser.add_argument('--users', type=int, default=5, help='Number of users to create')
    
    # Status command
    subparsers.add_parser('status', help='Check current sample data status')
    
    # Reset and regenerate command
    reset_regen_parser = subparsers.add_parser('reset-regenerate', help='Reset and regenerate all data')
    reset_regen_parser.add_argument('--users', type=int, default=5, help='Number of users to create')
    
    # Demo prep command
    subparsers.add_parser('demo-prep', help='Prepare optimized data for demo')
    
    # Individual operations
    generate_parser = subparsers.add_parser('generate', help='Generate sample data only')
    generate_parser.add_argument('--users', type=int, default=5, help='Number of users to create')
    
    subparsers.add_parser('validate', help='Validate existing data only')
    
    reset_parser = subparsers.add_parser('reset', help='Reset sample data only')
    reset_parser.add_argument('--confirm', action='store_true', help='Confirm deletion')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = SampleDataManager()
    
    try:
        if args.command == 'quick-setup':
            success = await manager.quick_setup(args.users)
            sys.exit(0 if success else 1)
            
        elif args.command == 'status':
            status = await manager.status_check()
            if status:
                print("\n📋 Status Summary:")
                for key, value in status.items():
                    print(f"  {key}: {value}")
            
        elif args.command == 'reset-regenerate':
            success = await manager.reset_and_regenerate(args.users)
            sys.exit(0 if success else 1)
            
        elif args.command == 'demo-prep':
            success = await manager.demo_prep()
            sys.exit(0 if success else 1)
            
        elif args.command == 'generate':
            stats = await manager.generator.populate_all_data(args.users)
            print(f"✅ Generated sample data: {stats}")
            
        elif args.command == 'validate':
            results = await manager.validator.validate_all_data()
            print(f"\n{results['recommendation']}")
            
        elif args.command == 'reset':
            stats = await manager.reset_tool.reset_all_data(args.confirm)
            if stats:
                print(f"✅ Reset completed: {stats}")
            
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())