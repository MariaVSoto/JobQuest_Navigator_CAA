import React, { useContext, useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { JobContext } from '../context/JobContext';
// JobMapIntegrated removed - using simplified location display only
import './JobListings.css';

const JobListings = () => {
  const navigate = useNavigate();
  
  // Local state for search interface
  const [searchKeyword, setSearchKeyword] = useState('');
  const [cityInput, setCityInput] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('');
  const [showCountryDropdown, setShowCountryDropdown] = useState(false);
  
  // Ref for country dropdown
  const countryDropdownRef = useRef(null);
  
  // Predefined country options
  const countryOptions = [
    { value: '', label: 'Any Country' },
    { value: 'United States', label: 'United States' },
    { value: 'Canada', label: 'Canada' },
    { value: 'United Kingdom', label: 'United Kingdom' },
    { value: 'Australia', label: 'Australia' },
    { value: 'France', label: 'France' },
    { value: 'Germany', label: 'Germany' },
    { value: 'Italy', label: 'Italy' }
  ];
  
  // Use Job Context
  const { 
    jobs, 
    setJobs,
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

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Only handle clicks outside the country dropdown, don't interfere with navbar dropdowns
      if (countryDropdownRef.current && 
          !countryDropdownRef.current.contains(event.target) &&
          !event.target.closest('.nav-dropdown, .navbar-dropdown-menu, .user-dropdown, .navbar-nav')) {
        setShowCountryDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);


  // Handle search functionality
  const handleSearch = () => {
    // Combine city and country for location search
    const locationString = [cityInput, selectedCountry].filter(Boolean).join(', ');
    
    const searchFilters = {
      search: searchKeyword,
      location: locationString,
      // Reset other filters for clean search
      company: '',
      type: '',
      experience_level: '',
      remote_type: '',
      salary_min: '',
      sort: '',
    };
    setFilters(searchFilters);
  };

  // Handle country selection
  const handleCountrySelect = (option) => {
    setSelectedCountry(option.value);
    setShowCountryDropdown(false);
  };


  // Handle Enter key press in search input
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
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
        // Update job locally immediately for better UX
        const updatedJobs = jobs.map(j => 
          j.id === job.id ? { ...j, is_saved: false } : j
        );
        // Update the jobs state directly in the context
        setJobs(updatedJobs);
      }
    } else {
      const result = await contextSaveJob(job.id);
      if (result.success) {
        // Update job locally immediately for better UX
        const updatedJobs = jobs.map(j => 
          j.id === job.id ? { ...j, is_saved: true } : j
        );
        // Update the jobs state directly in the context
        setJobs(updatedJobs);
      }
    }
  };

  const handleLoadMore = () => {
    if (!hasMore || loading) return;
    loadMoreJobs();
  };

  return (
    <div className="joblistings-container">
      {/* Search Section */}
      <div className="search-section">
        <div className="search-header">
          <h1>Find Your Perfect Job</h1>
          <p className="search-subtitle">Discover opportunities that match your skills and aspirations</p>
        </div>
        
        <div className="search-card card">
          <div className="search-form">
            {/* Search Input Field */}
            <div className="search-field">
              <label className="field-label">What</label>
              <div className="input-group">
                <span className="input-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                  </svg>
                </span>
                <input
                  type="text"
                  className="form-input"
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Job title, keywords, or company"
                />
              </div>
            </div>

            {/* Location Input */}
            <div className="search-field">
              <label className="field-label">Where</label>
              <div className="input-group">
                <span className="input-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                    <circle cx="12" cy="10" r="3"></circle>
                  </svg>
                </span>
                <input
                  type="text"
                  className="form-input"
                  value={cityInput}
                  onChange={(e) => setCityInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="City or location"
                />
              </div>
            </div>

            {/* Country Selector */}
            <div className="search-field">
              <label className="field-label">Country</label>
              <div className="select-container" ref={countryDropdownRef}>
                <div 
                  className="form-select"
                  onClick={() => setShowCountryDropdown(!showCountryDropdown)}
                >
                  <span>{selectedCountry || 'Any Country'}</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="6,9 12,15 18,9"></polyline>
                  </svg>
                </div>
                
                {showCountryDropdown && (
                  <div className="select-dropdown">
                    {countryOptions.map((option, index) => (
                      <button
                        key={index}
                        className="select-option"
                        onClick={() => handleCountrySelect(option)}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Search Button */}
            <div className="search-action">
              <button 
                className="btn btn-primary search-btn"
                onClick={handleSearch}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <svg width="16" height="16" className="animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M21 12a9 9 0 11-6.219-8.56"/>
                    </svg>
                    Searching...
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="11" cy="11" r="8"></circle>
                      <path d="m21 21-4.35-4.35"></path>
                    </svg>
                    Search Jobs
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Map section removed - focusing on user input jobs */}

      {/* Results Section */}
      <main className="joblistings-main">
        <div className="results-header">
          <div className="results-info">
            {jobs.length > 0 && (
              <div className="results-count">
                Found {jobs.length} jobs
              </div>
            )}
          </div>
          <div className="results-actions">
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/create-job')}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Add Job Position
            </button>
          </div>
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
                <div className="no-jobs-icon">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                  </svg>
                </div>
                <h3>No jobs found</h3>
                <p>Try adjusting your search criteria or browse all available positions</p>
                <div className="no-jobs-actions">
                  <button onClick={() => setFilters({search: '', location: '', company: '', type: '', experience_level: '', remote_type: '', salary_min: '', sort: ''})} className="clear-filters-btn">
                    View All Jobs
                  </button>
                  <button 
                    onClick={() => navigate('/create-job')} 
                    className="btn btn-primary"
                  >
                    Add Job Position
                  </button>
                </div>
              </div>
            ) : (
              <>
                {jobs.map(job => (
                  <article 
                    className="job-card card" 
                    key={job.id}
                    onClick={() => handleJobClick(job)}
                  >
                    <div className="card-body">
                      <div className="job-header">
                        <div className="job-company-logo">
                          <span>{job.company?.name?.[0] || 'C'}</span>
                        </div>
                        <div className="job-meta">
                          <div className="job-posted">
                            {new Date(job.posted_date || job.created_at).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric'
                            })}
                          </div>
                          <button 
                            className={`save-btn ${job.is_saved ? 'saved' : ''}`}
                            onClick={(e) => handleSaveJob(e, job)}
                            title={job.is_saved ? "Remove from saved jobs" : "Save this job"}
                          >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill={job.is_saved ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                            </svg>
                          </button>
                        </div>
                      </div>

                      <div className="job-content">
                        <h3 className="job-title">{job.title}</h3>
                        <div className="job-company">{job.company?.name || 'Unknown Company'}</div>
                        <div className="job-location">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                            <circle cx="12" cy="10" r="3"></circle>
                          </svg>
                          <span>{job.location?.text || job.location?.display_name || 'Remote/Flexible'}</span>
                        </div>
                        
                        {job.description && (
                          <p className="job-description">
                            {job.description.length > 120 
                              ? `${job.description.substring(0, 120)}...` 
                              : job.description
                            }
                          </p>
                        )}

                        <div className="job-tags">
                          {job.employment_type && (
                            <span className="job-tag job-type">{job.employment_type}</span>
                          )}
                          {job.experience_level && (
                            <span className="job-tag job-level">{job.experience_level}</span>
                          )}
                          {job.salary_min && job.salary_max && (
                            <span className="job-tag job-salary">
                              ${job.salary_min}k - ${job.salary_max}k
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="job-actions">
                        <button 
                          className={`btn btn-outline ${job.is_applied ? 'btn-secondary' : ''}`}
                          onClick={(e) => handleApply(e, job)}
                          disabled={job.is_applied}
                        >
                          {job.is_applied ? (
                            <>
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <polyline points="20,6 9,17 4,12"></polyline>
                              </svg>
                              Applied
                            </>
                          ) : (
                            'Apply Now'
                          )}
                        </button>
                        <button 
                          className="btn btn-secondary btn-sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleJobClick(job);
                          }}
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                    
                    {/* Hover indicator */}
                    <div className="job-card-indicator">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="9,18 15,12 9,6"></polyline>
                      </svg>
                    </div>
                  </article>
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