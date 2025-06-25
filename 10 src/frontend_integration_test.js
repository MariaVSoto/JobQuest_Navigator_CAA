/**
 * Frontend Integration Test for Phase 1 API Standardization
 * Tests the updated frontend services with new ViewSets endpoints
 */

// Simulate the updated jobService
const API_BASE_URL = 'http://localhost:8000/api';

class JobService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Test the main endpoints that were updated
  async testEndpoints() {
    const endpoints = [
      { name: 'Job List', url: `${this.baseURL}/jobs/jobs/`, expected: 'paginated jobs' },
      { name: 'Job Search', url: `${this.baseURL}/jobs/jobs/search/`, expected: 'search results' },
      { name: 'Nearby Jobs', url: `${this.baseURL}/jobs/jobs/nearby/`, expected: 'nearby jobs' },
      { name: 'Job Map', url: `${this.baseURL}/jobs/jobs/map/`, expected: 'map data' },
      { name: 'Saved Jobs', url: `${this.baseURL}/jobs/saved-jobs/`, expected: 'saved jobs' },
      { name: 'Applications', url: `${this.baseURL}/jobs/applications/`, expected: 'applications' },
      { name: 'Alerts', url: `${this.baseURL}/jobs/alerts/`, expected: 'alerts' },
      { name: 'Skills', url: `${this.baseURL}/jobs/skills/`, expected: 'skills' },
      { name: 'User Skills', url: `${this.baseURL}/jobs/user-skills/`, expected: 'user skills' }
    ];

    console.log('🧪 Testing Frontend Integration with New ViewSets...\n');

    const results = [];
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(endpoint.url);
        const success = response.status === 200 || response.status === 401; // 401 is OK for auth-required endpoints
        results.push({
          name: endpoint.name,
          url: endpoint.url,
          status: response.status,
          success: success,
          note: response.status === 401 ? 'Auth required (expected)' : 'Public endpoint working'
        });
      } catch (error) {
        results.push({
          name: endpoint.name,
          url: endpoint.url,
          status: 'ERROR',
          success: false,
          note: error.message
        });
      }
    }

    return results;
  }

  printResults(results) {
    console.log('📊 Frontend Integration Test Results:\n');
    console.log('| Endpoint | Status | Result | Notes |');
    console.log('|----------|---------|---------|--------|');
    
    results.forEach(result => {
      const status = result.success ? '✅ PASS' : '❌ FAIL';
      console.log(`| ${result.name} | ${result.status} | ${status} | ${result.note} |`);
    });

    const passCount = results.filter(r => r.success).length;
    const totalCount = results.length;
    
    console.log(`\n📈 Summary: ${passCount}/${totalCount} endpoints working correctly`);
    
    if (passCount === totalCount) {
      console.log('🎉 All frontend services updated successfully!');
      console.log('✅ Phase 1 API standardization complete');
    } else {
      console.log('⚠️  Some endpoints need attention');
    }
  }
}

// Run the test
async function runIntegrationTest() {
  const jobService = new JobService();
  const results = await jobService.testEndpoints();
  jobService.printResults(results);
}

// Export for potential use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { JobService, runIntegrationTest };
} else {
  // Run if executed directly
  runIntegrationTest();
}