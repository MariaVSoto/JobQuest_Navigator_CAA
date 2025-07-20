import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation } from '@apollo/client';
import { gql } from '@apollo/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import './UploadJob.css';

const CREATE_USER_JOB = gql`
  mutation CreateJob($input: CreateJobInput!) {
    createJob(input: $input) {
      success
      errors
      jobId
    }
  }
`;

const UploadJob = () => {
  const { user } = useAuth();
  const { showSuccess, showError, showWarning } = useToast();
  const navigate = useNavigate();
  const [method, setMethod] = useState('paste'); // 'paste', 'url', 'file'
  const [jobData, setJobData] = useState({
    title: '',
    company: '',
    location: '',
    description: '',
    requirements: '',
    url: '',
    salary: '',
    type: 'full-time'
  });
  const [jobText, setJobText] = useState('');
  const [jobUrl, setJobUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [parsedJob, setParsedJob] = useState(null);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const [createJob, { loading: createJobLoading }] = useMutation(CREATE_USER_JOB);

  const handleMethodChange = (newMethod) => {
    setMethod(newMethod);
    setParsedJob(null);
    setJobData({
      title: '',
      company: '',
      location: '',
      description: '',
      requirements: '',
      url: '',
      salary: '',
      type: 'full-time'
    });
  };

  const handleTextSubmit = async () => {
    if (!jobText.trim()) {
      showWarning('Please paste the job posting text');
      return;
    }

    setIsProcessing(true);
    setError(null);
    
    try {
      // Simple parsing - extract basic info from the pasted text
      const text = jobText.trim();
      
      // Try to extract title (first line that looks like a job title)
      const lines = text.split('\n').filter(line => line.trim());
      let title = lines[0] || 'Job Position';
      
      // Try to find company name (look for common patterns)
      let company = 'Company Name';
      const companyPatterns = [
        /at\s+([A-Z][A-Za-z\s&.,]+)/i,
        /Company:\s*([A-Za-z\s&.,]+)/i,
        /([A-Z][A-Za-z\s&.,]+)\s+is\s+hiring/i
      ];
      
      for (const pattern of companyPatterns) {
        const match = text.match(pattern);
        if (match && match[1]) {
          company = match[1].trim();
          break;
        }
      }
      
      // Try to find location
      let location = 'Location not specified';
      const locationPatterns = [
        /Location:\s*([A-Za-z\s,.-]+)/i,
        /(Remote|Hybrid|On-site)/i,
        /([A-Za-z\s]+,\s*[A-Z]{2,})/i
      ];
      
      for (const pattern of locationPatterns) {
        const match = text.match(pattern);
        if (match && match[1]) {
          location = match[1].trim();
          break;
        }
      }
      
      // Use the full text as description
      const description = text;
      
      const parsedJob = {
        title: title,
        company: company,
        location: location,
        description: description,
        requirements: [], // Will be filled from description
        skills: [], // Will be extracted later
        salary: 'Not specified',
        type: 'full-time',
        source: 'pasted-text',
        rawText: text
      };
      
      setParsedJob(parsedJob);
      setIsProcessing(false);
    } catch (error) {
      console.error('Error parsing job text:', error);
      setError('Failed to parse job posting. Please check the format and try again.');
      setIsProcessing(false);
    }
  };

  const handleUrlSubmit = async () => {
    if (!jobUrl.trim()) {
      showWarning('Please enter a job posting URL');
      return;
    }

    setIsProcessing(true);
    setError(null);
    
    try {
      // For now, create a placeholder job from URL
      // In a real app, this would fetch and parse the URL content
      const parsedJob = {
        title: "Job from URL",
        company: "Company from Job Board",
        location: "Location not specified",
        description: `Job posting from URL: ${jobUrl}\n\nThis job was imported from a job board. Please edit the details below to complete the information.`,
        requirements: [],
        skills: [],
        salary: 'Not specified',
        type: 'full-time',
        source: jobUrl,
        url: jobUrl
      };
      
      setParsedJob(parsedJob);
      setIsProcessing(false);
    } catch (error) {
      console.error('Error fetching job from URL:', error);
      setError('Failed to fetch job posting from URL. Please check the URL and try again.');
      setIsProcessing(false);
    }
  };

  const handleManualSave = () => {
    if (!jobData.title || !jobData.company) {
      showWarning('Please fill in at least the job title and company');
      return;
    }

    const manualJob = {
      ...jobData,
      requirements: jobData.requirements.split('\n').filter(req => req.trim()),
      skills: [], // Could be extracted from description
      source: "manual-entry",
      matchScore: null
    };

    setParsedJob(manualJob);
  };

  const handleSaveJob = async () => {
    if (!parsedJob) {
      showWarning('No job data to save. Please parse a job posting first.');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      console.log('🚀 Saving job via GraphQL:', parsedJob);

      const { data } = await createJob({
        variables: {
          input: {
            title: parsedJob.title,
            companyName: parsedJob.company,
            locationText: parsedJob.location,
            description: parsedJob.description,
            requirements: parsedJob.requirements?.join('\n') || null,
            benefits: null,
            salaryMin: null,
            salaryMax: null,
            salaryCurrency: 'USD',
            salaryPeriod: 'yearly',
            jobType: parsedJob.type === 'full-time' ? 'full_time' : 'part_time',
            contractType: 'permanent',
            experienceLevel: null,
            remoteType: parsedJob.location?.toLowerCase().includes('remote') ? 'remote' : 'on_site'
          }
        }
      });

      if (data.createJob.success) {
        console.log('✅ Job saved successfully with ID:', data.createJob.jobId);
        showSuccess('Job posting saved successfully! You can now get AI optimization suggestions.');
        navigate('/ai-suggestions?newJob=true');
      } else {
        console.error('❌ Job save failed:', data.createJob.errors);
        setError('Failed to save job: ' + (data.createJob.errors?.join(', ') || 'Unknown error'));
      }
    } catch (err) {
      console.error('GraphQL createJob error:', err);
      setError('Failed to save job: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page-container">
      <div className="container">
        {/* Header */}
        <div className="page-header">
          <div className="header-content">
            <h1 className="page-title">Upload Job Position</h1>
            <p className="page-description">
              Add job postings to get AI-powered resume optimization and application insights
            </p>
          </div>
          <div className="header-actions">
            <Link to="/ai-suggestions" className="btn btn-outline">
              View AI Insights
            </Link>
          </div>
        </div>

        {/* Method Selection */}
        <div className="method-selection">
          <div className="method-tabs">
            <button 
              className={`method-tab ${method === 'paste' ? 'active' : ''}`}
              onClick={() => handleMethodChange('paste')}
            >
              📝 Paste Job Text
            </button>
            <button 
              className={`method-tab ${method === 'url' ? 'active' : ''}`}
              onClick={() => handleMethodChange('url')}
            >
              🔗 From URL
            </button>
            <button 
              className={`method-tab ${method === 'manual' ? 'active' : ''}`}
              onClick={() => handleMethodChange('manual')}
            >
              ✏️ Manual Entry
            </button>
          </div>
        </div>

        {/* Input Methods */}
        <div className="input-section">
          {method === 'paste' && (
            <div className="paste-method card">
              <div className="card-header">
                <h3>Paste Job Posting Text</h3>
                <p>Copy and paste the complete job posting from any source</p>
              </div>
              <div className="card-body">
                <textarea
                  className="job-text-area"
                  placeholder="Paste the complete job posting here (including title, company, description, requirements, etc.)..."
                  value={jobText}
                  onChange={(e) => setJobText(e.target.value)}
                  rows={12}
                />
                <div className="input-actions">
                  <button 
                    className="btn btn-primary"
                    onClick={handleTextSubmit}
                    disabled={isProcessing || !jobText.trim()}
                  >
                    {isProcessing ? 'Processing...' : 'Parse Job Posting'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {method === 'url' && (
            <div className="url-method card">
              <div className="card-header">
                <h3>Import from URL</h3>
                <p>Enter a link to a job posting from popular job boards</p>
              </div>
              <div className="card-body">
                <div className="url-input-group">
                  <input
                    type="url"
                    className="url-input"
                    placeholder="https://example.com/job-posting"
                    value={jobUrl}
                    onChange={(e) => setJobUrl(e.target.value)}
                  />
                  <button 
                    className="btn btn-primary"
                    onClick={handleUrlSubmit}
                    disabled={isProcessing || !jobUrl.trim()}
                  >
                    {isProcessing ? 'Fetching...' : 'Import'}
                  </button>
                </div>
                <div className="supported-sites">
                  <p>Supported sites: LinkedIn, Indeed, Glassdoor, AngelList, and more</p>
                </div>
              </div>
            </div>
          )}

          {method === 'manual' && (
            <div className="manual-method card">
              <div className="card-header">
                <h3>Manual Entry</h3>
                <p>Fill in the job details manually</p>
              </div>
              <div className="card-body">
                <div className="manual-form">
                  <div className="form-row">
                    <div className="form-group">
                      <label>Job Title *</label>
                      <input
                        type="text"
                        className="form-input"
                        placeholder="e.g., Senior Software Engineer"
                        value={jobData.title}
                        onChange={(e) => setJobData({...jobData, title: e.target.value})}
                      />
                    </div>
                    <div className="form-group">
                      <label>Company *</label>
                      <input
                        type="text"
                        className="form-input"
                        placeholder="e.g., TechCorp Inc."
                        value={jobData.company}
                        onChange={(e) => setJobData({...jobData, company: e.target.value})}
                      />
                    </div>
                  </div>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>Location</label>
                      <input
                        type="text"
                        className="form-input"
                        placeholder="e.g., San Francisco, CA"
                        value={jobData.location}
                        onChange={(e) => setJobData({...jobData, location: e.target.value})}
                      />
                    </div>
                    <div className="form-group">
                      <label>Job Type</label>
                      <select
                        className="form-input"
                        value={jobData.type}
                        onChange={(e) => setJobData({...jobData, type: e.target.value})}
                      >
                        <option value="full-time">Full-time</option>
                        <option value="part-time">Part-time</option>
                        <option value="contract">Contract</option>
                        <option value="freelance">Freelance</option>
                      </select>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Salary Range</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g., $80,000 - $120,000"
                      value={jobData.salary}
                      onChange={(e) => setJobData({...jobData, salary: e.target.value})}
                    />
                  </div>

                  <div className="form-group">
                    <label>Job Description</label>
                    <textarea
                      className="form-textarea"
                      placeholder="Describe the role, responsibilities, and what the company is looking for..."
                      value={jobData.description}
                      onChange={(e) => setJobData({...jobData, description: e.target.value})}
                      rows={4}
                    />
                  </div>

                  <div className="form-group">
                    <label>Requirements (one per line)</label>
                    <textarea
                      className="form-textarea"
                      placeholder="• 5+ years of experience&#10;• Proficiency in React and Node.js&#10;• Bachelor's degree in Computer Science"
                      value={jobData.requirements}
                      onChange={(e) => setJobData({...jobData, requirements: e.target.value})}
                      rows={6}
                    />
                  </div>

                  <div className="form-actions">
                    <button 
                      className="btn btn-primary"
                      onClick={handleManualSave}
                    >
                      Save Job Details
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Processing State */}
        {isProcessing && (
          <div className="processing-state card">
            <div className="card-body">
              <div className="processing-content">
                <div className="processing-spinner">⏳</div>
                <h3>Processing Job Posting...</h3>
                <p>Extracting key information and analyzing requirements</p>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error-state card">
            <div className="card-body">
              <div className="error-content">
                <div className="error-icon">❌</div>
                <h3>Error</h3>
                <p>{error}</p>
                <button className="btn btn-outline" onClick={() => setError(null)}>
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Parsed Job Preview */}
        {parsedJob && (
          <div className="parsed-job-section">
            <div className="section-header">
              <h2>Job Analysis Complete</h2>
              <p>Review the extracted information and save to get AI optimization insights</p>
            </div>

            <div className="job-preview card">
              <div className="card-body">
                <div className="job-header">
                  <div className="job-main-info">
                    <h3>{parsedJob.title}</h3>
                    <p className="company">{parsedJob.company}</p>
                    <p className="location">{parsedJob.location}</p>
                  </div>
                  {parsedJob.matchScore && (
                    <div className="match-score">
                      <div className="score-circle">
                        <span>{parsedJob.matchScore}%</span>
                      </div>
                      <p>Profile Match</p>
                    </div>
                  )}
                </div>

                <div className="job-details">
                  <div className="detail-section">
                    <h4>Description</h4>
                    <p>{parsedJob.description}</p>
                  </div>

                  <div className="detail-section">
                    <h4>Requirements</h4>
                    <ul>
                      {parsedJob.requirements.map((req, index) => (
                        <li key={index}>{req}</li>
                      ))}
                    </ul>
                  </div>

                  {parsedJob.skills && parsedJob.skills.length > 0 && (
                    <div className="detail-section">
                      <h4>Key Skills</h4>
                      <div className="skills-tags">
                        {parsedJob.skills.map((skill, index) => (
                          <span key={index} className="skill-tag">{skill}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="job-meta">
                    <div className="meta-item">
                      <span className="meta-label">Salary:</span>
                      <span>{parsedJob.salary || 'Not specified'}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Type:</span>
                      <span className="job-type">{parsedJob.type}</span>
                    </div>
                  </div>
                </div>

                <div className="job-actions">
                  <button 
                    className="btn btn-primary btn-lg"
                    onClick={handleSaveJob}
                    disabled={saving || createJobLoading}
                  >
                    {saving || createJobLoading ? 'Saving...' : 'Save & Get AI Insights'}
                  </button>
                  <Link to="/application-history" className="btn btn-outline btn-lg">
                    Track Application
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tips Section */}
        <div className="tips-section">
          <div className="card">
            <div className="card-header">
              <h3>Tips for Better Results</h3>
            </div>
            <div className="card-body">
              <div className="tips-content">
                <div className="tip-item">
                  <div className="tip-icon">💡</div>
                  <div className="tip-text">
                    <h4>Complete Job Postings</h4>
                    <p>Include the full job description, requirements, and company information for better AI analysis.</p>
                  </div>
                </div>
                <div className="tip-item">
                  <div className="tip-icon">🎯</div>
                  <div className="tip-text">
                    <h4>Multiple Positions</h4>
                    <p>Add multiple job postings to compare requirements and get comprehensive optimization suggestions.</p>
                  </div>
                </div>
                <div className="tip-item">
                  <div className="tip-icon">🔄</div>
                  <div className="tip-text">
                    <h4>Keep Updated</h4>
                    <p>Regularly update your saved jobs to ensure your optimization strategies remain current.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadJob;