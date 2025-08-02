# Testing Quick Start Guide

## Getting Started with Testing in JNv3

This guide helps you quickly set up and run the comprehensive testing framework for JobQuest Navigator v3.

## Prerequisites

Before running tests, ensure you have the following installed:

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Docker** and Docker Compose
- **Git** for version control

## Quick Setup

### 1. Navigate to Test Directory

```bash
cd test
```

### 2. Setup Test Environment

```bash
# Automated environment setup
./scripts/setup-test-env.sh
```

This script will:

- Create necessary test directories
- Install Python and Node.js test dependencies
- Configure test databases
- Set up test environment variables
- Validate test environment

### 3. Run Your First Test

```bash
# Run quick test suite (unit tests only)
./scripts/run-all-tests.sh --quick
```

## Test Execution Options

### Complete Test Suite

```bash
# Run all tests (unit, integration, e2e, performance, security)
./scripts/run-all-tests.sh
```

### Targeted Testing

```bash
# Backend tests only (Python/FastAPI)
./scripts/run-all-tests.sh --backend-only

# Frontend tests only (React/Jest)
./scripts/run-all-tests.sh --frontend-only

# End-to-end tests only (Playwright)
./scripts/run-all-tests.sh --e2e-only

# Performance tests (Locust)
./scripts/run-all-tests.sh --performance

# Security tests (Bandit, Safety, Semgrep)
./scripts/run-all-tests.sh --security
```

### Development Workflow

```bash
# Quick validation during development
./scripts/run-all-tests.sh --quick

# Watch mode for continuous testing
./scripts/run-all-tests.sh --watch --frontend-only

# CI/CD optimized run
./scripts/run-all-tests.sh --ci
```

## Viewing Test Results

### Coverage Reports

```bash
# Backend coverage report
open test/reports/coverage/backend/html/index.html

# Frontend coverage report
open test/reports/coverage/frontend/html/index.html
```

### Test Execution Reports

```bash
# E2E test report
open test/reports/e2e/playwright-report/index.html

# Performance test results
open test/reports/performance/locust_report.html

# Security scan results
cat test/reports/security/security_scan_results.txt
```

## Test Structure Overview

```text
test/
├── backend/          # Backend tests (pytest)
│   ├── unit/         # Unit tests (60+ tests)
│   ├── integration/  # Integration tests (30+ tests)
│   └── performance/  # Performance tests (10+ tests)
├── frontend/         # Frontend tests (Jest/Playwright)
│   ├── unit/         # Component tests (60+ tests)
│   ├── integration/  # Frontend integration (30+ tests)
│   └── e2e/          # End-to-end tests (25+ tests)
├── config/           # Test configurations
├── scripts/          # Test execution scripts
├── fixtures/         # Test data and mocks
└── reports/          # Test execution reports
```

## Common Test Commands

### Backend Testing (Python/pytest)

```bash
# Run backend unit tests
cd JNv3/apps/backend-fastapi
pytest tests/unit/

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_user_service.py

# Run tests with markers
pytest -m "unit and not slow"
```

### Frontend Testing (React/Jest)

```bash
# Run frontend unit tests
cd JNv3/apps/frontend-react
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- JobListings.test.jsx

# Run in watch mode
npm test -- --watch
```

### E2E Testing (Playwright)

```bash
# Run E2E tests
cd test
npx playwright test

# Run specific browser
npx playwright test --project=chromium

# Run with debug mode
npx playwright test --debug

# View test report
npx playwright show-report
```

## Environment Configuration

### Test Environment Variables

The testing framework uses the following environment variables:

```bash
# Test database connection
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/jobquest_test

# Coverage thresholds
COVERAGE_THRESHOLD=80

# Test execution
MAX_PARALLEL_JOBS=4
TEST_TIMEOUT=300
```

### Docker Test Environment

```bash
# Start test services
cd JNv3/infrastructure/docker
docker-compose up -d db redis minio

# Check service status
docker-compose ps

# View service logs
docker-compose logs backend
```

## Test Data and Fixtures

### Backend Test Data

```python
# Using Factory Boy for test data
from tests.fixtures.factories import UserFactory, JobFactory

def test_user_creation():
    user = UserFactory(email="test@example.com")
    assert user.email == "test@example.com"
```

### Frontend Test Mocks

```javascript
// Using Mock Service Worker
import { server } from '../fixtures/frontend/mockData.js';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Test Environment Setup Issues

```bash
# Check prerequisites
python --version  # Should be 3.9+
node --version    # Should be 18+
docker --version  # Should be 20+

# Reinstall dependencies
cd test
rm -rf node_modules package-lock.json
npm install
pip install -r requirements-test.txt
```

#### 2. Database Connection Issues

```bash
# Check database container
docker-compose -f JNv3/infrastructure/docker/docker-compose.yml ps db

