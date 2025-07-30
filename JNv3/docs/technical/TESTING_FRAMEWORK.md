# Testing Framework Documentation

## Overview

JobQuest Navigator v3 features a comprehensive testing framework designed to ensure high code quality, catch regressions early, and provide confidence in deployments. The testing infrastructure supports multiple testing types including unit, integration, end-to-end, performance, and security testing.

## Testing Architecture

### Framework Structure

```text
test/
├── README.md                    # Comprehensive documentation
├── IMPLEMENTATION_SUMMARY.md    # Implementation details
├── TEST_EXECUTION_REPORT.md     # Test execution results
├── backend/                     # Backend testing
│   ├── unit/                   # Unit test templates (60+)
│   ├── integration/            # Integration test templates (30+)
│   └── performance/            # Performance testing setup (10+)
├── frontend/                   # Frontend testing  
│   ├── unit/                   # Component test templates (60+)
│   ├── integration/            # Frontend integration tests (30+)
│   └── e2e/                    # End-to-end testing (25+)
├── config/                     # Test configurations
│   ├── pytest.ini             # Backend test configuration
│   ├── jest.config.js          # Frontend test configuration
│   ├── playwright.config.js    # E2E test configuration
│   └── docker-compose.test.yml # Test environment
├── scripts/                    # Test execution scripts
│   ├── run-all-tests.sh        # Master test runner
│   ├── setup-test-env.sh       # Environment setup
│   └── cleanup-test-env.sh     # Environment cleanup
├── fixtures/                   # Test data and mocks
│   ├── backend/                # Backend test fixtures
│   ├── frontend/               # Frontend mock data
│   └── shared/                 # Shared testing utilities
├── shared/                     # Shared testing utilities
│   └── mocks/                  # Mock Service Worker setup
└── reports/                    # Test execution reports
    ├── backend/                # Backend test reports
    ├── frontend/               # Frontend test reports
    ├── e2e/                    # E2E test reports
    ├── performance/            # Performance test reports
    ├── security/               # Security scan reports
    └── coverage/               # Coverage analysis reports
```

## Testing Technologies

### Backend Testing Stack

- **pytest** - Primary testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting
- **Factory Boy** - Test data generation
- **SQLAlchemy** - Database testing
- **Bandit** - Security linting
- **Safety** - Dependency vulnerability scanning

### Frontend Testing Stack

- **Jest** - Primary testing framework
- **React Testing Library** - Component testing
- **Mock Service Worker** - API mocking
- **@testing-library/jest-dom** - DOM testing utilities
- **Playwright** - End-to-end testing
- **Coverage reporting** - HTML/XML coverage reports

### Performance & Security Testing

- **Locust** - Load testing framework
- **Semgrep** - Static Application Security Testing
- **Performance monitoring** - Response time tracking
- **OWASP compliance** - Security best practices

## Test Coverage Goals

| Test Type | Target Coverage | Current Status |
|-----------|----------------|----------------|
| **Backend Unit Tests** | ≥85% | ✅ Configured |
| **Frontend Unit Tests** | ≥80% | ✅ Configured |
| **Integration Tests** | 60+ test cases | ✅ Implemented |
| **E2E Tests** | 25+ scenarios | ✅ Implemented |
| **Performance Tests** | 10+ load scenarios | ✅ Implemented |
| **Security Tests** | 15+ security checks | ✅ Implemented |

## Running Tests

### Complete Test Suite

```bash
# Execute all tests
cd test
./scripts/run-all-tests.sh
```

### Targeted Testing

```bash
# Backend tests only
./scripts/run-all-tests.sh --backend-only

# Frontend tests only
./scripts/run-all-tests.sh --frontend-only

# End-to-end tests only
./scripts/run-all-tests.sh --e2e-only

# Performance tests
./scripts/run-all-tests.sh --performance

# Security tests
./scripts/run-all-tests.sh --security

# Quick validation (unit tests only)
./scripts/run-all-tests.sh --quick

# CI/CD optimized run
./scripts/run-all-tests.sh --ci
```

