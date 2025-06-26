"""
Django management command to sync jobs from Adzuna API.

This command provides a CLI interface for testing and running job synchronization
from the Adzuna API with various options for filtering and controlling the sync.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from jobs.services.job_sync import JobSyncService
from core.security import APIKeyNotFoundException


class Command(BaseCommand):
    help = 'Sync jobs from Adzuna API to the local database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--country',
            type=str,
            default='us',
            help='Country code to search (default: us)',
        )
        parser.add_argument(
            '--what',
            type=str,
            help='Job keywords or title to search for',
        )
        parser.add_argument(
            '--where',
            type=str,
            help='Location to search in',
        )
        parser.add_argument(
            '--pages',
            type=int,
            default=1,
            help='Maximum number of pages to fetch (default: 1)',
        )
        parser.add_argument(
            '--per-page',
            type=int,
            default=50,
            help='Results per page (max 50, default: 50)',
        )
        parser.add_argument(
            '--test-connection',
            action='store_true',
            help='Test API connection without syncing jobs',
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Show summary of recent sync activity',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Fetch data but do not save to database',
        )
    
    def handle(self, *args, **options):
        sync_service = JobSyncService()
        
        # Test connection if requested
        if options['test_connection']:
            self.test_api_connection(sync_service)
            return
        
        # Show summary if requested
        if options['summary']:
            self.show_sync_summary(sync_service)
            return
        
        # Validate API configuration
        try:
            # This will raise an exception if keys are not configured
            sync_service.adzuna_api._get_api_credentials()
        except APIKeyNotFoundException as e:
            raise CommandError(f"API configuration error: {e}")
        except Exception as e:
            raise CommandError(f"Failed to validate API configuration: {e}")
        
        # Perform sync
        self.sync_jobs(sync_service, options)
    
    def test_api_connection(self, sync_service):
        """Test the connection to Adzuna API."""
        self.stdout.write(self.style.WARNING('Testing Adzuna API connection...'))
        
        try:
            if sync_service.test_adzuna_connection():
                self.stdout.write(
                    self.style.SUCCESS('✓ Adzuna API connection successful')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Adzuna API connection failed')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Connection test error: {e}')
            )
    
    def show_sync_summary(self, sync_service):
        """Show summary of recent sync activity."""
        self.stdout.write(self.style.WARNING('Recent sync activity summary:'))
        
        try:
            summary = sync_service.get_sync_summary(days=7)
            
            self.stdout.write(f"  Total jobs (last 7 days): {summary['total_jobs']}")
            self.stdout.write(f"  Active jobs: {summary['active_jobs']}")
            self.stdout.write(f"  Unique companies: {summary['unique_companies']}")
            self.stdout.write(f"  Unique locations: {summary['unique_locations']}")
            self.stdout.write(f"  Date range: {summary['date_range']}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to get sync summary: {e}')
            )
    
    def sync_jobs(self, sync_service, options):
        """Perform the actual job synchronization."""
        country = options['country']
        what = options['what']
        where = options['where']
        max_pages = options['pages']
        per_page = min(options['per_page'], 50)  # Adzuna max is 50
        dry_run = options['dry_run']
        
        # Build search description
        search_parts = []
        if what:
            search_parts.append(f"'{what}'")
        if where:
            search_parts.append(f"in {where}")
        search_parts.append(f"({country.upper()})")
        
        search_desc = " ".join(search_parts) if search_parts else f"all jobs in {country.upper()}"
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would sync {search_desc}')
            )
            self.stdout.write(
                self.style.WARNING(f'Pages: {max_pages}, Per page: {per_page}')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Starting job sync for {search_desc}...')
        )
        self.stdout.write(f'  Pages to fetch: {max_pages}')
        self.stdout.write(f'  Results per page: {per_page}')
        
        try:
            stats = sync_service.sync_adzuna_jobs(
                country_code=country,
                what=what,
                where=where,
                max_pages=max_pages,
                results_per_page=per_page
            )
            
            # Display results
            self.display_sync_results(stats)
            
        except Exception as e:
            raise CommandError(f'Sync failed: {e}')
    
    def display_sync_results(self, stats):
        """Display the results of job synchronization."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('SYNC COMPLETED'))
        self.stdout.write('='*50)
        
        # Success metrics
        self.stdout.write(f'Total jobs processed: {stats.total_jobs_processed}')
        self.stdout.write(
            self.style.SUCCESS(f'Jobs created: {stats.jobs_created}')
        )
        self.stdout.write(
            self.style.WARNING(f'Jobs updated: {stats.jobs_updated}')
        )
        
        if stats.jobs_failed > 0:
            self.stdout.write(
                self.style.ERROR(f'Jobs failed: {stats.jobs_failed}')
            )
        
        # Performance metrics
        self.stdout.write(f'Duration: {stats.duration:.2f} seconds')
        if stats.total_jobs_processed > 0:
            rate = stats.total_jobs_processed / stats.duration
            self.stdout.write(f'Processing rate: {rate:.2f} jobs/second')
            
            success_rate = ((stats.total_jobs_processed - stats.jobs_failed) 
                          / stats.total_jobs_processed * 100)
            self.stdout.write(f'Success rate: {success_rate:.1f}%')
        
        # Show errors if any
        if stats.errors:
            self.stdout.write('\nErrors encountered:')
            for i, error in enumerate(stats.errors[:5], 1):  # Show first 5 errors
                self.stdout.write(
                    self.style.ERROR(f'  {i}. {error}')
                )
            if len(stats.errors) > 5:
                self.stdout.write(
                    self.style.ERROR(f'  ... and {len(stats.errors) - 5} more errors')
                )
        
        self.stdout.write('='*50)