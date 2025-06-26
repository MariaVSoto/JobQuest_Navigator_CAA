"""
Django management command to test OpenAI service integration.

This command validates the complete OpenAI service stack:
- Prompt loading and templating
- API connection and authentication
- JSON mode and response validation
- Token usage tracking and cost calculation
"""

from django.core.management.base import BaseCommand
from core.ai.services import openai_service
from core.ai.prompt_manager import prompt_manager
from core.ai.schemas import AIServiceError


class Command(BaseCommand):
    help = 'Test OpenAI service integration and AI response validation'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            default='gpt-4o-mini',
            help='OpenAI model to use for testing (default: gpt-4o-mini)'
        )
        parser.add_argument(
            '--company-name',
            type=str,
            default='Microsoft',
            help='Company name for testing (default: Microsoft)'
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Use synchronous API calls instead of async'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== OpenAI Service Integration Test ===\n')
        )
        
        model = options['model']
        company_name = options['company_name']
        use_sync = options['sync']
        
        # Test 1: Prompt Manager
        self.test_prompt_manager()
        
        # Test 2: OpenAI Service
        self.test_openai_service(model, company_name, use_sync)
        
        # Test 3: Response Validation
        self.test_response_validation()
        
        self.stdout.write('\n=== Test Complete ===')
    
    def test_prompt_manager(self):
        """Test prompt loading and templating."""
        self.stdout.write('\n1. Testing Prompt Manager:')
        
        try:
            # List available prompts
            prompts = prompt_manager.list_prompts()
            self.stdout.write(
                self.style.SUCCESS(f'   ✓ Loaded {len(prompts)} prompt templates')
            )
            
            for prompt_name, prompt in prompts.items():
                self.stdout.write(f'     - {prompt_name}: {prompt.description}')
            
            # Test company research prompt
            try:
                prompt = prompt_manager.get_prompt('company_research', 1)
                test_variables = {
                    'company_name': 'Test Company',
                    'company_description': 'A test software company',
                    'company_website': 'https://test.com',
                    'company_industry': 'Software'
                }
                formatted = prompt.substitute(**test_variables)
                
                self.stdout.write(
                    self.style.SUCCESS('   ✓ Prompt templating successful')
                )
                self.stdout.write(f'     Formatted prompt length: {len(formatted)} characters')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ✗ Prompt templating failed: {e}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Prompt manager failed: {e}')
            )
    
    def test_openai_service(self, model: str, company_name: str, use_sync: bool):
        """Test OpenAI API integration."""
        self.stdout.write(f'\\n2. Testing OpenAI Service (model: {model}, sync: {use_sync}):')
        
        # Prepare test data
        test_variables = {
            'company_name': company_name,
            'company_description': f'{company_name} is a major technology company known for software and cloud services.',
            'company_website': f'https://{company_name.lower()}.com',
            'company_industry': 'Technology'
        }
        
        try:
            self.stdout.write(f'   Making API request for company: {company_name}...')
            
            if use_sync:
                response = openai_service.generate_content_sync(
                    prompt_name='company_research',
                    prompt_variables=test_variables,
                    model=model,
                    temperature=0.3,
                    expected_schema='CompanyResearch'
                )
            else:
                # For testing async in sync context, we'll use sync version
                # In real usage, this would be called from async Celery tasks
                response = openai_service.generate_content_sync(
                    prompt_name='company_research',
                    prompt_variables=test_variables,
                    model=model,
                    temperature=0.3,
                    expected_schema='CompanyResearch'
                )
            
            # Display results
            self.stdout.write(
                self.style.SUCCESS(f'   ✓ API request successful')
            )
            
            self.stdout.write(f'     Model used: {response.model_used}')
            self.stdout.write(f'     Prompt version: {response.prompt_version}')
            self.stdout.write(f'     Total tokens: {response.total_tokens}')
            self.stdout.write(f'     Prompt tokens: {response.prompt_tokens}')
            self.stdout.write(f'     Completion tokens: {response.completion_tokens}')
            self.stdout.write(f'     Estimated cost: ${response.estimated_cost:.6f}')
            self.stdout.write(f'     Response time: {response.response_time_ms}ms')
            self.stdout.write(f'     Validation passed: {response.validation_passed}')
            
            # Display AI-generated content
            data = response.data
            self.stdout.write(f'\\n   Generated Company Research:')
            self.stdout.write(f'     Industry: {data.industry_focus}')
            self.stdout.write(f'     Company size: {data.company_size_estimate}')
            self.stdout.write(f'     Key insights: {len(data.key_insights)} items')
            self.stdout.write(f'     Technologies: {len(data.technologies or [])} items')
            self.stdout.write(f'     Summary length: {len(data.summary)} characters')
            
            # Show first insight as example
            if data.key_insights:
                self.stdout.write(f'     First insight: \"{data.key_insights[0][:100]}...\"')
                
        except AIServiceError as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ OpenAI service error: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Unexpected error: {e}')
            )
    
    def test_response_validation(self):
        """Test response validation with edge cases."""
        self.stdout.write('\\n3. Testing Response Validation:')
        
        try:
            from core.ai.services import OpenAIService
            from core.ai.schemas import CompanyResearch
            import json
            
            service = OpenAIService()
            
            # Test valid JSON
            valid_json = {
                "summary": "Test company summary that meets minimum length requirements for validation.",
                "key_insights": ["First insight", "Second insight"],
                "industry_focus": "Technology",
                "technologies": ["Python", "Django"],
                "company_size_estimate": "medium"
            }
            
            try:
                validated = service._validate_and_parse_response(
                    json.dumps(valid_json), 
                    'CompanyResearch'
                )
                self.stdout.write(
                    self.style.SUCCESS('   ✓ Valid JSON validation successful')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ✗ Valid JSON validation failed: {e}')
                )
            
            # Test invalid JSON
            try:
                service._validate_and_parse_response(
                    'invalid json string',
                    'CompanyResearch'
                )
                self.stdout.write(
                    self.style.ERROR('   ✗ Invalid JSON should have failed validation')
                )
            except Exception:
                self.stdout.write(
                    self.style.SUCCESS('   ✓ Invalid JSON correctly rejected')
                )
            
            # Test missing required fields
            try:
                incomplete_json = {"summary": "Test"}  # Missing required fields
                service._validate_and_parse_response(
                    json.dumps(incomplete_json),
                    'CompanyResearch'
                )
                self.stdout.write(
                    self.style.ERROR('   ✗ Incomplete JSON should have failed validation')
                )
            except Exception:
                self.stdout.write(
                    self.style.SUCCESS('   ✓ Incomplete JSON correctly rejected')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Validation testing failed: {e}')
            )