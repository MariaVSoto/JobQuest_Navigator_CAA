import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { JobContext } from '../context/JobContext';
import unifiedJobService from '../services/unifiedJobService';
import './JobDetails.css';

const JobDetails = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { saveJob, unsaveJob } = React.useContext(JobContext);
  const [job, setJob] = useState(null);
  const [isSaved, setIsSaved] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    const fetchJobDetails = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Fetch job details from Django backend
        const jobData = await unifiedJobService.getJob(jobId);
        
        if (jobData) {
          const transformedJob = jobData // jobService.transformJobData(jobData);
          setJob(transformedJob);
          setIsSaved(jobData.is_saved || false);
        } else {
          setError('Job not found');
          setTimeout(() => navigate('/jobs'), 2000);
        }
      } catch (err) {
        console.error('Error fetching job details:', err);
        setError('Failed to load job details');
        setTimeout(() => navigate('/jobs'), 2000);
      } finally {
        setIsLoading(false);
      }
    };

    if (jobId) {
      fetchJobDetails();
    }
  }, [jobId, navigate]);

  const handleSaveJob = async () => {
    try {
      setActionLoading(true);
      
      if (isSaved) {
        // Unsave the job
        const result = await unsaveJob(jobId);
        if (result.success) {
          setIsSaved(false);
        }
      } else {
        // Save the job
        const result = await saveJob(jobId);
        if (result.success) {
          setIsSaved(true);
        }
      }
    } catch (err) {
      console.error('Error saving/unsaving job:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleApply = () => {
    navigate(`/apply/${jobId}`);
  };

  if (isLoading) {
    return (
      <div className="job-details-container">
        <div className="loading">Loading job details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="job-details-container">
        <div className="error">{error}</div>
        <button onClick={() => navigate('/jobs')}>Back to Jobs</button>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="job-details-container">
        <div className="error">Job not found</div>
        <button onClick={() => navigate('/jobs')}>Back to Jobs</button>
      </div>
    );
  }

  return (
    <div className="job-details-container">
      {/* Back Navigation */}
      <div className="navigation-header">
        <button onClick={() => navigate('/jobs')} className="back-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="15,18 9,12 15,6"></polyline>
          </svg>
          Back to Jobs
        </button>
      </div>

      {/* Job Header */}
      <div className="job-header">
        <div className="job-header-content">
          <div className="job-title-section">
            <h1 className="job-title">{job.title}</h1>
            <div className="company-info">
              <h2 className="company-name">{job.company?.name || job.company?.display_name || 'Unknown Company'}</h2>
              <div className="location-info">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
                <span>
                  {job.location?.city || 'Unknown City'}, {job.location?.country || 'Unknown Country'}
                </span>
              </div>
            </div>
            <div className="job-meta-tags">
              <span className="meta-tag posted-date">
                Posted {new Date(job.posted_date || job.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </span>
            </div>
          </div>
          <div className="job-actions">
            <button 
              className={`save-btn ${isSaved ? 'saved' : ''}`}
              onClick={handleSaveJob}
              disabled={actionLoading}
              title={isSaved ? "Remove from saved jobs" : "Save this job"}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill={isSaved ? "currentColor" : "none"} stroke="currentColor">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
              </svg>
              {actionLoading ? 'Loading...' : (isSaved ? 'Saved' : 'Save Job')}
            </button>
            <button className="apply-btn" onClick={handleApply}>
              Apply Now
            </button>
          </div>
        </div>
      </div>

      {/* Job Content */}
      <div className="job-content">
        <div className="content-grid">
          {/* Main Content */}
          <div className="main-content">
            {/* Job Overview */}
            <section className="content-section job-overview">
              <h3>Job Overview</h3>
              <div className="overview-grid">
                {job.job_type && (
                  <div className="overview-item">
                    <span className="label">Job Type</span>
                    <span className="value">{job.job_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  </div>
                )}
                {job.contract_type && (
                  <div className="overview-item">
                    <span className="label">Contract Type</span>
                    <span className="value">{job.contract_type.replace(/\b\w/g, l => l.toUpperCase())}</span>
                  </div>
                )}
                {job.experience_level && (
                  <div className="overview-item">
                    <span className="label">Experience Level</span>
                    <span className="value">{job.experience_level.replace(/\b\w/g, l => l.toUpperCase())}</span>
                  </div>
                )}
                {job.remote_type && (
                  <div className="overview-item">
                    <span className="label">Work Arrangement</span>
                    <span className="value">{job.remote_type.replace('_', '-').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  </div>
                )}
                {(job.salary_min || job.salary_max) && (
                  <div className="overview-item">
                    <span className="label">Salary</span>
                    <span className="value salary">
                      {job.salary_min && job.salary_max 
                        ? `$${parseInt(job.salary_min).toLocaleString()} - $${parseInt(job.salary_max).toLocaleString()}`
                        : job.salary_min 
                        ? `From $${parseInt(job.salary_min).toLocaleString()}`
                        : job.salary_max
                        ? `Up to $${parseInt(job.salary_max).toLocaleString()}`
                        : 'Not specified'}
                      {job.salary_currency && job.salary_currency !== 'USD' && ` ${job.salary_currency}`}
                      {job.salary_period && job.salary_period !== 'yearly' && ` (${job.salary_period})`}
                    </span>
                  </div>
                )}
                {job.category && (
                  <div className="overview-item">
                    <span className="label">Category</span>
                    <span className="value">{job.category.name || job.category}</span>
                  </div>
                )}
                {job.source && (
                  <div className="overview-item">
                    <span className="label">Source</span>
                    <span className="value">{job.source.charAt(0).toUpperCase() + job.source.slice(1)}</span>
                  </div>
                )}
                {job.external_url && (
                  <div className="overview-item full-width">
                    <span className="label">External Link</span>
                    <span className="value">
                      <a href={job.external_url} target="_blank" rel="noopener noreferrer" className="external-link">
                        View Original Posting
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                          <polyline points="15,3 21,3 21,9"></polyline>
                          <line x1="10" y1="14" x2="21" y2="3"></line>
                        </svg>
                      </a>
                    </span>
                  </div>
                )}
              </div>
            </section>

            {/* Job Description */}
            <section className="content-section job-description">
              <h3>Job Description</h3>
              <div className="description-content">
                {job.description ? (
                  <div dangerouslySetInnerHTML={{ 
                    __html: job.description.replace(/\n/g, '<br>') 
                  }} />
                ) : (
                  <p className="no-content">No description provided.</p>
                )}
              </div>
            </section>

            {/* Requirements */}
            {job.requirements && (
              <section className="content-section job-requirements">
                <h3>Requirements</h3>
                <div className="requirements-content">
                  <div dangerouslySetInnerHTML={{ 
                    __html: job.requirements.replace(/\n/g, '<br>') 
                  }} />
                </div>
              </section>
            )}

            {/* Benefits */}
            {job.benefits && (
              <section className="content-section job-benefits">
                <h3>Benefits</h3>
                <div className="benefits-content">
                  <div dangerouslySetInnerHTML={{ 
                    __html: job.benefits.replace(/\n/g, '<br>') 
                  }} />
                </div>
              </section>
            )}

            {/* Required Skills */}
            {job.required_skills && job.required_skills.length > 0 && (
              <section className="content-section job-skills">
                <h3>Required Skills</h3>
                <div className="skills-grid">
                  {job.required_skills.map((skillObj, index) => (
                    <div key={index} className="skill-item">
                      <span className="skill-name">
                        {skillObj.skill?.name || skillObj.name || skillObj}
                      </span>
                      {skillObj.is_required && <span className="required-badge">Required</span>}
                      {skillObj.proficiency_level && (
                        <span className="proficiency-level">
                          {skillObj.proficiency_level.charAt(0).toUpperCase() + skillObj.proficiency_level.slice(1)}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>

          {/* Sidebar */}
          <aside className="job-sidebar">
            {/* Company Information */}
            <section className="sidebar-section company-info">
              <h3>Company Information</h3>
              <div className="company-details">
                <div className="company-name-section">
                  <h4>{job.company?.name || job.company?.display_name || 'Unknown Company'}</h4>
                  {job.company?.description && (
                    <p className="company-description">{job.company.description}</p>
                  )}
                </div>
                
                <div className="company-stats">
                  {job.company?.industry && (
                    <div className="stat-item">
                      <span className="label">Industry</span>
                      <span className="value">{job.company.industry}</span>
                    </div>
                  )}
                  {job.company?.company_size && (
                    <div className="stat-item">
                      <span className="label">Company Size</span>
                      <span className="value">{job.company.company_size}</span>
                    </div>
                  )}
                  {job.company?.founded_year && (
                    <div className="stat-item">
                      <span className="label">Founded</span>
                      <span className="value">{job.company.founded_year}</span>
                    </div>
                  )}
                  {job.company?.website && (
                    <div className="stat-item">
                      <span className="label">Website</span>
                      <span className="value">
                        <a href={job.company.website} target="_blank" rel="noopener noreferrer" className="company-website">
                          Visit Website
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                            <polyline points="15,3 21,3 21,9"></polyline>
                            <line x1="10" y1="14" x2="21" y2="3"></line>
                          </svg>
                        </a>
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </section>

            {/* Job Metadata */}
            <section className="sidebar-section job-metadata">
              <h3>Job Details</h3>
              <div className="metadata-list">
                <div className="metadata-item">
                  <span className="label">Job ID</span>
                  <span className="value">{job.id || job.external_id || 'N/A'}</span>
                </div>
                {job.created_at && (
                  <div className="metadata-item">
                    <span className="label">Listed</span>
                    <span className="value">
                      {new Date(job.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                )}
                {job.expires_date && (
                  <div className="metadata-item">
                    <span className="label">Expires</span>
                    <span className="value">
                      {new Date(job.expires_date).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                )}
                <div className="metadata-item">
                  <span className="label">Status</span>
                  <span className="value">
                    <span className={`status-badge ${job.is_active ? 'active' : 'inactive'}`}>
                      {job.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </span>
                </div>
              </div>
            </section>

            {/* Application CTA */}
            <section className="sidebar-section application-cta">
              <div className="cta-content">
                <h4>Ready to Apply?</h4>
                <p>Take the next step in your career journey.</p>
                <button className="apply-btn-large" onClick={handleApply}>
                  Apply for This Position
                </button>
              </div>
            </section>
          </aside>
        </div>
      </div>
    </div>
  );
};

export default JobDetails; 