# Restart database
docker-compose -f JNv3/infrastructure/docker/docker-compose.yml restart db

# Check connection
psql -h localhost -p 5433 -U jobquest_user -d jobquest_navigator_v2
```

#### 3. Port Conflicts

```bash
# Check port usage
lsof -i :3001  # Frontend
lsof -i :8001  # Backend
lsof -i :5433  # Database

# Kill processes using ports
kill -9 $(lsof -ti:3001)
```

#### 4. Permission Issues

```bash
# Make scripts executable
chmod +x test/scripts/*.sh

# Fix ownership issues
sudo chown -R $USER:$USER test/
```

### Reset Test Environment

```bash
# Complete environment reset
cd test
./scripts/cleanup-test-env.sh
./scripts/setup-test-env.sh
```

## Test Development Guidelines

### Writing New Tests

#### Backend Test Example

```python
# tests/unit/test_user_service.py
import pytest
from app.services.user_service import UserService
from tests.fixtures.factories import UserFactory

class TestUserService:
    def test_create_user(self):
        user_data = {"email": "test@example.com", "username": "testuser"}
        user = UserService.create_user(user_data)
        assert user.email == "test@example.com"
    
    def test_get_user_by_id(self):
        user = UserFactory()
        found_user = UserService.get_user_by_id(user.id)
        assert found_user.id == user.id
```

#### Frontend Test Example

```javascript
// src/__tests__/components/JobListings.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { JobListings } from '../../pages/JobListings';
import { renderWithProviders } from '../utils/testUtils';

describe('JobListings', () => {
  test('displays job listings', async () => {
    renderWithProviders(<JobListings />);
    
    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    });
  });
});
```

#### E2E Test Example

```javascript
// test/frontend/e2e/auth.spec.js
import { test, expect } from '@playwright/test';

test('user can login successfully', async ({ page }) => {
  await page.goto('/login');
  
  await page.fill('[data-testid="email"]', 'test@example.com');
  await page.fill('[data-testid="password"]', 'password123');
  await page.click('[data-testid="login-button"]');
  
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
});
```

### Test Naming Conventions

- **Backend**: `test_<functionality>_<scenario>.py`
- **Frontend**: `<Component>.test.jsx`
- **E2E**: `<feature>.spec.js`

### Test Organization

```text
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Tests with external dependencies
├── e2e/           # Full user workflow tests
├── performance/   # Load and stress tests
└── security/      # Security-focused tests
```

## Integration with IDE

### VS Code Configuration

Create `.vscode/settings.json`:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "jest.jestCommandLine": "npm test --",
  "playwright.reuseBrowser": true
}
```

### Test Debugging

```bash
# Debug Python tests
python -m pytest --pdb tests/unit/test_user_service.py

# Debug JavaScript tests
npm test -- --debug JobListings.test.jsx

# Debug E2E tests
npx playwright test --debug auth.spec.js
```

## Continuous Integration

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run pre-commit checks
pre-commit run --all-files
```

### Git Hooks Integration

```bash
# Run tests before push
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

## Performance Tips

### Speed Up Test Execution

```bash
# Run tests in parallel
pytest -n auto

# Skip slow tests during development
pytest -m "not slow"

# Use test database in memory
export TEST_DATABASE_URL=sqlite:///:memory:
```

### Optimize Test Data

```bash
# Use fixtures instead of recreating data
@pytest.fixture(scope="session")
def test_data():
    return create_test_data()

# Clear cache between test runs
pytest --cache-clear
```

## Getting Help

### Documentation

- **Full Testing Guide**: `docs/technical/TESTING_FRAMEWORK.md`
- **Implementation Details**: `test/IMPLEMENTATION_SUMMARY.md`
- **Test Execution Report**: `test/TEST_EXECUTION_REPORT.md`

### Command Help

```bash
# Test runner help
./scripts/run-all-tests.sh --help

# pytest help
pytest --help

# Jest help
npm test -- --help

# Playwright help
npx playwright --help
```

### Common Commands Reference

```bash
# Quick validation
./scripts/run-all-tests.sh --quick

# Full test suite
./scripts/run-all-tests.sh

# Backend only
./scripts/run-all-tests.sh --backend-only

# Frontend only
./scripts/run-all-tests.sh --frontend-only

# E2E only
./scripts/run-all-tests.sh --e2e-only

# With performance
./scripts/run-all-tests.sh --performance

# With security
./scripts/run-all-tests.sh --security

# CI mode
./scripts/run-all-tests.sh --ci
```

---

You're now ready to use the comprehensive testing framework for JobQuest Navigator v3! 🚀

For detailed information, refer to the complete testing documentation in `docs/technical/TESTING_FRAMEWORK.md`.