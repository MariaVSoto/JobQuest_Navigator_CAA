import React, { useState, useContext, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { JobContext } from '../context/JobContext';
import { useAuth } from '../context/AuthContext';
import unifiedJobService from '../services/unifiedJobService';
import './JobApplicationForm.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const JobApplicationForm = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { applyToJob } = useContext(JobContext);
  
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  
  const [formData, setFormData] = useState({
    cover_letter: '',
    notes: ''
  });

  // Load job details
  useEffect(() => {
    const loadJob = async () => {
      try {
        setLoading(true);
        const jobData = await unifiedJobService.getJob(jobId);
        if (jobData) {
          const transformedJob = jobData // jobService.transformJobData(jobData);
          setJob(transformedJob);
        } else {
          setError('Job not found');
          setTimeout(() => navigate('/jobs'), 2000);
        }
      } catch (err) {
        console.error('Error loading job:', err);
        setError('Failed to load job details');
        setTimeout(() => navigate('/jobs'), 2000);
      } finally {
        setLoading(false);
      }
    };

    if (jobId) {
      loadJob();
    }
  }, [jobId, navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!job) return;
    
    try {
      setSubmitting(true);
      setError(null);
      
      const applicationData = {
        cover_letter: formData.cover_letter,
        notes: formData.notes
      };
      
      const result = await applyToJob(jobId, applicationData);
      
      if (result.success) {
        setSubmitted(true);
        setTimeout(() => {
          navigate('/application-history');
        }, 3000);
      } else {
        setError(result.error || 'Failed to submit application');
      }
    } catch (err) {
      console.error('Application submission error:', err);
      setError('An error occurred while submitting your application');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="application-container">
        <div className="loading">Loading job details...</div>
      </div>
    );
  }

  if (error && !job) {
    return (
      <div className="application-container">
        <div className="error-state">
          <p>{error}</p>
          <button onClick={() => navigate('/jobs')}>Back to Jobs</button>
        </div>
      </div>
    );
  }

  return (
    <div className="application-container">
      <div className="application-box">
        <h1 className="application-title">Job Application</h1>
        
        {job && (
          <div className="application-jobinfo">
            <div className="job-details">
              <h2>{job.title}</h2>
              <h3>{job.company?.display_name || job.company?.name}</h3>
              <p className="location">{job.location?.display_name}</p>
              {job.salary_min && job.salary_max && (
                <p className="salary">
                  ${parseInt(job.salary_min).toLocaleString()} - ${parseInt(job.salary_max).toLocaleString()}
                </p>
              )}
            </div>
            <div className="job-type-info">
              <span className="job-type">{job.job_type || job.contract_type}</span>
              {job.remote_type && (
                <span className="remote-type">{job.remote_type}</span>
              )}
            </div>
          </div>
        )}

        {submitted ? (
          <div className="application-success">
            <h3>Application Submitted Successfully!</h3>
            <p>Thank you for your interest. We'll review your application and get back to you soon.</p>
            <p>Redirecting to your application history...</p>
          </div>
        ) : (
          <>
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
            
            <form className="application-form" onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="applicant-info">Applicant Information</label>
                <div className="applicant-info">
                  <p><strong>Name:</strong> {user?.full_name || 'Not provided'}</p>
                  <p><strong>Email:</strong> {user?.email}</p>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="cover_letter">Cover Letter</label>
                <textarea
                  id="cover_letter"
                  name="cover_letter"
                  value={formData.cover_letter}
                  onChange={handleInputChange}
                  rows="8"
                  placeholder="Please tell us why you're interested in this position and how your skills match the requirements..."
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="notes">Additional Notes (Optional)</label>
                <textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleInputChange}
                  rows="4"
                  placeholder="Any additional information you'd like to share..."
                />
              </div>

              <div className="form-actions">
                <button 
                  type="button" 
                  className="cancel-btn"
                  onClick={() => navigate(`/jobs/${jobId}`)}
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="application-btn"
                  disabled={submitting}
                >
                  {submitting ? 'Submitting...' : 'Submit Application'}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default JobApplicationForm; 