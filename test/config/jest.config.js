const path = require('path');

module.exports = {
  // Test environment
  testEnvironment: 'jsdom',
  
  // Root directory
  rootDir: path.resolve(__dirname, '../..'),
  
  // Test file patterns
  testMatch: [
    '<rootDir>/test/frontend/**/__tests__/**/*.(js|jsx|ts|tsx)',
    '<rootDir>/test/frontend/**/*.(test|spec).(js|jsx|ts|tsx)',
    '<rootDir>/JNv3/apps/frontend-react/src/**/__tests__/**/*.(js|jsx|ts|tsx)',
    '<rootDir>/JNv3/apps/frontend-react/src/**/*.(test|spec).(js|jsx|ts|tsx)'
  ],
  
  // Module file extensions
  moduleFileExtensions: [
    'js',
    'jsx',
    'ts',
    'tsx',
    'json',
    'node'
  ],
  
  // Module name mapping for absolute imports
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/JNv3/apps/frontend-react/src/$1',
    '^@test/(.*)$': '<rootDir>/test/$1',
    '^@fixtures/(.*)$': '<rootDir>/test/fixtures/$1',
    '^@shared/(.*)$': '<rootDir>/test/shared/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': '<rootDir>/test/shared/mocks/fileMock.js'
  },
  
  // Setup files
  setupFilesAfterEnv: [
    '<rootDir>/test/config/jest.setup.js'
  ],
  
  // Transform configuration
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
    '^.+\\.css$': '<rootDir>/test/shared/mocks/cssTransform.js',
    '^(?!.*\\.(js|jsx|ts|tsx|css|json)$)': '<rootDir>/test/shared/mocks/fileTransform.js'
  },
  
  // Transform ignore patterns
  transformIgnorePatterns: [
    '[/\\\\]node_modules[/\\\\].+\\.(js|jsx|ts|tsx)$',
    '^.+\\.module\\.(css|sass|scss)$'
  ],
  
  // Coverage configuration
  collectCoverage: true,
  coverageDirectory: '<rootDir>/test/reports/coverage/frontend',
  coverageReporters: [
    'text',
    'text-summary',
    'lcov',
    'html',
    'clover',
    'json'
  ],
  
  // Coverage collection patterns
  collectCoverageFrom: [
    'JNv3/apps/frontend-react/src/**/*.{js,jsx,ts,tsx}',
    '!JNv3/apps/frontend-react/src/**/*.d.ts',
    '!JNv3/apps/frontend-react/src/index.js',
    '!JNv3/apps/frontend-react/src/serviceWorker.js',
    '!JNv3/apps/frontend-react/src/setupTests.js',
    '!JNv3/apps/frontend-react/src/reportWebVitals.js',
    '!JNv3/apps/frontend-react/src/**/*.stories.{js,jsx,ts,tsx}',
    '!JNv3/apps/frontend-react/src/**/*.test.{js,jsx,ts,tsx}',
    '!JNv3/apps/frontend-react/src/**/__tests__/**',
    '!JNv3/apps/frontend-react/src/**/__mocks__/**'
  ],
  
  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    // Specific thresholds for critical modules
    'JNv3/apps/frontend-react/src/services/': {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85
    },
    'JNv3/apps/frontend-react/src/context/': {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85
    },
    'JNv3/apps/frontend-react/src/hooks/': {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  
  // Test timeout
  testTimeout: 30000,
  
  // Verbose output
  verbose: true,
  
  // Watch plugins
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname'
  ],
  
  // Globals for tests
  globals: {
    'process.env.NODE_ENV': 'test',
    'process.env.REACT_APP_API_URL': 'http://localhost:8000',
    'process.env.REACT_APP_GRAPHQL_URL': 'http://localhost:8000/graphql',
    'IS_REACT_ACT_ENVIRONMENT': true
  },
  
  // Module directories
  moduleDirectories: [
    'node_modules',
    '<rootDir>/JNv3/apps/frontend-react/src',
    '<rootDir>/test/shared'
  ],
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Restore mocks after each test
  restoreMocks: true,
  
  // Reset modules between tests
  resetModules: false,
  
  // Error handling
  errorOnDeprecated: true,
  
  // Test result processor
  testResultsProcessor: '<rootDir>/test/shared/utils/testResultsProcessor.js',
  
  // Reporters
  reporters: [
    'default',
    [
      'jest-html-reporters',
      {
        publicPath: './test/reports/frontend',
        filename: 'jest-report.html',
        expand: true,
        hideIcon: false,
        pageTitle: 'JobQuest Navigator Frontend Test Report'
      }
    ],
    [
      'jest-junit',
      {
        outputDirectory: './test/reports/frontend',
        outputName: 'junit.xml',
        suiteName: 'Frontend Tests',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}',
        ancestorSeparator: ' › ',
        usePathForSuiteName: true
      }
    ]
  ],
  
  // Performance monitoring
  maxWorkers: '50%',
  workerIdleMemoryLimit: '500MB',
  
  // Snapshot serializers
  snapshotSerializers: [
    '@emotion/jest/serializer'
  ],
  
  // Test environment options
  testEnvironmentOptions: {
    url: 'http://localhost:3000'
  }
};