"""
Django management command to test API security configuration.

This command verifies that API keys are properly configured and that
usage tracking and rate limiting are working correctly.
"""

from django.core.management.base import BaseCommand, CommandError
from core.security import api_manager, usage_tracker, APIKeyNotFoundException


class Command(BaseCommand):
    help = 'Test API security configuration and usage tracking'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--check-keys',
            action='store_true',
            help='Check if API keys are properly configured',
        )
        parser.add_argument(
            '--test-tracking',
            action='store_true',
            help='Test usage tracking functionality',
        )
        parser.add_argument(
            '--show-stats',
            action='store_true',
            help='Show current usage statistics',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== JobQuest Navigator API Security Test ===\n')
        )
        
        if options['check_keys']:
            self.test_api_keys()
        
        if options['test_tracking']:
            self.test_usage_tracking()
        
        if options['show_stats']:
            self.show_usage_stats()
        
        if not any([options['check_keys'], options['test_tracking'], options['show_stats']]):
            # Run all tests by default
            self.test_api_keys()
            self.test_usage_tracking()
            self.show_usage_stats()
    
    def test_api_keys(self):
        """Test API key configuration."""
        self.stdout.write('\n1. Testing API Key Configuration:')
        
        # Test OpenAI key
        try:
            openai_key = api_manager.openai_key
            masked_key = api_manager.get_masked_key(openai_key)
            self.stdout.write(
                self.style.SUCCESS(f'   ✓ OpenAI API Key: {masked_key}')
            )
        except APIKeyNotFoundException as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ OpenAI API Key: {e}')
            )
        
        # Test Adzuna keys
        try:
            adzuna_app_id = api_manager.adzuna_app_id
            self.stdout.write(
                self.style.SUCCESS(f'   ✓ Adzuna App ID: {adzuna_app_id}')
            )
        except APIKeyNotFoundException as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Adzuna App ID: {e}')
            )
        
        try:
            adzuna_key = api_manager.adzuna_app_key
            masked_key = api_manager.get_masked_key(adzuna_key)
            self.stdout.write(
                self.style.SUCCESS(f'   ✓ Adzuna App Key: {masked_key}')
            )
        except APIKeyNotFoundException as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Adzuna App Key: {e}')
            )
    
    def test_usage_tracking(self):
        """Test usage tracking functionality."""
        self.stdout.write('\n2. Testing Usage Tracking:')
        
        try:
            # Test OpenAI tracking with new parameters
            stats = usage_tracker.track_openai_usage(
                model_name='gpt-4o-mini',
                prompt_tokens=60,
                completion_tokens=40
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'   ✓ OpenAI tracking: {stats["tokens_used_today"]} tokens '
                    f'(prompt: {stats["prompt_tokens_today"]}, completion: {stats["completion_tokens_today"]}), '
                    f'${stats["cost_today"]:.6f} cost'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ OpenAI tracking failed: {e}')
            )
        
        try:
            # Test Adzuna tracking
            stats = usage_tracker.track_adzuna_usage()
            self.stdout.write(
                self.style.SUCCESS(
                    f'   ✓ Adzuna tracking: {stats["requests_today"]} requests'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Adzuna tracking failed: {e}')
            )
    
    def show_usage_stats(self):
        """Show current usage statistics."""
        self.stdout.write('\n3. Current Usage Statistics:')
        
        try:
            stats = usage_tracker.get_usage_stats()
            
            if 'openai' in stats:
                openai = stats['openai']
                self.stdout.write(
                    f'   OpenAI: {openai["tokens_used"]}/{openai["tokens_limit"]} tokens '
                    f'({openai["token_usage_percentage"]:.1f}%), '
                    f'${openai["cost_used"]:.6f}/${openai["cost_limit"]:.2f} cost '
                    f'({openai["cost_usage_percentage"]:.1f}%)'
                )
                self.stdout.write(
                    f'           Prompt tokens: {openai["prompt_tokens_used"]}, '
                    f'Completion tokens: {openai["completion_tokens_used"]}'
                )
            
            if 'adzuna' in stats:
                adzuna = stats['adzuna']
                self.stdout.write(
                    f'   Adzuna: {adzuna["requests_used"]}/{adzuna["requests_limit"]} requests'
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Failed to get stats: {e}')
            )
        
        self.stdout.write('\n=== Test Complete ===')