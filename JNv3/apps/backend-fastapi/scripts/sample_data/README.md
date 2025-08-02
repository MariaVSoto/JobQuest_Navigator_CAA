# Sample Data Scripts for JobQuest Navigator v2

This directory contains scripts for generating, managing, and validating sample data for demonstration purposes.

## Scripts Overview

### 1. `config.json`
Configuration file containing:
- **User personas**: 5 different career stages and backgrounds
- **Company profiles**: 15 diverse technology companies
- **Job templates**: Realistic job descriptions and requirements
- **Skills database**: Common technical and soft skills
- **Data generation parameters**: Realistic application behaviors and distributions

### 2. `populate_data.py`
Generates comprehensive sample data including users, companies, jobs, applications, and activities.

**Usage:**
```bash
# Generate data for 5 users (default)
python scripts/sample_data/populate_data.py

# Generate data for 10 users
python scripts/sample_data/populate_data.py --users 10

# Use custom configuration file
python scripts/sample_data/populate_data.py --config path/to/custom/config.json

# Preview what would be created (dry run)
python scripts/sample_data/populate_data.py --dry-run
```

**What it creates:**
- **Users**: Based on 5 career personas (recent graduate, experienced developer, senior engineer, product manager, career changer)
- **Companies**: 15 technology companies across different industries
- **Skills**: ~35 technical and professional skills
- **Jobs**: 3-5 jobs per company with realistic salary ranges
- **Applications**: Realistic application patterns based on user personas
- **Saved Jobs**: Jobs saved for later application
- **Activities**: User activity logs for dashboard statistics

### 3. `reset_data.py`
Safely removes sample data while preserving any real user data.

**Usage:**
```bash
# Show current sample data count
python scripts/sample_data/reset_data.py --show-count

# Remove all sample data (requires confirmation)
python scripts/sample_data/reset_data.py --confirm

# Remove specific category only
python scripts/sample_data/reset_data.py --category users --confirm
python scripts/sample_data/reset_data.py --category companies --confirm
python scripts/sample_data/reset_data.py --category jobs --confirm
```

**Safety features:**
- Identifies sample data by email domains (`@demo.jobquest.com`)
- Preserves real user data and external job listings
- Requires explicit confirmation for deletions
- Shows count before deletion

### 4. `validate_data.py`
Validates data integrity, consistency, and quality for demonstration purposes.

**Usage:**
```bash
# Run comprehensive validation
python scripts/sample_data/validate_data.py

# Validate only dashboard data
python scripts/sample_data/validate_data.py --dashboard-only

# Show detailed statistics
python scripts/sample_data/validate_data.py --detailed

# Output results in JSON format
python scripts/sample_data/validate_data.py --json
```

**Validation checks:**
- **Referential integrity**: All foreign keys are valid
- **Data consistency**: Salary ranges, dates, email formats
- **Business logic**: No duplicate applications, realistic distributions
- **Sample data quality**: Persona distribution, industry diversity
- **Dashboard readiness**: Sufficient data for meaningful statistics

## Data Structure

### User Personas
1. **Recent Graduate** (entry level, actively looking)
2. **Experienced Developer** (mid level, casually looking)
3. **Senior Engineer** (senior level, not actively looking)
4. **Product Manager** (mid level, actively looking)
5. **Career Changer** (entry level, actively looking, from marketing background)

### Application Status Distribution
- **Pending**: 40-55% (varies by persona)
- **Rejected**: 25-40%
- **Interview**: 4-30%
- **Offer**: 0.5-12%
- **Withdrawn**: 0.5-3%

### Company Industries
- Technology, Fintech, Healthcare, Gaming
- AI/ML, Cybersecurity, EdTech, GreenTech
- Cloud Computing, Mobile Development
- Enterprise Software, Retail Technology

## Integration with GraphQL

The sample data is designed to work seamlessly with the existing GraphQL endpoints:

- **Dashboard Statistics**: Realistic data for dashboard charts and metrics
- **Job Listings**: Diverse job postings with proper company relationships
- **User Applications**: Complete application history with realistic statuses
- **Skills and Preferences**: Proper skill relationships and user preferences

## Development Workflow

1. **Initial Setup**: Run `populate_data.py` to create sample data
2. **Testing**: Use `validate_data.py` to ensure data quality
3. **Demo Preparation**: Verify dashboard has meaningful statistics
4. **Cleanup**: Use `reset_data.py` when resetting for fresh demo
5. **Iteration**: Modify `config.json` and regenerate as needed

## Configuration Customization

Edit `config.json` to customize:
- **User personas**: Add new career backgrounds and behaviors
- **Companies**: Add industry-specific companies
- **Job templates**: Create templates for new job types
- **Skills**: Add domain-specific skills
- **Locations**: Update geographic preferences

## Database Requirements

Ensure these tables exist in your database:
- `users`, `user_preferences`
- `companies`, `jobs`, `skills`, `job_skills`
- `job_applications`, `saved_jobs`
- `activity_logs`

## Error Handling

All scripts include comprehensive error handling:
- Database connection validation
- Configuration file validation
- Graceful handling of missing dependencies
- Detailed error messages and stack traces

## Best Practices

1. **Always validate** after generating new data
2. **Use dry-run** to preview changes before execution
3. **Backup database** before running reset operations
4. **Check dashboard** to ensure realistic demo experience
5. **Update configuration** based on demo feedback

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the backend root directory
2. **Database Connection**: Verify DATABASE_URL environment variable
3. **Permission Errors**: Check database user permissions
4. **Configuration Errors**: Validate JSON syntax in config.json

### Debug Mode

Add print statements or use Python debugger:
```python
import pdb; pdb.set_trace()  # Add to any script for debugging
```

## Support

For issues or questions:
1. Check validation output for specific errors
2. Review database logs for connection issues
3. Verify configuration file syntax
4. Ensure all required models exist in database schema