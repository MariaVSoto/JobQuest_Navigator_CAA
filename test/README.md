# JobQuest Navigator v3 - Testing Infrastructure

This directory contains the comprehensive testing infrastructure for JobQuest Navigator v3, including unit tests, integration tests, end-to-end tests, performance tests, and security tests.

## Directory Structure

```
test/
├── README.md                           # This file
├── config/                            # Test configuration files
│   ├── pytest.ini                    # Backend pytest configuration
│   ├── jest.config.js                # Frontend Jest configuration
│   ├── playwright.config.js          # E2E test configuration
│   ├── docker-compose.test.yml       # Docker test environment
│   └── coverage.json                 # Coverage configuration
├── fixtures/                         # Test data and fixtures
│   ├── backend/                      # Backend test fixtures
│   ├── frontend/                     # Frontend test fixtures
│   └── shared/                       # Shared test data
├── backend/                          # Backend tests
│   ├── unit/                        # Unit tests (60+ tests)
│   ├── integration/                  # Integration tests (30+ tests)
│   ├── graphql/                     # GraphQL-specific tests
│   ├── performance/                  # Performance tests
│   └── security/                    # Security tests
├── frontend/                         # Frontend tests
│   ├── unit/                        # Unit tests (60+ tests)
│   ├── integration/                  # Integration tests (30+ tests)
│   ├── components/                   # Component tests
│   ├── pages/                       # Page tests
│   ├── services/                    # Service tests
│   └── e2e/                         # End-to-end tests (25+ tests)
├── shared/                          # Shared test utilities
│   ├── utils/                       # Test utilities
│   ├── mocks/                       # Mock data and services
│   └── helpers/                     # Test helper functions
├── scripts/                         # Test execution scripts
│   ├── run-all-tests.sh            # Execute all tests
│   ├── run-backend-tests.sh         # Backend tests only
│   ├── run-frontend-tests.sh        # Frontend tests only
│   ├── run-e2e-tests.sh            # E2E tests only
│   ├── run-performance-tests.sh     # Performance tests
│   ├── run-security-tests.sh        # Security tests
│   ├── setup-test-env.sh           # Setup test environment
│   └── cleanup-test-env.sh         # Cleanup test environment
├── reports/                         # Test reports and coverage
│   ├── coverage/                    # Coverage reports
│   ├── performance/                 # Performance test reports
│   └── security/                   # Security test reports
└── ci/                             # CI/CD integration
    ├── github-actions.yml          # GitHub Actions workflow
    ├── test-matrix.yml             # Test matrix configuration
    └── quality-gates.yml           # Quality gate definitions
```

## Test Coverage Goals

### Backend Tests (85% Coverage Target)
- **Unit Tests**: 60+ tests covering models, services, utilities
- **Integration Tests**: 30+ tests covering API endpoints, database operations
- **GraphQL Tests**: 20+ tests covering queries, mutations, subscriptions
- **Performance Tests**: 10+ tests covering load, stress, endurance
- **Security Tests**: 10+ tests covering authentication, authorization, vulnerabilities

### Frontend Tests (80% Coverage Target)
- **Unit Tests**: 60+ tests covering components, hooks, utilities
- **Integration Tests**: 30+ tests covering service integration, state management
- **E2E Tests**: 25+ tests covering user workflows, critical paths
- **Component Tests**: 40+ tests covering UI components
- **Service Tests**: 15+ tests covering API services, GraphQL operations

## Test Types

### 1. Unit Tests
- Test individual functions, methods, and components in isolation
- Use mocks and stubs for external dependencies
- Fast execution, run on every commit

### 2. Integration Tests
- Test interactions between multiple components
- Test API endpoints, database operations
- Test service integrations

### 3. End-to-End Tests
- Test complete user workflows
- Test critical business paths
- Use real browser automation

### 4. Performance Tests
- Load testing for API endpoints
- Stress testing for high traffic scenarios
- Memory and CPU usage testing

### 5. Security Tests
- Authentication and authorization testing
- Input validation and sanitization
- Vulnerability scanning

## Test Data Management

