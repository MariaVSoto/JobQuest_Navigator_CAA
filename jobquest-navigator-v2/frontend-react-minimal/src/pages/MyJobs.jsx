import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import unifiedJobService from '../services/unifiedJobService';
import './MyJobs.css';

const MyJobs = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [myJobs, setMyJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('date');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (user) {
      fetchMyJobs();
    }
  }, [user]);

  const fetchMyJobs = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch jobs created by the current user
      const response = await unifiedJobService.getJobs({
        user_created: true, // Filter for user-created jobs
        limit: 100, // Get all user jobs
        offset: 0
      });
      
      const jobsData = response.results || response || [];
      setMyJobs(jobsData);
    } catch (err) {
      console.error('Error fetching my jobs:', err);
      setError('Failed to load your job listings. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleJobClick = (jobId) => {
    navigate(`/jobs/${jobId}`);
  };

  const handleEditJob = (e, jobId) => {
    e.stopPropagation();
    // Navigate to edit job page (you may need to create this)
    navigate(`/edit-job/${jobId}`);
  };

  const handleDeleteJob = async (e, jobId) => {
    e.stopPropagation();
    
    if (window.confirm('Are you sure you want to delete this job posting?')) {
      try {
        await unifiedJobService.deleteJob(jobId);
        // Remove from local state
        setMyJobs(prev => prev.filter(job => job.id !== jobId));
      } catch (err) {
        console.error('Error deleting job:', err);
        setError('Failed to delete job. Please try again.');
      }
    }
  };

  const filteredJobs = myJobs
    .filter(job => {
      const matchesStatus = filterStatus === 'all' || 
        (filterStatus === 'active' && job.is_active) ||
        (filterStatus === 'inactive' && !job.is_active);
      
      const matchesSearch = searchQuery === '' || 
        job.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.company?.name?.toLowerCase().includes(searchQuery.toLowerCase());
      
      return matchesStatus && matchesSearch;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        case 'company':
          return (a.company?.name || '').localeCompare(b.company?.name || '');
        default:
          return 0;
      }
    });

  if (isLoading) {
    return (
      <div className="my-jobs-container">
        <div className="loading">Loading your job listings...</div>
      </div>
    );
  }

  return (
    <div className="my-jobs-container">
      <div className="my-jobs-header">
        <div className="header-content">
          <h1>My Job Listings</h1>
          <p className="header-subtitle">Manage the job positions you've uploaded</p>
        </div>
        <div className="header-actions">
          <button 
            className="btn btn-primary"
            onClick={() => navigate('/create-job')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Add New Job
          </button>
        </div>
      </div>

      <div className="my-jobs-controls">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search your job listings..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="filter-sort-controls">
          <div className="control-group">
            <label>Filter by status:</label>
            <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
              <option value="all">All Jobs</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div className="control-group">
            <label>Sort by:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="date">Date Created</option>
              <option value="title">Job Title</option>
              <option value="company">Company</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="my-jobs-stats">
        <div className="stat-item">
          <span className="stat-number">{myJobs.length}</span>
          <span className="stat-label">Total Jobs</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{myJobs.filter(job => job.is_active).length}</span>
          <span className="stat-label">Active</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{myJobs.filter(job => !job.is_active).length}</span>
          <span className="stat-label">Inactive</span>
        </div>
      </div>

      <div className="my-jobs-list">
        {filteredJobs.length === 0 ? (
          <div className="no-jobs">
            {searchQuery || filterStatus !== 'all' ? (
              <>
                <h3>No jobs found</h3>
                <p>No jobs match your current search criteria.</p>
                <button 
                  onClick={() => {
                    setSearchQuery('');
                    setFilterStatus('all');
                  }}
                  className="btn btn-secondary"
                >
                  Clear Filters
                </button>
              </>
            ) : (
              <>
                <div className="no-jobs-icon">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                    <line x1="8" y1="21" x2="16" y2="21"></line>
                    <line x1="12" y1="17" x2="12" y2="21"></line>
                  </svg>
                </div>
                <h3>No job listings yet</h3>
                <p>You haven't uploaded any job positions yet. Start by creating your first job listing.</p>
                <button 
                  onClick={() => navigate('/create-job')}
                  className="btn btn-primary"
                >
                  Create Your First Job
                </button>
              </>
            )}
          </div>
        ) : (
          filteredJobs.map(job => (
            <div key={job.id} className="my-job-card" onClick={() => handleJobClick(job.id)}>
              <div className="job-card-header">
                <div className="job-title-section">
                  <h3 className="job-title">{job.title}</h3>
                  <div className="job-company">{job.company?.name || 'Company Not Specified'}</div>
                  <div className="job-location">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                      <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    <span>{job.location_text || 'Location Not Specified'}</span>
                  </div>
                </div>
                <div className="job-status">
                  <span className={`status-badge ${job.is_active ? 'active' : 'inactive'}`}>
                    {job.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              <div className="job-card-content">
                {job.description && (
                  <p className="job-description">
                    {job.description.length > 150 
                      ? `${job.description.substring(0, 150)}...` 
                      : job.description
                    }
                  </p>
                )}

                <div className="job-details">
                  <div className="detail-item">
                    <span className="label">Created:</span>
                    <span className="value">
                      {new Date(job.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                  {job.job_type && (
                    <div className="detail-item">
                      <span className="label">Type:</span>
                      <span className="value">{job.job_type}</span>
                    </div>
                  )}
                  {job.experience_level && (
                    <div className="detail-item">
                      <span className="label">Level:</span>
                      <span className="value">{job.experience_level}</span>
                    </div>
                  )}
                  {(job.salary_min || job.salary_max) && (
                    <div className="detail-item">
                      <span className="label">Salary:</span>
                      <span className="value">
                        {job.salary_min && job.salary_max 
                          ? `$${parseInt(job.salary_min).toLocaleString()} - $${parseInt(job.salary_max).toLocaleString()}`
                          : job.salary_min 
                          ? `From $${parseInt(job.salary_min).toLocaleString()}`
                          : job.salary_max
                          ? `Up to $${parseInt(job.salary_max).toLocaleString()}`
                          : 'Not specified'}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <div className="job-card-actions">
                <button 
                  className="btn btn-secondary btn-sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleJobClick(job.id);
                  }}
                >
                  View Details
                </button>
                <button 
                  className="btn btn-outline btn-sm"
                  onClick={(e) => handleEditJob(e, job.id)}
                >
                  Edit
                </button>
                <button 
                  className="btn btn-danger btn-sm"
                  onClick={(e) => handleDeleteJob(e, job.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MyJobs;