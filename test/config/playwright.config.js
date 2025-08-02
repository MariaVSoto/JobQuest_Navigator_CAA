const { defineConfig, devices } = require('@playwright/test');

/**
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  // Test directory
  testDir: '../frontend/e2e',
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter to use
  reporter: [
    ['html', { outputFolder: '../reports/e2e/html' }],
    ['json', { outputFile: '../reports/e2e/results.json' }],
    ['junit', { outputFile: '../reports/e2e/junit.xml' }],
    ['line'],
    ['allure-playwright', { outputFolder: '../reports/e2e/allure-results' }]
  ],
  
  // Global timeout
  timeout: 30 * 1000,
  expect: {
    timeout: 5 * 1000,
  },
  
  // Shared settings for all the projects below
  use: {
    // Base URL to use in actions like `await page.goto('/')`
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Record video on failure
    video: 'retain-on-failure',
    
    // Take screenshot on failure
    screenshot: 'only-on-failure',
    
    // Browser context options
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    
    // Artifacts
    actionTimeout: 10 * 1000,
    navigationTimeout: 30 * 1000,
  },

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // Mobile browsers
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
    
    // Tablet
    {
      name: 'Tablet',
      use: { ...devices['iPad Pro'] },
    },
    
    // Microsoft Edge
    {
      name: 'Microsoft Edge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },
    
    // Google Chrome
    {
      name: 'Google Chrome',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },
  ],

  // Global setup and teardown
  globalSetup: require.resolve('../shared/utils/globalSetup.js'),
  globalTeardown: require.resolve('../shared/utils/globalTeardown.js'),
  
  // Web server configuration
  webServer: [
    {
      command: 'cd ../../JNv3/apps/backend-fastapi && python run_dev.py',
      port: 8000,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
      env: {
        NODE_ENV: 'test',
        DATABASE_URL: 'postgresql://test:test@localhost:5433/test_jobquest',
      },
    },
    {
      command: 'cd ../../JNv3/apps/frontend-react && npm start',
      port: 3000,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
      env: {
        REACT_APP_API_URL: 'http://localhost:8000',
        REACT_APP_GRAPHQL_URL: 'http://localhost:8000/graphql',
        CI: 'true',
      },
    }
  ],
  
  // Test output directory
  outputDir: '../reports/e2e/test-results',
  
  // Metadata
  metadata: {
    project: 'JobQuest Navigator v3',
    version: '3.0.0',
    environment: process.env.NODE_ENV || 'test',
    browser: 'multi-browser',
    platform: process.platform,
  },
  
  // Test patterns
  testMatch: [
    '**/*.e2e.js',
    '**/*.e2e.ts',
    '**/e2e/**/*.test.js',
    '**/e2e/**/*.test.ts',
    '**/e2e/**/*.spec.js',
    '**/e2e/**/*.spec.ts',
  ],
  
  // Test ignore patterns
  testIgnore: [
    '**/node_modules/**',
    '**/build/**',
    '**/dist/**',
    '**/.git/**',
  ],
  
  // Maximum failures
  maxFailures: process.env.CI ? 10 : undefined,
  
  // Test file extensions
  testFileExtensions: ['js', 'ts'],
  
  // Custom test fixtures
  testFixtures: {
    testDataManager: '../fixtures/e2e/testDataManager.js',
    apiClient: '../shared/utils/apiClient.js',
    authHelpers: '../shared/utils/authHelpers.js',
  },
});

// Environment-specific overrides
if (process.env.NODE_ENV === 'ci') {
  module.exports.retries = 3;
  module.exports.workers = 2;
  module.exports.reporter = [
    ['github'],
    ['html', { outputFolder: '../reports/e2e/html' }],
    ['junit', { outputFile: '../reports/e2e/junit.xml' }],
  ];
}

if (process.env.NODE_ENV === 'development') {
  module.exports.use.headless = false;
  module.exports.use.slowMo = 1000;
  module.exports.reporter = [['line'], ['html']];
}