### Fixtures
- **Static Fixtures**: Pre-defined test data for consistent testing
- **Dynamic Fixtures**: Generated test data for various scenarios
- **Shared Fixtures**: Common test data used across multiple tests

### Mock Data
- **API Mocks**: Mock external API responses
- **Database Mocks**: Mock database operations for unit tests
- **Service Mocks**: Mock internal services

## Test Execution

### Local Development
```bash
# Run all tests
./scripts/run-all-tests.sh

# Run specific test suites
./scripts/run-backend-tests.sh
./scripts/run-frontend-tests.sh
./scripts/run-e2e-tests.sh

# Run with coverage
./scripts/run-all-tests.sh --coverage

# Run specific test files
pytest test/backend/unit/test_user_service.py
npm test -- --testPathPattern=components/NavBar
```

### CI/CD Environment
- Tests run automatically on pull requests
- Coverage reports generated and published
- Quality gates enforce minimum coverage thresholds
- Performance regression detection

## Quality Gates

### Coverage Requirements
- Backend: Minimum 85% code coverage
- Frontend: Minimum 80% code coverage
- Critical paths: 95% coverage required

### Performance Requirements
- API response time: < 200ms (95th percentile)
- Page load time: < 2 seconds
- Memory usage: < 512MB per service

### Security Requirements
- No high or critical security vulnerabilities
- Authentication tests must pass
- Input validation tests must pass

## Configuration

### Environment Variables
```bash
# Test database
TEST_DATABASE_URL=postgresql://test:test@localhost:5433/test_jobquest

# Test API keys (use test/sandbox keys)
TEST_OPENAI_API_KEY=sk-test-...
TEST_GOOGLE_MAPS_API_KEY=test-key-...

# Test flags
RUN_SLOW_TESTS=false
RUN_E2E_TESTS=true
HEADLESS_BROWSER=true
```

### Docker Test Environment
- Isolated test database
- Test Redis instance
- Mock external services
- Clean environment for each test run

## Best Practices

### Writing Tests
1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Use Descriptive Names**: Test names should describe the scenario
3. **Test One Thing**: Each test should verify one specific behavior
4. **Use Fixtures**: Reuse test data and setup code
5. **Clean Up**: Properly clean up after tests

### Test Organization
1. **Group Related Tests**: Use test classes or describe blocks
2. **Shared Setup**: Use beforeEach/setUp for common initialization
3. **Test Data**: Keep test data close to tests or in fixtures
4. **Documentation**: Document complex test scenarios

### Maintenance
1. **Regular Updates**: Keep tests updated with code changes
2. **Remove Dead Tests**: Delete obsolete or redundant tests
3. **Monitor Performance**: Track test execution time
4. **Review Coverage**: Regularly review and improve coverage

## Troubleshooting

### Common Issues
1. **Flaky Tests**: Tests that pass/fail intermittently
2. **Slow Tests**: Tests taking too long to execute
3. **Environment Issues**: Tests failing due to environment setup
4. **Data Dependencies**: Tests failing due to data assumptions

### Debugging
1. **Verbose Output**: Use verbose flags for detailed test output
2. **Test Isolation**: Run tests individually to isolate issues
3. **Debug Mode**: Use debugger or print statements
4. **Log Analysis**: Check test logs for error details

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure tests pass before submitting PR
3. Maintain or improve coverage metrics
4. Update test documentation if needed
5. Follow existing test patterns and conventions

## Tools and Libraries

### Backend Testing
- **pytest**: Main testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **factory-boy**: Test data generation
- **freezegun**: Time mocking
- **responses**: HTTP request mocking

### Frontend Testing
- **Jest**: Main testing framework
- **React Testing Library**: React component testing
- **MSW**: API mocking
- **Playwright**: E2E testing
- **@testing-library/user-event**: User interaction simulation

### Performance Testing
- **Locust**: Load testing framework
- **Artillery**: Performance testing toolkit
- **k6**: Load testing tool
- **pytest-benchmark**: Python performance testing

### Security Testing
- **bandit**: Python security linting
- **safety**: Dependency vulnerability scanning
- **OWASP ZAP**: Web application security testing
- **semgrep**: Static analysis security testing