### Test Environment Management

```bash
# Setup test environment
./scripts/setup-test-env.sh

# Cleanup test environment
./scripts/cleanup-test-env.sh

# Keep reports after cleanup
./scripts/cleanup-test-env.sh --keep-reports

# Keep all artifacts
./scripts/cleanup-test-env.sh --keep-all
```

## Test Configuration

### Backend Configuration (pytest.ini)

```ini
[tool:pytest]
testpaths = test/backend
python_files = test_*.py *_test.py
addopts = 
    --verbose
    --cov=app
    --cov-report=html:test/reports/coverage/backend/html
    --cov-report=xml:test/reports/coverage/backend/coverage.xml
    --cov-fail-under=85
    --asyncio-mode=auto
```

### Frontend Configuration (jest.config.js)

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/test/config/jest.setup.js'],
  coverageDirectory: 'test/reports/coverage/frontend',
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### E2E Configuration (playwright.config.js)

```javascript
module.exports = {
  testDir: './test/frontend/e2e',
  outputDir: 'test/reports/e2e/test-results',
  use: {
    baseURL: 'http://localhost:3001',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } }
  ]
};
```

## Test Categories

### 1. Authentication & User Management (25 tests)

- User registration/login workflows
- JWT token validation and refresh
- Password reset functionality
- User profile management
- Role-based access control

### 2. Resume Management & PDF Upload (30 tests)

- PDF file upload and validation
- Resume parsing and data extraction
- Resume template generation
- File storage integration (MinIO/S3)
- Resume version management

### 3. Job Search & Application Tracking (25 tests)

- Job search with filters and pagination
- Application submission workflow
- Application status tracking
- Saved jobs functionality
- External API integration (Adzuna)

### 4. AI Suggestions & Company Research (20 tests)

- AI job matching algorithms
- Company research data aggregation
- Skill gap analysis
- Interview preparation content
- Learning path recommendations

### 5. Skills Assessment & Certification (15 tests)

- Skills assessment workflow
- Certification tracking
- Professional development paths
- Skills matching with jobs
- Progress tracking

### 6. GraphQL API Layer (20 tests)

- Schema validation and introspection
- Query/mutation error handling
- Authentication middleware
- Data loading and caching
- Field resolver testing

## Test Data Management

### Backend Test Fixtures

```python
# Backend test fixtures using Factory Boy
@pytest.fixture
def test_user():
    return UserFactory(
        email="test@example.com",
        username="testuser",
        is_active=True
    )

@pytest.fixture
def test_job():
    return JobFactory(
        title="Software Engineer",
        company="Test Company",
        location="Remote"
    )
```

### Frontend Test Mocks

```javascript
// Mock Service Worker setup
import { setupServer } from 'msw/node';
import { graphql } from 'msw';

const server = setupServer(
  graphql.query('GetJobs', (req, res, ctx) => {
    return res(ctx.data({ jobs: mockJobs }));
  }),
  graphql.mutation('CreateUser', (req, res, ctx) => {
    return res(ctx.data({ createUser: { success: true } }));
  })
);
```

## Coverage Reporting

### Viewing Coverage Reports

```bash
# Backend coverage
open test/reports/coverage/backend/html/index.html

# Frontend coverage
open test/reports/coverage/frontend/html/index.html

# Combined coverage report
open test/reports/coverage/combined/index.html
```

### Coverage Thresholds

- **Backend**: Minimum 85% code coverage
- **Frontend**: Minimum 80% code coverage
- **Critical paths**: 100% coverage required
- **Branch coverage**: Enabled for comprehensive testing

## CI/CD Integration

### GitHub Actions Workflow

The testing framework integrates with GitHub Actions for automated testing:

```yaml
name: Comprehensive Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Test Environment
        run: |
          cd test
          ./scripts/setup-test-env.sh
      
      - name: Run All Tests
        run: |
          cd test
          ./scripts/run-all-tests.sh --ci
      
      - name: Upload Coverage Reports
        uses: codecov/codecov-action@v3
        with:
          files: ./test/reports/coverage/coverage.xml
```

