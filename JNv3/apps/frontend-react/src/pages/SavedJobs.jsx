import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import unifiedJobService from '../services/unifiedJobService';
import './SavedJobs.css';

const SavedJobs = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [savedJobs, setSavedJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortBy, setSortBy] = useState('saved_date');
  const [filterStatus, setFilterStatus] = useState('all');
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSavedJobs = async () => {
      if (!user) return;
      
      setIsLoading(true);
      setError(null);
      try {
        const response = await unifiedJobService.getSavedJobs({ 
          ordering: `-${sortBy}`,
          limit: 50 
        });
        setSavedJobs(response.results || response || []);
      } catch (err) {
        console.error('Error fetching saved jobs:', err);
        setError('Failed to load saved jobs');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSavedJobs();
  }, [user, sortBy]);

  const handleJobClick = (job) => {
    navigate(`/jobs/${job.id || job.__unique_id || job.redirect_url}`);
  };

  const handleRemoveJob = async (e, jobId) => {
    e.stopPropagation();
    try {
      await unifiedJobService.unsaveJob(jobId);
      setSavedJobs(prev => prev.filter(job => job.job?.id !== jobId));
    } catch (err) {
      console.error('Error removing saved job:', err);
      setError('Failed to remove job from saved list');
    }
  };

  const handleStatusChange = async (e, savedJobId, newStatus) => {
    e.stopPropagation();
    try {
      // Update local state immediately for better UX
      setSavedJobs(prev => prev.map(savedJob => 
        savedJob.id === savedJobId ? { ...savedJob, status: newStatus } : savedJob
      ));
      
      // TODO: Add API call to update saved job status when backend supports it
      // await jobService.updateSavedJobStatus(savedJobId, newStatus);
    } catch (err) {
      console.error('Error updating job status:', err);
      setError('Failed to update job status');
    }
  };

  const handleSortChange = (e) => {
    setSortBy(e.target.value);
  };

  const handleFilterChange = (e) => {
    setFilterStatus(e.target.value);
  };


  if (!user) {
    return (
      <div className="saved-jobs-container">
        <div className="auth-required">
          <h2>Login Required</h2>
          <p>Please log in to view your saved jobs.</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="saved-jobs-container">
        <div className="loading">Loading saved jobs...</div>
      </div>
    );
  }

  const filteredJobs = filterStatus === 'all' 
    ? savedJobs 
    : savedJobs.filter(savedJob => savedJob.status === filterStatus);

  return (
    <div className="saved-jobs-container">
      <div className="saved-jobs-header">
        <h1>Saved Jobs</h1>
        <div className="saved-jobs-controls">
          <div className="control-group">
            <label>Sort by:</label>
            <select value={sortBy} onChange={handleSortChange}>
              <option value="saved_date">Date Saved</option>
              <option value="job__title">Job Title</option>
              <option value="job__company__name">Company</option>
            </select>
          </div>
          <div className="control-group">
            <label>Filter by status:</label>
            <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
              <option value="all">All Statuses</option>
              <option value="applied">Applied</option>
              <option value="interviewing">Interviewing</option>
              <option value="offered">Offered</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="saved-jobs-list">
        {filteredJobs.length === 0 ? (
          <div className="no-jobs">
            {filterStatus === 'all' 
              ? "You haven't saved any jobs yet. Start exploring jobs and save the ones you're interested in!"
              : `No jobs with status "${filterStatus}" found.`}
          </div>
        ) : (
          filteredJobs.map(savedJob => (
            <div 
              key={savedJob.id}
              className="saved-job-card"
              onClick={() => handleJobClick(savedJob.job)}
            >
              <div className="job-main-info">
                <h3>{savedJob.job?.title || 'Unknown Position'}</h3>
                <p className="company">{savedJob.job?.company?.name || 'Unknown Company'}</p>
                <p className="location">{savedJob.job?.location?.city || 'Unknown Location'}</p>
                <div className="job-meta">
                  <span className="job-type">{savedJob.job?.job_type?.replace('_', '-') || 'Full-time'}</span>
                  <span className="saved-date">
                    Saved on {new Date(savedJob.saved_date).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="job-actions">
                <select 
                  value={savedJob.status || 'saved'}
                  onChange={(e) => handleStatusChange(e, savedJob.id, e.target.value)}
                  onClick={(e) => e.stopPropagation()}
                  className={`status-select ${savedJob.status || 'saved'}`}
                >
                  <option value="saved">Saved</option>
                  <option value="applied">Applied</option>
                  <option value="interviewing">Interviewing</option>
                  <option value="offered">Offered</option>
                  <option value="rejected">Rejected</option>
                </select>
                <button 
                  className="remove-btn"
                  onClick={(e) => handleRemoveJob(e, savedJob.job?.id)}
                >
                  Remove
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default SavedJobs; 