import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './UploadJob.css';

const UploadJob = () => {
  const { user } = useAuth();
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
      alert('Please paste the job posting text');
      return;
    }

    setIsProcessing(true);
    
    // Simulate AI parsing of job posting text
    setTimeout(() => {
      const mockParsedJob = {
        title: "Senior Full Stack Developer",
        company: "TechFlow Inc.",
        location: "San Francisco, CA (Remote)",
        description: "Join our dynamic team to build scalable web applications using modern technologies. You'll work on exciting projects that impact millions of users worldwide.",
        requirements: [
          "5+ years of experience in full-stack development",
          "Proficiency in React, Node.js, and TypeScript",
          "Experience with cloud platforms (AWS, Azure, or GCP)",
          "Strong understanding of database design and optimization",
          "Excellent communication and teamwork skills"
        ],
        skills: ["React", "Node.js", "TypeScript", "AWS", "PostgreSQL", "GraphQL", "Docker"],
        salary: "$120,000 - $150,000",
        type: "full-time",
        source: "pasted-text",
        matchScore: 85
      };
      
      setParsedJob(mockParsedJob);
      setIsProcessing(false);
    }, 2000);
  };

  const handleUrlSubmit = async () => {
    if (!jobUrl.trim()) {
      alert('Please enter a job posting URL');
      return;
    }

    setIsProcessing(true);
    
    // Simulate fetching and parsing job from URL
    setTimeout(() => {
      const mockParsedJob = {
        title: "Product Manager",
        company: "InnovateCorp",
        location: "New York, NY",
        description: "Lead product development initiatives and work closely with engineering teams to deliver exceptional user experiences.",
        requirements: [
          "3+ years of product management experience",
          "Experience with agile development methodologies",
          "Strong analytical and problem-solving skills",
          "Excellent stakeholder management abilities",
          "Technical background preferred"
        ],
        skills: ["Product Management", "Agile", "Analytics", "Stakeholder Management", "Technical Strategy"],
        salary: "$100,000 - $130,000",
        type: "full-time",
        source: jobUrl,
        matchScore: 72
      };
      
      setParsedJob(mockParsedJob);
      setIsProcessing(false);
    }, 3000);
  };

  const handleManualSave = () => {
    if (!jobData.title || !jobData.company) {
      alert('Please fill in at least the job title and company');
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

  const handleSaveJob = () => {
    // In a real app, this would save to backend
    alert('Job posting saved successfully! You can now get AI optimization suggestions.');
    window.location.href = '/ai-suggestions?newJob=true';
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
                  >
                    Save & Get AI Insights
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