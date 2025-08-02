import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import unifiedJobService from '../services/unifiedJobService';
import './CreateJob.css'; // Reuse the same CSS

const EditJob = () => {
  const navigate = useNavigate();
  const { jobId } = useParams();
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    companyName: '',
    locationText: '',
    description: '',
    requirements: '',
    benefits: '',
    salaryMin: '',
    salaryMax: '',
    salaryCurrency: 'USD',
    salaryPeriod: 'yearly',
    jobType: 'full_time',
    contractType: 'permanent',
    experienceLevel: '',
    remoteType: 'on_site'
  });

  useEffect(() => {
    fetchJobData();
  }, [jobId]);

  const fetchJobData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch the job data to pre-populate the form
      const job = await unifiedJobService.getJobById(jobId);
      
      if (job) {
        setFormData({
          title: job.title || '',
          companyName: job.company?.name || '',
          locationText: job.location_text || job.locationText || '',
          description: job.description || '',
          requirements: job.requirements || '',
          benefits: job.benefits || '',
          salaryMin: job.salary_min || job.salaryMin || '',
          salaryMax: job.salary_max || job.salaryMax || '',
          salaryCurrency: job.salary_currency || job.salaryCurrency || 'USD',
          salaryPeriod: job.salary_period || job.salaryPeriod || 'yearly',
          jobType: job.job_type || job.jobType || 'full_time',
          contractType: job.contract_type || job.contractType || 'permanent',
          experienceLevel: job.experience_level || job.experienceLevel || '',
          remoteType: job.remote_type || job.remoteType || 'on_site'
        });
      } else {
        setError('Job not found');
      }
    } catch (err) {
      console.error('Error fetching job data:', err);
      setError('Failed to load job data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      // Validate required fields
      if (!formData.title.trim()) {
        throw new Error('Job title is required');
      }
      if (!formData.companyName.trim()) {
        throw new Error('Company name is required');
      }
      if (!formData.description.trim()) {
        throw new Error('Job description is required');
      }

      // Update the job
      await unifiedJobService.updateJob(jobId, formData);
      
      // Navigate back to My Jobs page
      navigate('/my-jobs');
    } catch (err) {
      console.error('Error updating job:', err);
      setError(err.message || 'Failed to update job. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="create-job-container">
        <div className="loading">Loading job data...</div>
      </div>
    );
  }

  return (
    <div className="create-job-container">
      <div className="create-job-header">
        <h1>Edit Job Position</h1>
        <p className="header-subtitle">Update the details for this job posting</p>
      </div>

      <form onSubmit={handleSubmit} className="create-job-form">
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="form-section">
          <h2>Basic Information</h2>
          
          <div className="form-group">
            <label htmlFor="title">Job Title *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="e.g., Senior Frontend Developer"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="companyName">Company Name *</label>
            <input
              type="text"
              id="companyName"
              name="companyName"
              value={formData.companyName}
              onChange={handleInputChange}
              placeholder="e.g., TechCorp Inc."
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="locationText">Location</label>
            <input
              type="text"
              id="locationText"
              name="locationText"
              value={formData.locationText}
              onChange={handleInputChange}
              placeholder="e.g., San Francisco, CA or Remote"
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Job Details</h2>
          
          <div className="form-group">
            <label htmlFor="description">Job Description *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe the role, responsibilities, and what you're looking for..."
              rows={6}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="requirements">Requirements</label>
            <textarea
              id="requirements"
              name="requirements"
              value={formData.requirements}
              onChange={handleInputChange}
              placeholder="List the required skills, qualifications, and experience..."
              rows={4}
            />
          </div>

          <div className="form-group">
            <label htmlFor="benefits">Benefits</label>
            <textarea
              id="benefits"
              name="benefits"
              value={formData.benefits}
              onChange={handleInputChange}
              placeholder="Describe the benefits, perks, and compensation package..."
              rows={3}
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Employment Details</h2>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="jobType">Job Type</label>
              <select
                id="jobType"
                name="jobType"
                value={formData.jobType}
                onChange={handleInputChange}
              >
                <option value="full_time">Full Time</option>
                <option value="part_time">Part Time</option>
                <option value="contract">Contract</option>
                <option value="temporary">Temporary</option>
                <option value="internship">Internship</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="contractType">Contract Type</label>
              <select
                id="contractType"
                name="contractType"
                value={formData.contractType}
                onChange={handleInputChange}
              >
                <option value="permanent">Permanent</option>
                <option value="contract">Contract</option>
                <option value="temporary">Temporary</option>
                <option value="freelance">Freelance</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="experienceLevel">Experience Level</label>
              <select
                id="experienceLevel"
                name="experienceLevel"
                value={formData.experienceLevel}
                onChange={handleInputChange}
              >
                <option value="">Select Experience Level</option>
                <option value="entry">Entry Level</option>
                <option value="junior">Junior</option>
                <option value="mid">Mid Level</option>
                <option value="senior">Senior</option>
                <option value="lead">Lead</option>
                <option value="executive">Executive</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="remoteType">Work Type</label>
              <select
                id="remoteType"
                name="remoteType"
                value={formData.remoteType}
                onChange={handleInputChange}
              >
                <option value="on_site">On-site</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h2>Compensation</h2>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="salaryMin">Minimum Salary</label>
              <input
                type="number"
                id="salaryMin"
                name="salaryMin"
                value={formData.salaryMin}
                onChange={handleInputChange}
                placeholder="e.g., 80000"
                min="0"
              />
            </div>

            <div className="form-group">
              <label htmlFor="salaryMax">Maximum Salary</label>
              <input
                type="number"
                id="salaryMax"
                name="salaryMax"
                value={formData.salaryMax}
                onChange={handleInputChange}
                placeholder="e.g., 120000"
                min="0"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="salaryCurrency">Currency</label>
              <select
                id="salaryCurrency"
                name="salaryCurrency"
                value={formData.salaryCurrency}
                onChange={handleInputChange}
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="CAD">CAD</option>
                <option value="AUD">AUD</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="salaryPeriod">Period</label>
              <select
                id="salaryPeriod"
                name="salaryPeriod"
                value={formData.salaryPeriod}
                onChange={handleInputChange}
              >
                <option value="yearly">Yearly</option>
                <option value="monthly">Monthly</option>
                <option value="weekly">Weekly</option>
                <option value="daily">Daily</option>
                <option value="hourly">Hourly</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={() => navigate('/my-jobs')}
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Updating...' : 'Update Job'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditJob;