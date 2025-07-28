import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import graphqlApplicationService from '../services/graphqlApplicationService';
import graphqlDashboardService from '../services/graphqlDashboardService';
import MobileLayout from '../components/MobileLayout';
import useResponsive from '../hooks/useResponsive';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const { isMobile, getGridColumns } = useResponsive();
  const [appliedJobs, setAppliedJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalApplications: 0,
    interviewsScheduled: 0,
    savedJobs: 0,
    profileViews: 0
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!user) return;
      
      try {
        setLoading(true);
        
        // Use user ID for GraphQL queries (fallback to demo user ID)
        const userId = user.id || user.userId || 'demo-user-id';
        
        // Fetch dashboard statistics via GraphQL
        const dashboardStatsResult = await graphqlDashboardService.getDashboardStats(userId);
        if (dashboardStatsResult.success) {
          setStats({
            totalApplications: dashboardStatsResult.data.totalApplications,
            interviewsScheduled: dashboardStatsResult.data.interviewsScheduled,
            savedJobs: dashboardStatsResult.data.savedJobs,
            profileViews: dashboardStatsResult.data.profileViews
          });
          
          // Log if using mock data
          if (dashboardStatsResult.isMockData) {
            console.log('🔄 Dashboard using mock data - backend may not be fully connected');
          }
        }
        
        // Fetch recent applications
        const applications = await graphqlApplicationService.getApplications({ limit: 5 });
        setAppliedJobs(applications.results || applications || []);
        
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data');
        
        // Fall back to mock stats on error
        setStats({
          totalApplications: 12,
          interviewsScheduled: 3,
          savedJobs: 8,
          profileViews: 47
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [user]);

  const quickActions = [
    { title: 'Resume Builder', description: 'Create and edit professional resumes', link: '/resume-builder', icon: '📄' },
    { title: 'Version Management', description: 'Manage multiple resume versions', link: '/resume-versions', icon: '🗂️' },
    { title: 'Upload Job Position', description: 'Add job postings for optimization', link: '/upload-job', icon: '📋' },
    { title: 'AI Insights', description: 'Get AI-powered job recommendations', link: '/ai-suggestions', icon: '🤖' },
    { title: 'Skills Assessment', description: 'Enhance your qualifications', link: '/skills', icon: '🎯' },
    { title: 'Interview Prep', description: 'Practice for interviews', link: '/interview-prep', icon: '💼' }
  ];

  const recentActivities = [
    { type: 'application', content: 'Applied to Software Engineer at TechCorp', time: '2 hours ago' },
    { type: 'save', content: 'Saved Full Stack Developer at StartupXYZ', time: '1 day ago' },
    { type: 'view', content: 'Viewed Senior Developer at BigTech', time: '2 days ago' },
    { type: 'interview', content: 'Interview scheduled with DevCompany', time: '3 days ago' }
  ];

  return (
    <MobileLayout>
      <div className={`dashboard-container ${isMobile ? 'dashboard--mobile' : ''}`}>
        {/* Header Section */}
        <div className="dashboard-header">
          <div className="welcome-section">
            <div className="user-avatar-large">
              {user?.profile_picture ? (
                <img src={user.profile_picture} alt="Profile" />
              ) : (
                <span>{user?.first_name?.[0] || user?.email?.[0] || 'U'}</span>
              )}
            </div>
            <div className="welcome-content">
              <h1>Welcome back, {user?.first_name || 'User'}!</h1>
              <p className="welcome-subtitle">Ready to take the next step in your career?</p>
            </div>
          </div>
          {!isMobile && (
            <div className="header-actions">
              <Link to="/profile" className="btn btn-outline">Edit Profile</Link>
              <Link to="/jobs" className="btn btn-primary">Browse Jobs</Link>
            </div>
          )}
        </div>

        {/* Mobile Action Buttons */}
        {isMobile && (
          <div className="mobile-actions">
            <Link to="/profile" className="btn btn-outline btn-mobile-full">Edit Profile</Link>
            <Link to="/jobs" className="btn btn-primary btn-mobile-full">Browse Jobs</Link>
          </div>
        )}

        {/* Stats Grid */}
        <div className={`stats-grid ${isMobile ? 'mobile-stats-grid' : ''}`}>
          <div className="stat-card card">
            <div className="card-body">
              <div className="stat-content">
                <div className="stat-number">{stats.totalApplications}</div>
                <div className="stat-label">Applications</div>
              </div>
              <div className="stat-icon">📊</div>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body">
              <div className="stat-content">
                <div className="stat-number">{stats.interviewsScheduled}</div>
                <div className="stat-label">Interviews</div>
              </div>
              <div className="stat-icon">📅</div>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body">
              <div className="stat-content">
                <div className="stat-number">{stats.savedJobs}</div>
                <div className="stat-label">Saved Jobs</div>
              </div>
              <div className="stat-icon">❤️</div>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body">
              <div className="stat-content">
                <div className="stat-number">{stats.profileViews}</div>
                <div className="stat-label">Profile Views</div>
              </div>
              <div className="stat-icon">👁️</div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className={`dashboard-content ${isMobile ? 'mobile-dashboard-content' : ''}`}>
          
          {/* Quick Actions */}
          <div className="quick-actions-section">
            <div className="card">
              <div className="card-header">
                <h3>Quick Actions</h3>
              </div>
              <div className="card-body">
                <div className="quick-actions-grid">
                  {quickActions.map((action, index) => (
                    <Link
                      key={index}
                      to={action.link}
                      className="quick-action-item"
                    >
                      <div className="action-icon">{action.icon}</div>
                      <div className="action-content">
                        <div className="action-title">{action.title}</div>
                        <div className="action-description">{action.description}</div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Recent Applications */}
          <div className="recent-applications-section">
            <div className="card">
              <div className="card-header">
                <h3>Recent Applications</h3>
                <Link to="/application-history" className="text-primary text-sm font-medium">
                  View All
                </Link>
              </div>
              <div className="card-body">
                {loading ? (
                  <div className="loading-state">
                    <div className="loading"></div>
                    <span>Loading applications...</span>
                  </div>
                ) : error ? (
                  <div className="error-state">
                    <span className="text-error-600">{error}</span>
                  </div>
                ) : appliedJobs.length > 0 ? (
                  <div className="applications-list">
                    {appliedJobs.map(application => (
                      <div key={application.id} className="application-item">
                        <div className="application-content">
                          <div className="application-title">{application.job_title || 'Unknown Position'}</div>
                          <div className="application-company">{application.company_name || 'Unknown Company'}</div>
                        </div>
                        <div className={`application-status status-${(application.status || 'pending').toLowerCase()}`}>
                          {application.status || 'Pending'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <div className="empty-icon">📄</div>
                    <div className="empty-message">No applications yet</div>
                    <Link to="/jobs" className="btn btn-primary btn-sm">Browse Jobs</Link>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="recent-activity-section">
            <div className="card">
              <div className="card-header">
                <h3>Recent Activity</h3>
              </div>
              <div className="card-body">
                <div className="activity-list">
                  {recentActivities.map((activity, index) => (
                    <div key={index} className="activity-item">
                      <div className={`activity-icon activity-${activity.type}`}>
                        {activity.type === 'application' && '📧'}
                        {activity.type === 'save' && '❤️'}
                        {activity.type === 'view' && '👁️'}
                        {activity.type === 'interview' && '📅'}
                      </div>
                      <div className="activity-content">
                        <div className="activity-text">{activity.content}</div>
                        <div className="activity-time">{activity.time}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </MobileLayout>
  );
};

export default Dashboard; 