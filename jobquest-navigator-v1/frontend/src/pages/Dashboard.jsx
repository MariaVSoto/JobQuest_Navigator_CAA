import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import applicationService from '../services/applicationService';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
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
        
        // Fetch recent applications
        const applications = await applicationService.getApplications({ limit: 5 });
        setAppliedJobs(applications.results || applications || []);
        
        // Mock stats for demonstration
        setStats({
          totalApplications: 12,
          interviewsScheduled: 3,
          savedJobs: 8,
          profileViews: 47
        });
        
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [user]);

  const quickActions = [
    { title: 'Browse Jobs', description: 'Find new opportunities', link: '/jobs', icon: '🔍' },
    { title: 'AI Suggestions', description: 'Get personalized recommendations', link: '/ai-suggestions', icon: '🤖' },
    { title: 'Resume Builder', description: 'Update your resume', link: '/resume-builder', icon: '📄' },
    { title: 'Interview Prep', description: 'Practice for interviews', link: '/interview-prep', icon: '💼' }
  ];

  const recentActivities = [
    { type: 'application', content: 'Applied to Software Engineer at TechCorp', time: '2 hours ago' },
    { type: 'save', content: 'Saved Full Stack Developer at StartupXYZ', time: '1 day ago' },
    { type: 'view', content: 'Viewed Senior Developer at BigTech', time: '2 days ago' },
    { type: 'interview', content: 'Interview scheduled with DevCompany', time: '3 days ago' }
  ];

  return (
    <div className="page-container">
      <div className="container">
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
              <p className="text-neutral-600">Ready to take the next step in your career?</p>
            </div>
          </div>
          <div className="header-actions">
            <Link to="/profile" className="btn btn-outline">Edit Profile</Link>
            <Link to="/jobs" className="btn btn-primary">Browse Jobs</Link>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid grid grid-cols-2 md:grid-cols-4 mb-8">
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
        <div className="dashboard-content grid lg:grid-cols-3 gap-6">
          
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
    </div>
  );
};

export default Dashboard; 