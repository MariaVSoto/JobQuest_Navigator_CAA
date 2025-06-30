import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { JobContext } from '../context/JobContext';
import './JobListings.css';

const JobListings = () => {
  const navigate = useNavigate();
  
  // Use Job Context instead of GraphQL
  const { 
    jobs, 
    loading, 
    error, 
    filters, 
    setFilters, 
    loadMoreJobs, 
    refreshJobs, 
    saveJob: contextSaveJob, 
    unsaveJob: contextUnsaveJob,
    totalJobs
  } = useContext(JobContext);

  const hasMore = jobs.length < totalJobs;

  const handleFilterChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleJobClick = (job) => {
    navigate(`/jobs/${job.id}`);
  };

  const handleApply = (e, job) => {
    e.stopPropagation(); // Prevent job click event
    navigate(`/apply/${job.id}`);
  };

  const handleSaveJob = async (e, job) => {
    e.stopPropagation();
    if (job.is_saved) {
      const result = await contextUnsaveJob(job.id);
      if (result.success) {
        // Optionally refresh jobs or update local state
        refreshJobs();
      }
    } else {
      const result = await contextSaveJob(job.id);
      if (result.success) {
        // Optionally refresh jobs or update local state
        refreshJobs();
      }
    }
  };

  const handleLoadMore = () => {
    if (!hasMore || loading) return;
    loadMoreJobs();
  };

  return (
    <div className="joblistings-container">
      <aside className="joblistings-sidebar">
        <h3>Filters</h3>
        
        <div className="filter-section">
          <label>Location
            <input 
              name="location" 
              type="text" 
              value={filters.location} 
              onChange={handleFilterChange} 
              placeholder="e.g. San Francisco, CA" 
            />
          </label>
        </div>

        <div className="filter-section">
          <label>Company
            <input 
              name="company" 
              type="text" 
              value={filters.company} 
              onChange={handleFilterChange} 
              placeholder="e.g. TechCorp" 
            />
          </label>
        </div>

        <div className="filter-section">
          <label>Job Type
            <select name="type" value={filters.type} onChange={handleFilterChange}>
              <option value="">All Types</option>
              <option value="full_time">Full-time</option>
              <option value="part_time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="freelance">Freelance</option>
              <option value="internship">Internship</option>
            </select>
          </label>
        </div>

        <div className="filter-section">
          <label>Experience Level
            <select name="experience_level" value={filters.experience_level || ''} onChange={handleFilterChange}>
              <option value="">All Levels</option>
              <option value="entry">Entry Level</option>
              <option value="junior">Junior</option>
              <option value="mid">Mid Level</option>
              <option value="senior">Senior</option>
              <option value="lead">Lead</option>
              <option value="manager">Manager</option>
            </select>
          </label>
        </div>

        <div className="filter-section">
          <label>Remote Type
            <select name="remote_type" value={filters.remote_type || ''} onChange={handleFilterChange}>
              <option value="">All Work Types</option>
              <option value="on_site">On-site</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
            </select>
          </label>
        </div>

        <div className="filter-section">
          <label>Minimum Salary
            <input 
              name="salary_min" 
              type="number" 
              value={filters.salary_min || ''} 
              onChange={handleFilterChange} 
              placeholder="e.g. 70000"
              min="0"
            />
          </label>
        </div>

        <div className="filter-section">
          <button 
            className="clear-filters-btn" 
            onClick={() => setFilters({
              search: '',
              location: '',
              company: '',
              type: '',
              experience_level: '',
              remote_type: '',
              salary_min: '',
            })}
          >
            Clear All Filters
          </button>
        </div>
      </aside>
      <main className="joblistings-main">
        <div className="main-header">
          <h1 className="joblistings-title">Job Listings</h1>
          <div className="search-and-sort">
            <div className="joblistings-searchbar">
              <input
                name="search"
                type="text"
                value={filters.search}
                onChange={handleFilterChange}
                placeholder="Search job titles, companies, or skills..."
              />
            </div>
            <div className="sort-options">
              <select 
                name="sort" 
                value={filters.sort || ''} 
                onChange={handleFilterChange}
                className="sort-select"
              >
                <option value="">Sort by</option>
                <option value="posted_date">Latest First</option>
                <option value="-posted_date">Oldest First</option>
                <option value="title">Title A-Z</option>
                <option value="-title">Title Z-A</option>
                <option value="salary_min">Salary: Low to High</option>
                <option value="-salary_min">Salary: High to Low</option>
              </select>
            </div>
          </div>
          {jobs.length > 0 && (
            <div className="results-count">
              {jobs.length} jobs found
            </div>
          )}
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading jobs...</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <p>{typeof error === 'string' ? error : 'Failed to load jobs'}</p>
            <button onClick={refreshJobs} className="retry-btn">Try Again</button>
          </div>
        ) : (
          <div className="joblistings-list">
            {jobs.length === 0 ? (
              <div className="no-jobs">
                <h3>No jobs found</h3>
                <p>Try adjusting your search criteria or filters</p>
              </div>
            ) : (
              <>
                {jobs.map(job => (
                  <div 
                    className="job-card" 
                    key={job.id}
                    onClick={() => handleJobClick(job)}
                  >
                    <div className="job-card-header">
                      <div className="job-info">
                        <h4 className="job-title">{job.title}</h4>
                        <p className="company-location">
                          <span className="company">{job.company?.name || 'Unknown Company'}</span>
                          <span className="separator">&bull;</span>
                          <span className="location">{job.location?.full_address || job.location?.city || 'Unknown Location'}</span>
                        </p>
                      </div>
                      <div className="job-actions">
                        <button 
                          className={`save-btn ${job.is_saved ? 'saved' : ''}`}
                          onClick={(e) => handleSaveJob(e, job)}
                          title={job.is_saved ? "Remove from saved jobs" : "Save this job"}
                        >
                          {job.is_saved ? '♥' : '♡'}
                        </button>
                        <button 
                          className={`apply-btn ${job.is_applied ? 'applied' : ''}`}
                          onClick={(e) => handleApply(e, job)}
                          title={job.is_applied ? "Already applied" : "Apply to this job"}
                          disabled={job.is_applied}
                        >
                          {job.is_applied ? 'Applied' : 'Apply'}
                        </button>
                      </div>
                    </div>
                    
                    <div className="job-card-body">
                      {job.description && (
                        <p className="job-description">
                          {job.description.length > 150 
                            ? `${job.description.substring(0, 150)}...` 
                            : job.description}
                        </p>
                      )}
                    </div>

                    <div className="job-card-footer">
                      <div className="job-meta">
                        <span className="job-type">
                          {job.job_type || job.contract_type || 'Full-time'}
                        </span>
                        {job.remote_type && (
                          <span className="remote-type">
                            {job.remote_type.charAt(0).toUpperCase() + job.remote_type.slice(1)}
                          </span>
                        )}
                        {job.experience_level && (
                          <span className="experience-level">
                            {job.experience_level.charAt(0).toUpperCase() + job.experience_level.slice(1)}
                          </span>
                        )}
                      </div>
                      <div className="job-salary-date">
                        {(job.salary_min || job.salary_max) && (
                          <span className="salary">
                            {job.salary_min && job.salary_max 
                              ? `$${parseInt(job.salary_min).toLocaleString()} - $${parseInt(job.salary_max).toLocaleString()}`
                              : job.salary_min 
                              ? `From $${parseInt(job.salary_min).toLocaleString()}`
                              : `Up to $${parseInt(job.salary_max).toLocaleString()}`}
                            {job.salary_currency && job.salary_currency !== 'USD' && ` ${job.salary_currency}`}
                          </span>
                        )}
                        <span className="posted-date">
                          {new Date(job.posted_date || job.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Pagination or Load More */}
                {hasMore && (
                  <div className="load-more-container">
                    <button 
                      className="load-more-btn" 
                      onClick={handleLoadMore}
                      disabled={loading}
                    >
                      {loading ? 'Loading...' : 'Load More Jobs'}
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default JobListings; 