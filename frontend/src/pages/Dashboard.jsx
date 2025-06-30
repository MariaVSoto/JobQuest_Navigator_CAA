import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import applicationService from '../services/applicationService';
import './Dashboard.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const Dashboard = () => {
  const { user } = useAuth();
  const [appliedJobs, setAppliedJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchApplications = async () => {
      if (!user) return;
      
      try {
        setLoading(true);
        const applications = await applicationService.getApplications({ limit: 5 });
        setAppliedJobs(applications.results || applications || []);
      } catch (err) {
        console.error('Failed to fetch applications:', err);
        setError('Failed to load recent applications');
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, [user]);

  return (
    <div className="dashboard-container">
      {/* <img src={logo} alt="JobQuest Logo" className="dashboard-logo" /> */}
      <div className="dashboard-profile">
        <div className="dashboard-avatar">
          {user?.profile_picture ? 
            <img src={user.profile_picture} alt="avatar" /> : 
            <div className="avatar-placeholder">{user?.full_name?.[0] || user?.email?.[0] || 'U'}</div>
          }
        </div>
        <div className="dashboard-info">
          <h1 className="dashboard-title">{user?.full_name || 'User'}</h1>
          <p>{user?.email || 'No email'}</p>
        </div>
      </div>
      <div className="dashboard-applied">
        <h3>Recent Applications</h3>
        {loading ? (
          <p>Loading applications...</p>
        ) : error ? (
          <p className="error-message">{error}</p>
        ) : appliedJobs.length > 0 ? (
          <ul>
            {appliedJobs.map(application => (
              <li key={application.id} className="applied-job">
                <span className="job-title">{application.job_title || 'Unknown Position'}</span>
                <span className="job-company">{application.company_name || 'Unknown Company'}</span>
                <span className="job-status">{application.status || 'Not Set'}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-applications">No job applications yet. <a href="/jobs">Start applying!</a></p>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 