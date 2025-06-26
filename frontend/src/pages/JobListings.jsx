import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@apollo/client';
import { GET_JOBS } from '../graphql/queries';
import { SAVE_JOB, UNSAVE_JOB, APPLY_TO_JOB } from '../graphql/mutations';
import './JobListings.css';

const JOBS_PER_PAGE = 20;

const JobListings = () => {
  const navigate = useNavigate();
  
  // Local state for filters
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    company: '',
    type: '',
    experience_level: '',
    remote_type: '',
    salary_min: '',
    sort: ''
  });

  // GraphQL query with filters
  const { loading, error, data, fetchMore, refetch } = useQuery(GET_JOBS, {
    variables: {
      limit: JOBS_PER_PAGE,
      offset: 0,
      search: filters.search || undefined,
      location: filters.location || undefined,
      company: filters.company || undefined,
      jobType: filters.type || undefined,
      experienceLevel: filters.experience_level || undefined,
      remoteType: filters.remote_type || undefined,
    },
    notifyOnNetworkStatusChange: true,
  });

  // Job mutations
  const [saveJob] = useMutation(SAVE_JOB, {
    update(cache, { data: { saveJob } }) {
      if (!saveJob.success) return;
      
      // Update the job's isSaved field in cache
      const jobId = saveJob.savedJob.job.id;
      cache.modify({
        id: cache.identify({ __typename: 'JobType', id: jobId }),
        fields: {
          isSaved: () => true,
        },
      });
    }
  });

  const [unsaveJob] = useMutation(UNSAVE_JOB, {
    update(cache, { data: { unsaveJob } }) {
      if (!unsaveJob.success) return;
      
      cache.modify({
        id: cache.identify({ __typename: 'JobType', id: unsaveJob.jobId }),
        fields: {
          isSaved: () => false,
        },
      });
    }
  });

  const [applyToJob] = useMutation(APPLY_TO_JOB, {
    update(cache, { data: { applyToJob } }) {
      if (!applyToJob.success) return;
      
      const jobId = applyToJob.application.job.id;
      cache.modify({
        id: cache.identify({ __typename: 'JobType', id: jobId }),
        fields: {
          isApplied: () => true,
        },
      });
    }
  });

  const jobs = data?.jobs || [];
  const hasMore = jobs.length % JOBS_PER_PAGE === 0 && jobs.length > 0;

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

  const handleSaveJob = (e, job) => {
    e.stopPropagation();
    if (job.isSaved) {
      unsaveJob({ 
        variables: { jobId: job.id },
        optimisticResponse: {
          unsaveJob: {
            __typename: 'UnsaveJobMutation',
            success: true,
            jobId: job.id,
            errors: []
          }
        }
      });
    } else {
      saveJob({ 
        variables: { jobId: job.id },
        optimisticResponse: {
          saveJob: {
            __typename: 'SaveJobMutation',
            success: true,
            errors: [],
            savedJob: {
              __typename: 'SavedJobType',
              id: -1,
              job: {
                __typename: 'JobType',
                id: job.id,
                isSaved: true
              }
            }
          }
        }
      });
    }
  };

  const handleLoadMore = () => {
    if (!hasMore || loading) return;

    fetchMore({
      variables: {
        offset: jobs.length,
      },
      updateQuery: (prevResult, { fetchMoreResult }) => {
        if (!fetchMoreResult || fetchMoreResult.jobs.length === 0) {
          return prevResult;
        }
        
        return {
          jobs: [...prevResult.jobs, ...fetchMoreResult.jobs],
        };
      },
    });
  };

  const refreshJobs = () => {
    refetch();
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
            <p>{error}</p>
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
                          <span className="location">{job.location?.name || job.location?.city || 'Unknown Location'}</span>
                        </p>
                      </div>
                      <div className="job-actions">
                        <button 
                          className={`save-btn ${job.isSaved ? 'saved' : ''}`}
                          onClick={(e) => handleSaveJob(e, job)}
                          title={job.isSaved ? "Remove from saved jobs" : "Save this job"}
                        >
                          {job.isSaved ? '♥' : '♡'}
                        </button>
                        <button 
                          className={`apply-btn ${job.isApplied ? 'applied' : ''}`}
                          onClick={(e) => handleApply(e, job)}
                          title={job.isApplied ? "Already applied" : "Apply to this job"}
                          disabled={job.isApplied}
                        >
                          {job.isApplied ? 'Applied' : 'Apply'}
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
                        {(job.salaryMin || job.salaryMax) && (
                          <span className="salary">
                            {job.salaryMin && job.salaryMax 
                              ? `$${parseInt(job.salaryMin).toLocaleString()} - $${parseInt(job.salaryMax).toLocaleString()}`
                              : job.salaryMin 
                              ? `From $${parseInt(job.salaryMin).toLocaleString()}`
                              : `Up to $${parseInt(job.salaryMax).toLocaleString()}`}
                            {job.salaryCurrency && job.salaryCurrency !== 'USD' && ` ${job.salaryCurrency}`}
                          </span>
                        )}
                        <span className="posted-date">
                          {new Date(job.postedDate || job.createdAt).toLocaleDateString()}
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