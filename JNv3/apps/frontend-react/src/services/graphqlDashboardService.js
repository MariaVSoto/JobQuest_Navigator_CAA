/**
 * GraphQL Dashboard Service for JobQuest Navigator v2
 * Handles dashboard statistics and data via GraphQL
 */

import { gql } from '@apollo/client';
import apolloClient from '../apolloClient';

// GraphQL Queries
const GET_DASHBOARD_STATS_QUERY = gql`
  query GetDashboardStats($userId: String!, $dateRangeDays: Int) {
    dashboardStats(userId: $userId, dateRangeDays: $dateRangeDays) {
      totalApplications
      interviewsScheduled
      savedJobs
      profileViews
      applicationsThisMonth
      responseRate
      activeApplications
    }
  }
`;

const GET_DASHBOARD_DATA_QUERY = gql`
  query GetDashboardData($userId: String!, $filters: DashboardFilters) {
    dashboardData(userId: $userId, filters: $filters) {
      stats {
        totalApplications
        interviewsScheduled
        savedJobs
        profileViews
        applicationsThisMonth
        responseRate
        activeApplications
      }
      recentActivities {
        id
        type
        content
        timestamp
        relatedJobId
        relatedJobTitle
        relatedCompanyName
      }
      recentApplications {
        id
        status
        appliedDate
        job {
          id
          title
          company {
            name
          }
        }
      }
    }
  }
`;

const GET_APPLICATION_STATUS_STATS_QUERY = gql`
  query GetApplicationStatusStats($userId: String!) {
    applicationStatusStats(userId: $userId) {
      pending
      applied
      interview
      offer
      rejected
      withdrawn
    }
  }
`;

class GraphQLDashboardService {
  constructor() {
    this.client = apolloClient;
  }

  /**
   * Get dashboard statistics for a user
   */
  async getDashboardStats(userId, dateRangeDays = 30) {
    try {
      console.log('Fetching dashboard stats via GraphQL:', { userId, dateRangeDays });
      
      const { data } = await this.client.query({
        query: GET_DASHBOARD_STATS_QUERY,
        variables: { userId, dateRangeDays },
        fetchPolicy: 'cache-and-network',
      });

      console.log('✅ Fetched dashboard stats via GraphQL:', data.dashboardStats);
      
      return {
        success: true,
        data: this.transformStatsToFrontendFormat(data.dashboardStats)
      };
    } catch (error) {
      console.error('GraphQL getDashboardStats error:', error);
      console.log('🔄 Falling back to mock dashboard stats');
      
      // Return mock data as fallback
      return {
        success: true,
        data: this.getMockStats(),
        isMockData: true
      };
    }
  }

  /**
   * Get complete dashboard data
   */
  async getDashboardData(userId, filters = {}) {
    try {
      console.log('Fetching dashboard data via GraphQL:', { userId, filters });
      
      const { data } = await this.client.query({
        query: GET_DASHBOARD_DATA_QUERY,
        variables: { 
          userId, 
          filters: {
            dateRangeDays: filters.dateRangeDays || 30,
            includeActivities: filters.includeActivities !== false,
            activityLimit: filters.activityLimit || 10
          }
        },
        fetchPolicy: 'cache-and-network',
      });

      console.log('✅ Fetched dashboard data via GraphQL');
      
      return {
        success: true,
        data: {
          stats: this.transformStatsToFrontendFormat(data.dashboardData.stats),
          recentActivities: data.dashboardData.recentActivities || [],
          recentApplications: data.dashboardData.recentApplications || []
        }
      };
    } catch (error) {
      console.error('GraphQL getDashboardData error:', error);
      console.log('🔄 Falling back to mock dashboard data');
      
      // Return mock data as fallback
      return {
        success: true,
        data: {
          stats: this.getMockStats(),
          recentActivities: this.getMockActivities(),
          recentApplications: []
        },
        isMockData: true
      };
    }
  }

  /**
   * Get application status statistics
   */
  async getApplicationStatusStats(userId) {
    try {
      console.log('Fetching application status stats via GraphQL:', userId);
      
      const { data } = await this.client.query({
        query: GET_APPLICATION_STATUS_STATS_QUERY,
        variables: { userId },
        fetchPolicy: 'cache-and-network',
      });

      console.log('✅ Fetched application status stats via GraphQL');
      
      return {
        success: true,
        data: data.applicationStatusStats
      };
    } catch (error) {
      console.error('GraphQL getApplicationStatusStats error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Transform GraphQL stats to frontend format
   */
  transformStatsToFrontendFormat(stats) {
    return {
      totalApplications: stats.totalApplications || 0,
      interviewsScheduled: stats.interviewsScheduled || 0,
      savedJobs: stats.savedJobs || 0,
      profileViews: stats.profileViews || 0,
      applicationsThisMonth: stats.applicationsThisMonth || 0,
      responseRate: stats.responseRate || 0,
      activeApplications: stats.activeApplications || 0
    };
  }

  /**
   * Get mock statistics for fallback
   */
  getMockStats() {
    return {
      totalApplications: 12,
      interviewsScheduled: 3,
      savedJobs: 8,
      profileViews: 47,
      applicationsThisMonth: 5,
      responseRate: 25.0,
      activeApplications: 7
    };
  }

  /**
   * Get mock activities for fallback
   */
  getMockActivities() {
    return [
      {
        id: 'mock-activity-1',
        type: 'application',
        content: 'Applied to Software Engineer at TechCorp',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        relatedJobId: 'mock-job-1',
        relatedJobTitle: 'Software Engineer',
        relatedCompanyName: 'TechCorp'
      },
      {
        id: 'mock-activity-2',
        type: 'save',
        content: 'Saved Full Stack Developer at StartupXYZ',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        relatedJobId: 'mock-job-2',
        relatedJobTitle: 'Full Stack Developer',
        relatedCompanyName: 'StartupXYZ'
      },
      {
        id: 'mock-activity-3',
        type: 'view',
        content: 'Viewed Senior Developer at BigTech',
        timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        relatedJobId: 'mock-job-3',
        relatedJobTitle: 'Senior Developer',
        relatedCompanyName: 'BigTech'
      },
      {
        id: 'mock-activity-4',
        type: 'interview',
        content: 'Interview scheduled with DevCompany',
        timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        relatedJobId: 'mock-job-4',
        relatedJobTitle: 'Backend Developer',
        relatedCompanyName: 'DevCompany'
      }
    ];
  }

  /**
   * Utility function to format activity timestamp
   */
  formatActivityTime(timestamp) {
    const now = new Date();
    const activityTime = new Date(timestamp);
    const diffMs = now - activityTime;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) {
      return 'Just now';
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else {
      return activityTime.toLocaleDateString();
    }
  }
}

export default new GraphQLDashboardService();