### Quality Gates

The CI/CD pipeline enforces the following quality gates:

- **Test Success**: All tests must pass
- **Coverage Threshold**: Backend ≥85%, Frontend ≥80%
- **Security Scan**: No high/critical vulnerabilities
- **Performance**: Response times <500ms
- **Code Quality**: No critical code smells

## Performance Testing

### Load Testing with Locust

```python
from locust import HttpUser, task, between

class JobQuestUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def view_jobs(self):
        self.client.get("/api/jobs")
    
    @task
    def search_jobs(self):
        self.client.get("/api/jobs?search=python")
    
    @task
    def view_job_details(self):
        self.client.get("/api/jobs/1")
```

### Performance Monitoring

- **Response time tracking**: Monitor API response times
- **Resource utilization**: Track CPU, memory, database usage
- **Load testing**: Simulate high traffic scenarios
- **Performance regression**: Detect performance degradation

## Security Testing

### Automated Security Scanning

```bash
# Python security scanning
bandit -r apps/backend-fastapi/app/

# Dependency vulnerability scanning
safety check

# Static Application Security Testing
semgrep --config=auto apps/
```

### Security Test Categories

- **Authentication security**: JWT token validation, session management
- **Authorization testing**: Role-based access control
- **Input validation**: SQL injection, XSS prevention
- **Data protection**: Sensitive data handling
- **API security**: GraphQL security best practices

## Troubleshooting

### Common Issues

1. **Test Database Connection**
   ```bash
   # Check database status
   docker-compose -f JNv3/infrastructure/docker/docker-compose.yml ps db
   
   # Reset test database
   cd test
   ./scripts/cleanup-test-env.sh
   ./scripts/setup-test-env.sh
   ```

2. **Coverage Report Generation**
   ```bash
   # Regenerate coverage reports
   pytest --cov=app --cov-report=html
   npm test -- --coverage
   ```

3. **E2E Test Failures**
   ```bash
   # Debug E2E tests
   npx playwright test --debug
   npx playwright show-report
   ```

### Test Environment Validation

```bash
# Validate test environment
cd test
python -m pytest --version
npm test --version
npx playwright --version
docker --version

# Check test configuration
pytest --collect-only
npm test -- --listTests
```

## Best Practices

### Writing Effective Tests

1. **Test Isolation**: Each test should be independent
2. **Clear Naming**: Use descriptive test names
3. **Arrange-Act-Assert**: Follow AAA pattern
4. **Mock External Dependencies**: Isolate units under test
5. **Test Edge Cases**: Cover boundary conditions

### Test Maintenance

1. **Regular Updates**: Keep tests in sync with code changes
2. **Flaky Test Management**: Identify and fix unreliable tests
3. **Test Documentation**: Document complex test scenarios
4. **Performance Monitoring**: Track test execution times
5. **Coverage Analysis**: Regular coverage reviews

## Integration with Development Workflow

### Pre-commit Testing

```bash
# Run quick tests before commit
cd test
./scripts/run-all-tests.sh --quick
```

### Feature Development Testing

```bash
# Run relevant tests during development
./scripts/run-all-tests.sh --backend-only  # For backend changes
./scripts/run-all-tests.sh --frontend-only # For frontend changes
./scripts/run-all-tests.sh --e2e-only     # For feature validation
```

### Release Testing

```bash
# Complete test suite before release
cd test
./scripts/run-all-tests.sh --performance --security
```

## Monitoring and Metrics

### Test Execution Metrics

- **Test execution time**: Monitor test suite performance
- **Test success rate**: Track test reliability
- **Coverage trends**: Monitor coverage over time
- **Flaky test identification**: Identify unreliable tests

### Quality Metrics

- **Code coverage percentage**: Backend and frontend coverage
- **Security vulnerability count**: Track security issues
- **Performance benchmarks**: API response times
- **Test maintenance burden**: Time spent fixing tests

---

**Last Updated**: July 29, 2025  
**Framework Version**: v1.0.0  
**Status**: Production Ready