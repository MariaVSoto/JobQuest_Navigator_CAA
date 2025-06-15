import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { JobContext } from '../context/JobContext';
import './JobDetails.css';

const JobDetails = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { jobs } = React.useContext(JobContext);
  const [job, setJob] = useState(null);
  const [isSaved, setIsSaved] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // In a real application, this would be an API call
    const fetchJobDetails = async () => {
      setIsLoading(true);
      try {
        // Simulating API call
        const foundJob = jobs.find(j => j.id === jobId);
        if (foundJob) {
          setJob(foundJob);
        } else {
          // Handle job not found
          navigate('/jobs');
        }
      } catch (error) {
        console.error('Error fetching job details:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchJobDetails();
  }, [jobId, jobs, navigate]);

  const handleSaveJob = () => {
    setIsSaved(!isSaved);
    // Here we would typically make an API call to save/unsave the job
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

  if (!job) {
    return (
      <div className="job-details-container">
        <div className="error">Job not found</div>
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
              {job.salary_is_predicted === '1' ? 'Salary: Predicted' : job.salary || 'Salary not specified'}
            </span>
            <span className="posted-date">Posted {new Date(job.created).toLocaleDateString()}</span>
          </div>
        </div>
        <div className="job-actions">
          <button 
            className={`save-job-btn ${isSaved ? 'saved' : ''}`}
            onClick={handleSaveJob}
          >
            {isSaved ? 'Saved' : 'Save Job'}
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

          <section className="job-requirements">
            <h3>Requirements</h3>
            <ul>
              {job.requirements?.map((req, index) => (
                <li key={index}>{req}</li>
              )) || <li>No specific requirements listed.</li>}
            </ul>
          </section>

          <section className="job-benefits">
            <h3>Benefits</h3>
            <ul>
              {job.benefits?.map((benefit, index) => (
                <li key={index}>{benefit}</li>
              )) || <li>No benefits listed.</li>}
            </ul>
          </section>
        </div>

        <aside className="job-sidebar">
          <section className="company-overview">
            <h3>Company Overview</h3>
            <p>{job.company?.description || 'No company description available.'}</p>
            <div className="company-stats">
              <div className="stat">
                <span className="label">Company Size</span>
                <span className="value">{job.company?.size || 'Not specified'}</span>
              </div>
              <div className="stat">
                <span className="label">Industry</span>
                <span className="value">{job.company?.industry || 'Not specified'}</span>
              </div>
              <div className="stat">
                <span className="label">Founded</span>
                <span className="value">{job.company?.founded || 'Not specified'}</span>
              </div>
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