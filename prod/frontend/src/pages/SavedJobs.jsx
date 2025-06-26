import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { JobContext } from '../context/JobContext';
import './SavedJobs.css';

const SavedJobs = () => {
  const navigate = useNavigate();
  const { jobs } = React.useContext(JobContext);
  const [savedJobs, setSavedJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortBy, setSortBy] = useState('date');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    // In a real application, this would be an API call to fetch saved jobs
    const fetchSavedJobs = async () => {
      setIsLoading(true);
      try {
        // Simulating API call - in reality, this would fetch from backend
        const mockSavedJobs = jobs.slice(0, 5).map(job => ({
          ...job,
          savedDate: new Date(Date.now() - Math.random() * 10000000000),
          status: ['applied', 'interviewing', 'offered', 'rejected'][Math.floor(Math.random() * 4)]
        }));
        setSavedJobs(mockSavedJobs);
      } catch (error) {
        console.error('Error fetching saved jobs:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSavedJobs();
  }, [jobs]);

  const handleJobClick = (job) => {
    navigate(`/jobs/${job.id || job.__unique_id || job.redirect_url}`);
  };

  const handleRemoveJob = (e, jobId) => {
    e.stopPropagation();
    setSavedJobs(prev => prev.filter(job => job.id !== jobId));
    // Here we would typically make an API call to remove the job from saved jobs
  };

  const handleStatusChange = (e, jobId) => {
    e.stopPropagation();
    const newStatus = e.target.value;
    setSavedJobs(prev => prev.map(job => 
      job.id === jobId ? { ...job, status: newStatus } : job
    ));
    // Here we would typically make an API call to update the job status
  };

  const handleSortChange = (e) => {
    setSortBy(e.target.value);
  };

  const handleFilterChange = (e) => {
    setFilterStatus(e.target.value);
  };

  const sortJobs = (jobs) => {
    return [...jobs].sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return b.savedDate - a.savedDate;
        case 'title':
          return a.title.localeCompare(b.title);
        case 'company':
          return (a.company?.display_name || '').localeCompare(b.company?.display_name || '');
        default:
          return 0;
      }
    });
  };

  const filterJobs = (jobs) => {
    if (filterStatus === 'all') return jobs;
    return jobs.filter(job => job.status === filterStatus);
  };

  const filteredAndSortedJobs = sortJobs(filterJobs(savedJobs));

  if (isLoading) {
    return (
      <div className="saved-jobs-container">
        <div className="loading">Loading saved jobs...</div>
      </div>
    );
  }

  return (
    <div className="saved-jobs-container">
      <div className="saved-jobs-header">
        <h1>Saved Jobs</h1>
        <div className="saved-jobs-controls">
          <div className="control-group">
            <label>Sort by:</label>
            <select value={sortBy} onChange={handleSortChange}>
              <option value="date">Date Saved</option>
              <option value="title">Job Title</option>
              <option value="company">Company</option>
            </select>
          </div>
          <div className="control-group">
            <label>Filter by status:</label>
            <select value={filterStatus} onChange={handleFilterChange}>
              <option value="all">All Statuses</option>
              <option value="applied">Applied</option>
              <option value="interviewing">Interviewing</option>
              <option value="offered">Offered</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
      </div>

      <div className="saved-jobs-list">
        {filteredAndSortedJobs.length === 0 ? (
          <div className="no-jobs">
            {filterStatus === 'all' 
              ? "You haven't saved any jobs yet."
              : `No jobs with status "${filterStatus}" found.`}
          </div>
        ) : (
          filteredAndSortedJobs.map(job => (
            <div 
              key={job.id || job.__unique_id || job.redirect_url}
              className="saved-job-card"
              onClick={() => handleJobClick(job)}
            >
              <div className="job-main-info">
                <h3>{job.title}</h3>
                <p className="company">{job.company?.display_name || 'Unknown Company'}</p>
                <p className="location">{job.location?.display_name || 'Unknown Location'}</p>
                <div className="job-meta">
                  <span className="job-type">{job.contract_type || 'Full-time'}</span>
                  <span className="saved-date">
                    Saved on {job.savedDate.toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="job-actions">
                <select 
                  value={job.status}
                  onChange={(e) => handleStatusChange(e, job.id)}
                  onClick={(e) => e.stopPropagation()}
                  className={`status-select ${job.status}`}
                >
                  <option value="applied">Applied</option>
                  <option value="interviewing">Interviewing</option>
                  <option value="offered">Offered</option>
                  <option value="rejected">Rejected</option>
                </select>
                <button 
                  className="remove-btn"
                  onClick={(e) => handleRemoveJob(e, job.id)}
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