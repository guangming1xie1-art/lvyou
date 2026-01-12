# End-to-End Testing Guide

This guide provides comprehensive information about the testing setup for the React → Agent → Java API architecture.

## Table of Contents

- [Test Structure](#test-structure)
- [Backend Tests](#backend-tests)
- [Frontend Tests](#frontend-tests)
- [API Integration Tests](#api-integration-tests)
- [Test Fixtures](#test-fixtures)
- [Running Tests](#running-tests)
- [CI/CD Integration](#cicd-integration)
- [Test Coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)

## Test Structure

```
travel-assistant-agent/tests/
├── test_e2e_api.py          # Backend API integration tests
├── test_health.py           # Health check tests
└── __init__.py

travel-assistant-front/tests/
├── integration/
│   ├── search.integration.test.ts      # Search workflow tests
│   ├── recommend.integration.test.ts   # Recommend workflow tests
│   └── booking.integration.test.ts     # Booking workflow tests
├── basic.test.ts            # Basic test example
└── fixtures/                # Test data fixtures

tests/
├── api_integration_test.py  # Complete workflow tests
└── fixtures/                # Shared test data
    ├── search_response.json
    ├── recommend_response.json
    ├── booking_response.json
    └── error_responses.json
```

## Backend Tests

### Location: `travel-assistant-agent/tests/test_e2e_api.py`

**Test Scenarios:**

1. **Search API E2E Test** (`test_search_api_e2e`)
   - Tests complete search workflow
   - Validates response structure and data integrity
   - Tests error handling for invalid parameters

2. **Recommend API E2E Test** (`test_recommend_api_e2e`)
   - Tests complete recommend workflow
   - Validates destination info, attractions, and weather data
   - Tests data consistency

3. **Book API E2E Test** (`test_book_api_e2e`)
   - Tests complete booking workflow
   - Validates booking ID generation
   - Tests price breakdown and confirmation

4. **Status API E2E Test** (`test_status_api_e2e`)
   - Tests task status polling
   - Validates status transitions
   - Tests error handling for non-existent tasks

5. **Error Handling Test** (`test_error_handling`)
   - Tests various error scenarios
   - Validates error response formats
   - Tests network and validation errors

**Dependencies:**
- `pytest`
- `pytest-asyncio`
- `httpx`
- `pytest-mock`
- `pytest-timeout`

## Frontend Tests

### Location: `travel-assistant-front/tests/integration/`

**Test Components:**

1. **Search Integration Tests** (`search.integration.test.ts`)
   - Tests search component rendering
   - Tests user input handling
   - Tests loading states
   - Tests result display
   - Tests error handling
   - Tests API mocking with MSW

2. **Recommend Integration Tests** (`recommend.integration.test.ts`)
   - Tests recommend component rendering
   - Tests preference selection
   - Tests recommendation display
   - Tests weather and attraction data
   - Tests API mocking

3. **Booking Integration Tests** (`booking.integration.test.ts`)
   - Tests booking form rendering
   - Tests passenger information handling
   - Tests booking confirmation display
   - Tests payment processing
   - Tests API mocking

**Dependencies:**
- `vitest`
- `@testing-library/react`
- `@testing-library/user-event`
- `msw` (Mock Service Worker)
- `@vitest/ui`

## API Integration Tests

### Location: `tests/api_integration_test.py`

**Test Scenarios:**

1. **Complete Workflow Test** (`test_complete_workflow`)
   - Tests full workflow: search → recommend → book → status
   - Validates data consistency across all steps
   - Tests task ID tracking
   - Tests error handling

2. **Concurrent Requests Test** (`test_concurrent_requests`)
   - Tests multiple simultaneous requests
   - Validates request isolation
   - Tests server load handling

3. **Performance Test** (`test_performance`)
   - Tests single request response time
   - Tests batch request throughput
   - Tests memory usage
   - Validates performance metrics

## Test Fixtures

### Location: `tests/fixtures/`

**Available Fixtures:**

1. **search_response.json**
   - Complete search API response
   - Includes flights and hotels
   - Contains metadata and pricing

2. **recommend_response.json**
   - Complete recommend API response
   - Includes destination info
   - Contains attractions and weather
   - Includes reviews and tips

3. **booking_response.json**
   - Complete booking API response
   - Includes booking confirmation
   - Contains price breakdown
   - Includes passenger details

4. **error_responses.json**
   - Various error scenarios
   - Invalid request formats
   - Authentication errors
   - Rate limiting errors

## Running Tests

### Backend Tests

```bash
# Run all backend tests
cd travel-assistant-agent
python -m pytest tests/test_e2e_api.py -v

# Run specific test
python -m pytest tests/test_e2e_api.py::test_search_api_e2e -v

# Generate coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

### Frontend Tests

```bash
# Run all frontend tests
cd travel-assistant-front
npm run test

# Run in watch mode
npm run test -- --watch

# Generate coverage report
npm run test -- --coverage
```

### API Integration Tests

```bash
# Run API integration tests
python tests/api_integration_test.py
```

## CI/CD Integration

### GitHub Actions Workflow: `.github/workflows/test.yml`

**Jobs:**

1. **backend-tests**
   - Runs on Ubuntu latest
   - Sets up Python 3.11
   - Installs dependencies
   - Runs pytest tests
   - Runs API integration tests

2. **frontend-tests**
   - Runs on Ubuntu latest
   - Sets up Node.js 20
   - Installs npm dependencies
   - Runs vitest tests
   - Generates coverage report

3. **lint-and-format**
   - Runs ESLint for code quality
   - Runs Prettier for code formatting
   - Ensures code style consistency

**Triggers:**
- Push to any branch
- Pull request creation
- Manual workflow dispatch

## Test Coverage

**Target Coverage:** > 80%

**Coverage Areas:**
- API endpoints (search, recommend, book, status)
- Error handling and validation
- Data consistency and integrity
- User interface components
- State management
- API integration
- Performance and concurrency

## Troubleshooting

### Common Issues

**1. API Server Not Running**
- Ensure the backend server is running on `http://localhost:8000`
- Check Docker containers are up: `docker-compose up -d`
- Verify API health: `curl http://localhost:8000/health`

**2. Test Dependencies Missing**
- Run `pip install -r requirements.txt` for Python dependencies
- Run `npm install` for JavaScript dependencies
- Ensure all test packages are installed

**3. Mock Server Issues**
- Verify MSW is properly configured
- Check mock handlers are correctly set up
- Ensure mock data matches expected API responses

**4. Network Timeouts**
- Increase timeout values in test configuration
- Check server response times
- Verify network connectivity

**5. Authentication Errors**
- Ensure API endpoints don't require authentication for tests
- Mock authentication if needed
- Check CORS settings

### Debugging Tips

**Backend Debugging:**
```bash
# Run tests with verbose output
pytest -vv

# Run tests with logging
pytest --log-cli-level=DEBUG

# Run specific test with breakpoints
pytest -pdb
```

**Frontend Debugging:**
```bash
# Run tests with UI
npm run test -- --ui

# Debug specific test
npm run test -- --reporter=verbose

# Check test coverage details
npm run test -- --coverage --reporter=html
```

## Best Practices

1. **Test Isolation**
   - Each test should be independent
   - Use setup/teardown methods
   - Clean up after tests

2. **Mocking Strategy**
   - Mock external API calls
   - Use fixtures for consistent data
   - Mock only what's necessary

3. **Error Handling**
   - Test both success and failure cases
   - Validate error response formats
   - Test edge cases

4. **Performance Testing**
   - Test under realistic conditions
   - Measure response times
   - Test concurrency scenarios

5. **Documentation**
   - Keep test documentation updated
   - Document test scenarios
   - Explain complex test logic

## Test Data Management

**Creating New Fixtures:**
1. Add JSON files to `tests/fixtures/`
2. Follow existing naming conventions
3. Ensure data is realistic and complete
4. Document fixture contents

**Using Fixtures:**
```python
# Python example
with open('tests/fixtures/search_response.json') as f:
    mock_data = json.load(f)
```

```typescript
// TypeScript example
import mockData from '../../tests/fixtures/search_response.json'
```

## Test Reporting

**Coverage Reports:**
- HTML reports generated in `coverage/` directory
- Detailed breakdown by file and function
- Identifies untested code paths

**Test Results:**
- Console output shows pass/fail status
- Detailed error messages for failures
- Performance metrics included

## Continuous Improvement

**Test Maintenance:**
- Update tests when API changes
- Add new test cases for new features
- Remove obsolete tests
- Keep test data current

**Performance Monitoring:**
- Track test execution times
- Identify slow tests
- Optimize test performance
- Monitor test reliability

**Coverage Improvement:**
- Identify untested code paths
- Add tests for missing coverage
- Focus on critical paths first
- Balance coverage with practicality

## Conclusion

This testing framework provides comprehensive coverage of the React → Agent → Java API architecture, ensuring reliability, performance, and correctness of the complete travel assistant system.