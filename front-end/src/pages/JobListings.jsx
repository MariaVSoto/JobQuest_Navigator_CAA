import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { JobContext } from '../context/JobContext';
import './JobListings.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const JobListings = () => {
  const navigate = useNavigate();
  const { jobs, filters, setFilters, setSelectedJob, loading, error } = useContext(JobContext);

  const handleFilterChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleApply = (job) => {
    setSelectedJob(job);
    navigate(`/apply/${job.id || job.__unique_id || job.redirect_url}`);
  };

  return (
    <div className="joblistings-container">
      <aside className="joblistings-sidebar">
        <h3>Filters</h3>
        <label>Location
          <input name="location" type="text" value={filters.location} onChange={handleFilterChange} placeholder="e.g. New York" />
        </label>
        <label>Company
          <input name="company" type="text" value={filters.company} onChange={handleFilterChange} placeholder="e.g. TechCorp" />
        </label>
        <label>Job Type
          <select name="type" value={filters.type} onChange={handleFilterChange}>
            <option value="">All</option>
            <option value="Full-time">Full-time</option>
            <option value="Part-time">Part-time</option>
            <option value="Contract">Contract</option>
          </select>
        </label>
        <label className="remote-checkbox">
          <input name="remote" type="checkbox" checked={filters.remote} onChange={handleFilterChange} /> Remote only
        </label>
      </aside>
      <main className="joblistings-main">
        {/* <img src={logo} alt="JobQuest Logo" className="joblistings-logo" /> */}
        <h1 className="joblistings-title">Job Listings</h1>
        <div className="joblistings-searchbar">
          <input
            name="search"
            type="text"
            value={filters.search}
            onChange={handleFilterChange}
            placeholder="Search job titles..."
          />
        </div>
        {loading ? (
          <div className="no-jobs">Loading jobs...</div>
        ) : error ? (
          <div className="no-jobs">{error}</div>
        ) : (
          <div className="joblistings-list">
            {jobs.length === 0 ? (
              <div className="no-jobs">No jobs found.</div>
            ) : (
              jobs.map(job => (
                <div className="job-card" key={job.id || job.__unique_id || job.redirect_url}>
                  <h4>{job.title}</h4>
                  <p>{job.company?.display_name || 'Unknown Company'} &bull; {job.location?.display_name || 'Unknown Location'}</p>
                  <span className="job-type">{job.contract_type ? job.contract_type.charAt(0).toUpperCase() + job.contract_type.slice(1) : 'N/A'}{job.salary_is_predicted === '1' ? ' • Salary Predicted' : ''}</span>
                  <button className="apply-btn" onClick={() => handleApply(job)}>Apply</button>
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default JobListings; 