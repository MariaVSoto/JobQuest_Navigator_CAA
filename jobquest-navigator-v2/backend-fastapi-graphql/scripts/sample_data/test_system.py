#!/usr/bin/env python3
"""
Test Script for Sample Data System
Validates the sample data system without requiring database connection
"""

import json
import sys
from pathlib import Path


def test_configuration():
    """Test configuration file loading and validation"""
    print("🔍 Testing configuration file...")
    
    config_path = Path(__file__).parent / "config.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        sample_config = config['sample_data_config']
        
        # Test required sections
        required_sections = ['user_personas', 'companies', 'job_templates', 'skills_database', 'locations', 'surnames']
        for section in required_sections:
            if section not in sample_config:
                print(f"❌ Missing required section: {section}")
                return False
            else:
                print(f"✅ Found section: {section}")
        
        # Test data counts
        personas = len(sample_config['user_personas'])
        companies = len(sample_config['companies'])
        job_templates = len(sample_config['job_templates'])
        skills = len(sample_config['skills_database'])
        
        print(f"📊 Data counts:")
        print(f"  User personas: {personas}")
        print(f"  Companies: {companies}")
        print(f"  Job templates: {job_templates}")
        print(f"  Skills: {skills}")
        
        # Validate minimum requirements
        if personas < 3:
            print("⚠️ Consider adding more user personas for diversity")
        if companies < 10:
            print("⚠️ Consider adding more companies for better demo")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration: {e}")
        return False
    except KeyError as e:
        print(f"❌ Missing required configuration key: {e}")
        return False


def test_persona_structure():
    """Test user persona structure and completeness"""
    print("\n👥 Testing user persona structure...")
    
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    personas = config['sample_data_config']['user_personas']
    
    required_persona_fields = [
        'id', 'email_template', 'full_name_templates', 'bio_template',
        'career_level', 'job_search_status', 'preferred_work_type',
        'skills', 'application_behavior'
    ]
    
    for i, persona in enumerate(personas):
        print(f"  Testing persona {i+1}: {persona['id']}")
        
        for field in required_persona_fields:
            if field not in persona:
                print(f"    ❌ Missing field: {field}")
                return False
        
        # Test application behavior structure
        behavior = persona['application_behavior']
        required_behavior_fields = ['applications_per_month', 'response_rate', 'typical_statuses']
        
        for field in required_behavior_fields:
            if field not in behavior:
                print(f"    ❌ Missing behavior field: {field}")
                return False
        
        # Test status distribution sums to ~1.0
        status_sum = sum(behavior['typical_statuses'].values())
        if abs(status_sum - 1.0) > 0.01:
            print(f"    ⚠️ Status distribution doesn't sum to 1.0: {status_sum}")
        
        print(f"    ✅ Persona structure valid")
    
    return True


def test_company_structure():
    """Test company structure and completeness"""
    print("\n🏢 Testing company structure...")
    
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    companies = config['sample_data_config']['companies']
    
    required_company_fields = [
        'name', 'slug', 'description', 'website', 'industry',
        'company_size', 'founded_year', 'job_types', 'location_preferences'
    ]
    
    industries = set()
    
    for i, company in enumerate(companies):
        print(f"  Testing company {i+1}: {company['name']}")
        
        for field in required_company_fields:
            if field not in company:
                print(f"    ❌ Missing field: {field}")
                return False
        
        industries.add(company['industry'])
        print(f"    ✅ Company structure valid")
    
    print(f"  📊 Found {len(industries)} different industries: {', '.join(sorted(industries))}")
    return True


def test_job_templates():
    """Test job template structure"""
    print("\n💼 Testing job templates...")
    
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    templates = config['sample_data_config']['job_templates']
    
    required_template_fields = [
        'description_template', 'requirements_template', 'benefits_template', 'salary_ranges'
    ]
    
    for job_type, template in templates.items():
        print(f"  Testing template: {job_type}")
        
        for field in required_template_fields:
            if field not in template:
                print(f"    ❌ Missing field: {field}")
                return False
        
        # Test salary ranges
        salary_ranges = template['salary_ranges']
        required_levels = ['entry', 'mid', 'senior']
        
        for level in required_levels:
            if level not in salary_ranges:
                print(f"    ❌ Missing salary level: {level}")
                return False
            
            salary_range = salary_ranges[level]
            if 'min' not in salary_range or 'max' not in salary_range:
                print(f"    ❌ Missing min/max in salary range for {level}")
                return False
            
            if salary_range['min'] >= salary_range['max']:
                print(f"    ❌ Invalid salary range for {level}: min >= max")
                return False
        
        print(f"    ✅ Template structure valid")
    
    return True


def test_script_files():
    """Test that all required script files exist"""
    print("\n📄 Testing script files...")
    
    script_dir = Path(__file__).parent
    required_files = [
        'config.json',
        'populate_data.py',
        'reset_data.py',
        'validate_data.py',
        'manage_sample_data.py',
        'README.md'
    ]
    
    for filename in required_files:
        filepath = script_dir / filename
        if filepath.exists():
            print(f"  ✅ {filename} exists")
        else:
            print(f"  ❌ {filename} missing")
            return False
    
    return True


def test_data_relationships():
    """Test logical relationships in configuration data"""
    print("\n🔗 Testing data relationships...")
    
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    sample_config = config['sample_data_config']
    
    # Test that job types in companies exist in job templates
    job_templates = set(sample_config['job_templates'].keys())
    
    for company in sample_config['companies']:
        for job_type in company['job_types']:
            # Allow for partial matches (e.g., "Software Engineer" should work with "Software Engineer" template)
            template_match = any(template in job_type or job_type in template for template in job_templates)
            if not template_match:
                print(f"  ⚠️ Job type '{job_type}' from {company['name']} may not have a matching template")
    
    # Test that skills in personas exist in skills database
    skills_db = set(skill.lower() for skill in sample_config['skills_database'])
    
    for persona in sample_config['user_personas']:
        for skill in persona['skills']:
            if skill.lower() not in skills_db:
                print(f"  ⚠️ Skill '{skill}' from persona '{persona['id']}' not in skills database")
    
    print("  ✅ Data relationships validated")
    return True


def main():
    """Run all tests"""
    print("🧪 Sample Data System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_configuration),
        ("User Persona Structure", test_persona_structure),
        ("Company Structure", test_company_structure),
        ("Job Templates", test_job_templates),
        ("Script Files", test_script_files),
        ("Data Relationships", test_data_relationships)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_function in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_function():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Sample data system is ready for use.")
        print("\nNext steps:")
        print("1. Install faker: pip install faker==22.2.0")
        print("2. Run: python scripts/sample_data/populate_data.py --dry-run")
        print("3. Generate data: python scripts/sample_data/populate_data.py --users 5")
        return True
    else:
        print("⚠️ Some tests failed. Please review and fix issues before proceeding.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)