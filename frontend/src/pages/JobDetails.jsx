import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { JobContext } from '../context/JobContext';
import jobService from '../services/jobService';
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
        const jobData = await jobService.getJobById(jobId);
        
        if (jobData) {
          const transformedJob = jobService.transformJobData(jobData);
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
      <div className="job-header">
        <div className="company-logo">
          <img src={job.company?.logo_url || 'https://via.placeholder.com/100'} alt={job.company?.display_name} />
        </div>
        <div className="job-title-section">
          <h1>{job.title}</h1>
          <div className="company-info">
            <h2>{job.company?.display_name}</h2>
            <span className="location">
              <i className="fas fa-map-marker-alt"></i>
              {job.location?.display_name || 'Location not specified'}
            </span>
          </div>
          <div className="job-meta">
            <span className="job-type">{job.contract_type || 'Full-time'}</span>
            <span className="salary">
              {job.salary_min && job.salary_max 
                ? `$${parseInt(job.salary_min).toLocaleString()} - $${parseInt(job.salary_max).toLocaleString()}`
                : job.salary_min 
                ? `From $${parseInt(job.salary_min).toLocaleString()}`
                : 'Salary not specified'}
            </span>
            <span className="posted-date">Posted {new Date(job.posted_date || job.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        <div className="job-actions">
          <button 
            className={`save-job-btn ${isSaved ? 'saved' : ''}`}
            onClick={handleSaveJob}
            disabled={actionLoading}
          >
            {actionLoading ? 'Loading...' : (isSaved ? 'Saved' : 'Save Job')}
          </button>
          <button className="apply-btn" onClick={handleApply}>
            Apply Now
          </button>
        </div>
      </div>

      <div className="job-content">
        <div className="main-content">
          <section className="job-description">
            <h3>Job Description</h3>
            <div className="description-content">
              {job.description || 'No description provided.'}
            </div>
          </section>

          {job.requirements && (
            <section className="job-requirements">
              <h3>Requirements</h3>
              <div className="requirements-content">
                {job.requirements}
              </div>
            </section>
          )}

          {job.benefits && (
            <section className="job-benefits">
              <h3>Benefits</h3>
              <div className="benefits-content">
                {job.benefits}
              </div>
            </section>
          )}

          {job.required_skills && job.required_skills.length > 0 && (
            <section className="job-skills">
              <h3>Required Skills</h3>
              <div className="skills-list">
                {job.required_skills.map((skillObj, index) => (
                  <span key={index} className="skill-tag">
                    {skillObj.skill?.name || skillObj.name}
                    {skillObj.is_required && <span className="required">*</span>}
                  </span>
                ))}
              </div>
            </section>
          )}
        </div>

        <aside className="job-sidebar">
          <section className="company-overview">
            <h3>Company Overview</h3>
            <p>{job.company?.description || 'No company description available.'}</p>
            <div className="company-stats">
              <div className="stat">
                <span className="label">Company Size</span>
                <span className="value">{job.company?.company_size || 'Not specified'}</span>
              </div>
              <div className="stat">
                <span className="label">Industry</span>
                <span className="value">{job.company?.industry || 'Not specified'}</span>
              </div>
              <div className="stat">
                <span className="label">Founded</span>
                <span className="value">{job.company?.founded_year || 'Not specified'}</span>
              </div>
              {job.company?.website && (
                <div className="stat">
                  <span className="label">Website</span>
                  <span className="value">
                    <a href={job.company.website} target="_blank" rel="noopener noreferrer">
                      {job.company.website}
                    </a>
                  </span>
                </div>
              )}
            </div>
          </section>

          <section className="similar-jobs">
            <h3>Similar Jobs</h3>
            <div className="similar-jobs-list">
              {/* This would typically be populated with actual similar jobs */}
              <p>Loading similar jobs...</p>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
};

export default JobDetails; 