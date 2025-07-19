import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@apollo/client';
import { gql } from '@apollo/client';
import './CreateJob.css';

const CREATE_USER_JOB = gql`
  mutation CreateUserJob($input: CreateUserJobInput!) {
    createUserJob(input: $input) {
      success
      errors
      job {
        id
        title
        company {
          name
        }
        locationText
        description
        salaryMin
        salaryMax
        jobType
        remoteType
      }
    }
  }
`;

const CreateJob = () => {
  const navigate = useNavigate();
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

  const [createJob, { loading, error }] = useMutation(CREATE_USER_JOB);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const { data } = await createJob({
        variables: {
          input: {
            title: formData.title,
            companyName: formData.companyName,
            locationText: formData.locationText,
            description: formData.description,
            requirements: formData.requirements || null,
            benefits: formData.benefits || null,
            salaryMin: formData.salaryMin ? parseFloat(formData.salaryMin) : null,
            salaryMax: formData.salaryMax ? parseFloat(formData.salaryMax) : null,
            salaryCurrency: formData.salaryCurrency,
            salaryPeriod: formData.salaryPeriod,
            jobType: formData.jobType,
            contractType: formData.contractType,
            experienceLevel: formData.experienceLevel || null,
            remoteType: formData.remoteType
          }
        }
      });

      if (data.createUserJob.success) {
        // Redirect to job details or jobs list
        navigate('/jobs');
      } else {
        console.error('Failed to create job:', data.createUserJob.errors);
      }
    } catch (err) {
      console.error('Error creating job:', err);
    }
  };

  return (
    <div className="create-job-container">
      <div className="create-job-header">
        <h1>Add a Job Position</h1>
        <p>Create a job position for skills assessment or application tracking</p>
      </div>

      <form className="create-job-form" onSubmit={handleSubmit}>
        <div className="form-section">
          <h3>Basic Information</h3>
          
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
              placeholder="e.g., TechCorp Inc"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="locationText">Location *</label>
            <input
              type="text"
              id="locationText"
              name="locationText"
              value={formData.locationText}
              onChange={handleInputChange}
              placeholder="e.g., Remote, New York NY, or Hybrid"
              required
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Job Details</h3>
          
          <div className="form-group">
            <label htmlFor="description">Job Description *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe the role, responsibilities, and what you're looking for..."
              rows="6"
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
              placeholder="List required skills, experience, and qualifications..."
              rows="4"
            />
          </div>

          <div className="form-group">
            <label htmlFor="benefits">Benefits</label>
            <textarea
              id="benefits"
              name="benefits"
              value={formData.benefits}
              onChange={handleInputChange}
              placeholder="List benefits, perks, and compensation details..."
              rows="4"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Employment Details</h3>
          
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
                <option value="freelance">Freelance</option>
                <option value="internship">Internship</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="remoteType">Work Style</label>
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

          <div className="form-row">
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
                <option value="apprenticeship">Apprenticeship</option>
                <option value="volunteer">Volunteer</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="experienceLevel">Experience Level</label>
              <select
                id="experienceLevel"
                name="experienceLevel"
                value={formData.experienceLevel}
                onChange={handleInputChange}
              >
                <option value="">Select level</option>
                <option value="entry">Entry Level</option>
                <option value="junior">Junior</option>
                <option value="mid">Mid Level</option>
                <option value="senior">Senior</option>
                <option value="lead">Lead</option>
                <option value="manager">Manager</option>
                <option value="director">Director</option>
                <option value="executive">Executive</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Salary Information (Optional)</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="salaryMin">Minimum Salary</label>
              <input
                type="number"
                id="salaryMin"
                name="salaryMin"
                value={formData.salaryMin}
                onChange={handleInputChange}
                placeholder="50000"
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
                placeholder="80000"
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
            onClick={() => navigate('/jobs')}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Creating Job...' : 'Create Job Position'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            Failed to create job: {error.message}
          </div>
        )}
      </form>
    </div>
  );
};

export default CreateJob;