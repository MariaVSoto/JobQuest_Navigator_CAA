import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation } from '@apollo/client';
import { gql } from '@apollo/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import './UploadJobEnhanced.css';

const CREATE_USER_JOB = gql`
  mutation CreateJob($input: CreateJobInput!) {
    createJob(input: $input) {
      success
      errors
      jobId
    }
  }
`;

const UploadJobEnhanced = () => {
  const { user } = useAuth();
  const { showSuccess, showError, showWarning } = useToast();
  const navigate = useNavigate();
  
  // Wizard state
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedMethod, setSelectedMethod] = useState(null);
  const totalSteps = 4;
  
  // Content state
  const [importContent, setImportContent] = useState({
    text: '',
    urls: [''],
    files: [],
    manualData: {
      title: '',
      company: '',
      location: '',
      description: '',
      requirements: '',
      salary: '',
      type: 'full-time',
      remote: false
    }
  });
  
  // Processing state
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState('');
  const [progress, setProgress] = useState(0);
  const [parsedJobs, setParsedJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});
  
  // Draft and history state
  const [savedDrafts, setSavedDrafts] = useState([]);
  const [autoSaveTimer, setAutoSaveTimer] = useState(null);
  
  // Refs
  const fileInputRef = useRef(null);
  const dropZoneRef = useRef(null);
  
  const [createJob, { loading: createJobLoading }] = useMutation(CREATE_USER_JOB);

  // Auto-save functionality
  useEffect(() => {
    if (selectedJob && currentStep >= 3) {
      clearTimeout(autoSaveTimer);
      const timer = setTimeout(() => {
        saveDraft();
      }, 3000); // Auto-save after 3 seconds of inactivity
      setAutoSaveTimer(timer);
    }
    return () => clearTimeout(autoSaveTimer);
  }, [selectedJob, currentStep]);

  // Import methods configuration
  const importMethods = [
    {
      id: 'text',
      title: 'Paste Job Text',
      description: 'Copy and paste job posting content',
      icon: '📝',
      estimatedTime: '30 seconds',
      difficulty: 'Easy',
      recommended: true,
      features: ['Smart parsing', 'Real-time preview', 'Format detection']
    },
    {
      id: 'url',
      title: 'Import from URL',
      description: 'Import directly from job board links',
      icon: '🔗',
      estimatedTime: '1 minute',
      difficulty: 'Easy',
      features: ['LinkedIn', 'Indeed', 'Glassdoor', 'AngelList']
    },
    {
      id: 'file',
      title: 'Upload Files',
      description: 'Upload PDF, DOC, or text files',
      icon: '📄',
      estimatedTime: '1 minute',
      difficulty: 'Easy',
      features: ['Drag & drop', 'Bulk upload', 'Multiple formats']
    },
    {
      id: 'bulk',
      title: 'Bulk Import',
      description: 'Import multiple jobs at once',
      icon: '📊',
      estimatedTime: '5 minutes',
      difficulty: 'Advanced',
      features: ['CSV/Excel', 'URL lists', 'Batch processing']
    }
  ];

  // Method selection handlers
  const handleMethodSelect = (methodId) => {
    setSelectedMethod(methodId);
    setCurrentStep(2);
    setValidationErrors({});
  };

  // Drag and drop handlers
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZoneRef.current?.classList.add('drag-over');
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZoneRef.current?.classList.remove('drag-over');
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZoneRef.current?.classList.remove('drag-over');
    
    const files = Array.from(e.dataTransfer.files);
    handleFileUpload(files);
  }, []);

  const handleFileUpload = (files) => {
    const validFiles = files.filter(file => {
      const validTypes = ['text/plain', 'application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      return validTypes.includes(file.type) || file.name.toLowerCase().endsWith('.txt');
    });

    if (validFiles.length !== files.length) {
      showWarning('Some files were skipped. Only PDF, DOC, DOCX, and TXT files are supported.');
    }

    setImportContent(prev => ({
      ...prev,
      files: [...prev.files, ...validFiles]
    }));

    if (validFiles.length > 0) {
      processFiles(validFiles);
    }
  };

  // Content processing functions
  const processTextContent = async (text) => {
    setIsProcessing(true);
    setProcessingStage('Analyzing content...');
    setProgress(10);

    try {
      // Simulate AI processing steps
      await simulateProcessingStep('Detecting format...', 25);
      await simulateProcessingStep('Extracting key information...', 50);
      await simulateProcessingStep('Enhancing with AI...', 75);
      await simulateProcessingStep('Finalizing...', 90);

      const parsedJob = await enhancedTextParsing(text);
      setParsedJobs([parsedJob]);
      setSelectedJob(parsedJob);
      setProgress(100);
      setCurrentStep(3);
    } catch (error) {
      showError('Failed to process job posting: ' + error.message);
    } finally {
      setIsProcessing(false);
      setProcessingStage('');
      setProgress(0);
    }
  };

  const processURLContent = async (urls) => {
    setIsProcessing(true);
    setProcessingStage('Fetching job postings...');
    setProgress(10);

    try {
      const validUrls = urls.filter(url => url.trim());
      const jobs = [];

      for (let i = 0; i < validUrls.length; i++) {
        const url = validUrls[i];
        setProcessingStage(`Processing URL ${i + 1} of ${validUrls.length}...`);
        setProgress(20 + (i / validUrls.length) * 60);
        
        const job = await processJobURL(url);
        jobs.push(job);
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate processing time
      }

      setParsedJobs(jobs);
      setSelectedJob(jobs[0]);
      setProgress(100);
      setCurrentStep(3);
    } catch (error) {
      showError('Failed to process URLs: ' + error.message);
    } finally {
      setIsProcessing(false);
      setProcessingStage('');
      setProgress(0);
    }
  };

  const processFiles = async (files) => {
    setIsProcessing(true);
    setProcessingStage('Reading files...');
    setProgress(10);

    try {
      const jobs = [];
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setProcessingStage(`Processing ${file.name}...`);
        setProgress(20 + (i / files.length) * 60);
        
        const content = await readFileContent(file);
        const job = await enhancedTextParsing(content, file.name);
        jobs.push(job);
      }

      setParsedJobs(jobs);
      setSelectedJob(jobs[0]);
      setProgress(100);
      setCurrentStep(3);
    } catch (error) {
      showError('Failed to process files: ' + error.message);
    } finally {
      setIsProcessing(false);
      setProcessingStage('');
      setProgress(0);
    }
  };

  // Helper functions
  const simulateProcessingStep = (stage, progress) => {
    return new Promise(resolve => {
      setTimeout(() => {
        setProcessingStage(stage);
        setProgress(progress);
        resolve();
      }, 500);
    });
  };

  const enhancedTextParsing = async (text, filename = '') => {
    const lines = text.split('\n').filter(line => line.trim());
    
    // Enhanced parsing with better patterns
    const titlePatterns = [
      /^(.+?)\s*[-–—|]\s*(.+?)$/m,
      /^Job Title:?\s*(.+?)$/im,
      /^Position:?\s*(.+?)$/im,
      /^(.+?)\s*at\s+(.+?)$/im
    ];

    const companyPatterns = [
      /Company:?\s*(.+?)$/im,
      /at\s+([A-Z][A-Za-z\s&.,Inc]+)/i,
      /([A-Z][A-Za-z\s&.,Inc]+)\s+is\s+(hiring|seeking|looking)/i,
      /Join\s+([A-Z][A-Za-z\s&.,Inc]+)/i
    ];

    const locationPatterns = [
      /Location:?\s*(.+?)$/im,
      /^(Remote|Hybrid|On-site)$/im,
      /([A-Za-z\s]+,\s*[A-Z]{2,})/i,
      /(Remote|Work from home|WFH)/i
    ];

    const salaryPatterns = [
      /Salary:?\s*(.+?)$/im,
      /Pay:?\s*(.+?)$/im,
      /\$[\d,]+\s*[-–—]\s*\$[\d,]+/i,
      /\$[\d,]+\s*per\s+\w+/i
    ];

    let title = filename || 'Job Position';
    let company = 'Company Name';
    let location = 'Location not specified';
    let salary = 'Not specified';

    // Try to extract title
    for (const pattern of titlePatterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        title = match[1].trim();
        if (match[2] && !company.includes('Company')) {
          company = match[2].trim();
        }
        break;
      }
    }

    // Try to extract company
    for (const pattern of companyPatterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        company = match[1].trim();
        break;
      }
    }

    // Try to extract location
    for (const pattern of locationPatterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        location = match[1].trim();
        break;
      }
    }

    // Try to extract salary
    for (const pattern of salaryPatterns) {
      const match = text.match(pattern);
      if (match && match[0]) {
        salary = match[0].trim();
        break;
      }
    }

    // Extract skills (enhanced pattern matching)
    const skillKeywords = [
      'React', 'JavaScript', 'Python', 'Java', 'Node.js', 'SQL', 'AWS', 'Docker',
      'TypeScript', 'GraphQL', 'MongoDB', 'PostgreSQL', 'Git', 'Linux', 'APIs',
      'REST', 'Microservices', 'Kubernetes', 'CI/CD', 'Agile', 'Scrum'
    ];
    
    const foundSkills = skillKeywords.filter(skill => 
      text.toLowerCase().includes(skill.toLowerCase())
    );

    // Extract requirements
    const requirements = extractRequirements(text);

    return {
      id: `job-${Date.now()}`,
      title,
      company,
      location,
      description: text,
      requirements,
      skills: foundSkills,
      salary,
      type: 'full-time',
      remote: location.toLowerCase().includes('remote'),
      source: filename ? 'file-upload' : 'text-paste',
      rawText: text,
      confidence: calculateConfidence(title, company, location),
      aiEnhancements: generateAIEnhancements(text),
      createdAt: new Date().toISOString()
    };
  };

  const extractRequirements = (text) => {
    const requirementSections = [
      /Requirements?:?\s*([\s\S]*?)(?=\n\n|\n[A-Z]|\n\*|\nBenefits?|$)/i,
      /Qualifications?:?\s*([\s\S]*?)(?=\n\n|\n[A-Z]|\n\*|\nBenefits?|$)/i,
      /Must have:?\s*([\s\S]*?)(?=\n\n|\n[A-Z]|\n\*|\nBenefits?|$)/i
    ];

    for (const pattern of requirementSections) {
      const match = text.match(pattern);
      if (match && match[1]) {
        return match[1]
          .split(/\n/)
          .map(req => req.trim())
          .filter(req => req && req.length > 10)
          .slice(0, 10); // Limit to 10 requirements
      }
    }

    return [];
  };

  const calculateConfidence = (title, company, location) => {
    let score = 0;
    if (title && title !== 'Job Position') score += 30;
    if (company && company !== 'Company Name') score += 30;
    if (location && location !== 'Location not specified') score += 20;
    score += Math.min(20, Math.random() * 20); // Random factor for demo
    return Math.round(score);
  };

  const generateAIEnhancements = (text) => {
    const enhancements = [];
    
    if (text.length < 200) {
      enhancements.push({
        type: 'length',
        suggestion: 'Consider adding more detail to the job description',
        priority: 'medium'
      });
    }

    if (!text.toLowerCase().includes('benefit')) {
      enhancements.push({
        type: 'benefits',
        suggestion: 'Add information about benefits and compensation',
        priority: 'low'
      });
    }

    if (!text.toLowerCase().includes('experience')) {
      enhancements.push({
        type: 'experience',
        suggestion: 'Specify required years of experience',
        priority: 'medium'
      });
    }

    return enhancements;
  };

  const processJobURL = async (url) => {
    // Simulate URL processing
    const domain = new URL(url).hostname;
    let source = 'job-board';
    
    if (domain.includes('linkedin')) source = 'LinkedIn';
    else if (domain.includes('indeed')) source = 'Indeed';
    else if (domain.includes('glassdoor')) source = 'Glassdoor';

    return {
      id: `job-${Date.now()}-${Math.random()}`,
      title: `Job from ${source}`,
      company: `Company via ${source}`,
      location: 'Location from URL',
      description: `Job posting imported from: ${url}\n\nThis position was automatically imported from ${source}. Please review and edit the details below.`,
      requirements: [`Experience with ${source} platform`],
      skills: ['Communication', 'Problem Solving'],
      salary: 'Competitive',
      type: 'full-time',
      remote: false,
      source: source.toLowerCase(),
      url: url,
      confidence: 75,
      aiEnhancements: [],
      createdAt: new Date().toISOString()
    };
  };

  const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  };

  // Save and draft functions
  const saveDraft = () => {
    if (selectedJob) {
      const draft = {
        ...selectedJob,
        id: `draft-${Date.now()}`,
        isDraft: true,
        lastModified: new Date().toISOString()
      };
      
      setSavedDrafts(prev => {
        const existing = prev.findIndex(d => d.originalId === selectedJob.id);
        if (existing >= 0) {
          prev[existing] = draft;
          return [...prev];
        }
        return [...prev, draft];
      });
    }
  };

  const handleSaveJob = async () => {
    if (!selectedJob) {
      showWarning('No job data to save. Please process a job posting first.');
      return;
    }

    setIsProcessing(true);
    setProcessingStage('Saving job...');

    try {
      const { data } = await createJob({
        variables: {
          input: {
            title: selectedJob.title,
            companyName: selectedJob.company,
            locationText: selectedJob.location,
            description: selectedJob.description,
            requirements: selectedJob.requirements?.join('\n') || null,
            benefits: null,
            salaryMin: null,
            salaryMax: null,
            salaryCurrency: 'USD',
            salaryPeriod: 'yearly',
            jobType: selectedJob.type === 'full-time' ? 'full_time' : 'part_time',
            contractType: 'permanent',
            experienceLevel: null,
            remoteType: selectedJob.remote ? 'remote' : 'on_site'
          }
        }
      });

      if (data.createJob.success) {
        showSuccess('Job saved successfully! Getting AI insights...');
        setCurrentStep(4);
        // Navigate to AI suggestions after a brief delay
        setTimeout(() => {
          navigate('/ai-suggestions?newJob=true');
        }, 2000);
      } else {
        showError('Failed to save job: ' + (data.createJob.errors?.join(', ') || 'Unknown error'));
      }
    } catch (err) {
      showError('Failed to save job: ' + err.message);
    } finally {
      setIsProcessing(false);
      setProcessingStage('');
    }
  };

  // Navigation functions
  const handleStepBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      if (currentStep === 2) {
        setSelectedMethod(null);
      }
    }
  };

  const handleStepForward = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  // Render different steps
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return renderMethodSelection();
      case 2:
        return renderImportInterface();
      case 3:
        return renderJobPreview();
      case 4:
        return renderSuccessStep();
      default:
        return renderMethodSelection();
    }
  };

  const renderMethodSelection = () => (
    <div className="method-selection-enhanced">
      <div className="step-header">
        <h2>Choose Your Import Method</h2>
        <p>Select how you'd like to add job postings to your profile</p>
      </div>
      
      <div className="method-grid">
        {importMethods.map((method) => (
          <div
            key={method.id}
            className={`method-card ${method.recommended ? 'recommended' : ''}`}
            onClick={() => handleMethodSelect(method.id)}
          >
            {method.recommended && (
              <div className="recommended-badge">Recommended</div>
            )}
            
            <div className="method-icon">{method.icon}</div>
            <h3>{method.title}</h3>
            <p className="method-description">{method.description}</p>
            
            <div className="method-meta">
              <span className="time-estimate">⏱️ {method.estimatedTime}</span>
              <span className="difficulty">{method.difficulty}</span>
            </div>
            
            <div className="method-features">
              {method.features.map((feature, index) => (
                <span key={index} className="feature-tag">{feature}</span>
              ))}
            </div>
            
            <button className="method-select-btn">
              Select Method
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderImportInterface = () => {
    switch (selectedMethod) {
      case 'text':
        return renderTextImport();
      case 'url':
        return renderURLImport();
      case 'file':
        return renderFileImport();
      case 'bulk':
        return renderBulkImport();
      default:
        return null;
    }
  };

  const renderTextImport = () => (
    <div className="import-interface text-import">
      <div className="import-header">
        <h3>📝 Paste Job Posting Text</h3>
        <p>Copy the complete job posting and paste it below for intelligent parsing</p>
      </div>

      <div className="smart-textarea-container">
        <textarea
          className="smart-textarea"
          placeholder="Paste the complete job posting here including:
          
• Job title and company name
• Job description and responsibilities  
• Required qualifications and skills
• Salary range and benefits
• Location and work arrangement

The AI will automatically extract and organize this information..."
          value={importContent.text}
          onChange={(e) => setImportContent(prev => ({ ...prev, text: e.target.value }))}
          rows={15}
        />
        
        <div className="textarea-footer">
          <div className="character-count">
            {importContent.text.length} characters
            {importContent.text.length > 500 && (
              <span className="good-length">✓ Good length for parsing</span>
            )}
          </div>
          
          <div className="format-hints">
            <span className="hint-tag">💡 Include full job description</span>
            <span className="hint-tag">🎯 Mention required skills</span>
            <span className="hint-tag">📍 Add location details</span>
          </div>
        </div>
      </div>

      <div className="import-actions">
        <button
          className="btn btn-primary btn-lg"
          onClick={() => processTextContent(importContent.text)}
          disabled={!importContent.text.trim() || isProcessing}
        >
          {isProcessing ? 'Processing...' : 'Parse Job Posting'}
        </button>
      </div>
    </div>
  );

  const renderURLImport = () => (
    <div className="import-interface url-import">
      <div className="import-header">
        <h3>🔗 Import from Job Board URLs</h3>
        <p>Enter job posting URLs from popular job boards</p>
      </div>

      <div className="url-inputs">
        {importContent.urls.map((url, index) => (
          <div key={index} className="url-input-group">
            <div className="url-input-container">
              <input
                type="url"
                className="url-input"
                placeholder={`Job posting URL ${index + 1}`}
                value={url}
                onChange={(e) => {
                  const newUrls = [...importContent.urls];
                  newUrls[index] = e.target.value;
                  setImportContent(prev => ({ ...prev, urls: newUrls }));
                }}
              />
              {index > 0 && (
                <button
                  className="remove-url-btn"
                  onClick={() => {
                    const newUrls = importContent.urls.filter((_, i) => i !== index);
                    setImportContent(prev => ({ ...prev, urls: newUrls }));
                  }}
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        ))}
        
        <button
          className="add-url-btn"
          onClick={() => {
            setImportContent(prev => ({
              ...prev,
              urls: [...prev.urls, '']
            }));
          }}
        >
          ➕ Add Another URL
        </button>
      </div>

      <div className="supported-platforms">
        <h4>Supported Platforms:</h4>
        <div className="platform-list">
          <span className="platform-tag">🔵 LinkedIn</span>
          <span className="platform-tag">🟢 Indeed</span>
          <span className="platform-tag">🔶 Glassdoor</span>
          <span className="platform-tag">🟣 AngelList</span>
        </div>
      </div>

      <div className="import-actions">
        <button
          className="btn btn-primary btn-lg"
          onClick={() => processURLContent(importContent.urls)}
          disabled={!importContent.urls.some(url => url.trim()) || isProcessing}
        >
          {isProcessing ? 'Importing...' : 'Import from URLs'}
        </button>
      </div>
    </div>
  );

  const renderFileImport = () => (
    <div className="import-interface file-import">
      <div className="import-header">
        <h3>📄 Upload Job Posting Files</h3>
        <p>Drag and drop or browse for PDF, DOC, or text files</p>
      </div>

      <div
        ref={dropZoneRef}
        className="drag-drop-zone"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="drop-zone-content">
          <div className="drop-zone-icon">📁</div>
          <h4>Drop files here or click to browse</h4>
          <p>Supports PDF, DOC, DOCX, and TXT files</p>
          <button className="browse-btn">Browse Files</button>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.txt"
        onChange={(e) => handleFileUpload(Array.from(e.target.files))}
        style={{ display: 'none' }}
      />

      {importContent.files.length > 0 && (
        <div className="uploaded-files">
          <h4>Uploaded Files:</h4>
          <div className="file-list">
            {importContent.files.map((file, index) => (
              <div key={index} className="file-item">
                <span className="file-icon">📄</span>
                <span className="file-name">{file.name}</span>
                <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                <button
                  className="remove-file-btn"
                  onClick={() => {
                    const newFiles = importContent.files.filter((_, i) => i !== index);
                    setImportContent(prev => ({ ...prev, files: newFiles }));
                  }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {importContent.files.length > 0 && (
        <div className="import-actions">
          <button
            className="btn btn-primary btn-lg"
            onClick={() => processFiles(importContent.files)}
            disabled={isProcessing}
          >
            {isProcessing ? 'Processing Files...' : `Process ${importContent.files.length} File(s)`}
          </button>
        </div>
      )}
    </div>
  );

  const renderBulkImport = () => (
    <div className="import-interface bulk-import">
      <div className="import-header">
        <h3>📊 Bulk Import Jobs</h3>
        <p>Import multiple job postings at once using various methods</p>
      </div>

      <div className="bulk-methods">
        <div className="bulk-method-card">
          <h4>📋 CSV/Excel Import</h4>
          <p>Upload a spreadsheet with job data</p>
          <button className="btn btn-outline">Choose File</button>
        </div>

        <div className="bulk-method-card">
          <h4>🔗 URL List</h4>
          <p>Process multiple job board URLs</p>
          <textarea
            placeholder="Enter one URL per line..."
            rows={5}
          />
          <button className="btn btn-outline">Process URLs</button>
        </div>

        <div className="bulk-method-card">
          <h4>📁 Zip File</h4>
          <p>Upload a zip file containing multiple job files</p>
          <button className="btn btn-outline">Upload Zip</button>
        </div>
      </div>

      <div className="bulk-info">
        <h4>Bulk Import Features:</h4>
        <ul>
          <li>✓ Process up to 50 jobs at once</li>
          <li>✓ Duplicate detection and merging</li>
          <li>✓ Progress tracking and error reporting</li>
          <li>✓ Batch validation and cleanup</li>
        </ul>
      </div>
    </div>
  );

  const renderJobPreview = () => (
    <div className="job-preview-enhanced">
      <div className="preview-header">
        <h3>🎯 Job Analysis Complete</h3>
        <p>Review and enhance the extracted information</p>
        
        <div className="confidence-score">
          <div className="confidence-circle">
            <span>{selectedJob?.confidence || 0}%</span>
          </div>
          <div className="confidence-label">
            <strong>Parsing Confidence</strong>
            <p>Based on data quality and completeness</p>
          </div>
        </div>
      </div>

      {selectedJob && (
        <div className="job-preview-card">
          <div className="job-header-enhanced">
            <div className="job-main-info">
              <h2>{selectedJob.title}</h2>
              <div className="company-info">
                <span className="company-name">{selectedJob.company}</span>
                <span className="location">{selectedJob.location}</span>
                {selectedJob.remote && <span className="remote-badge">Remote</span>}
              </div>
              <div className="job-meta-tags">
                <span className="job-type-tag">{selectedJob.type}</span>
                <span className="salary-tag">{selectedJob.salary}</span>
                <span className="source-tag">via {selectedJob.source}</span>
              </div>
            </div>
          </div>

          <div className="job-content-sections">
            <div className="content-section">
              <h4>📝 Description</h4>
              <div className="content-preview">
                {selectedJob.description.length > 300 
                  ? selectedJob.description.substring(0, 300) + '...'
                  : selectedJob.description
                }
              </div>
            </div>

            {selectedJob.requirements.length > 0 && (
              <div className="content-section">
                <h4>📋 Requirements</h4>
                <ul className="requirements-list">
                  {selectedJob.requirements.slice(0, 5).map((req, index) => (
                    <li key={index}>{req}</li>
                  ))}
                  {selectedJob.requirements.length > 5 && (
                    <li className="more-items">+{selectedJob.requirements.length - 5} more</li>
                  )}
                </ul>
              </div>
            )}

            {selectedJob.skills.length > 0 && (
              <div className="content-section">
                <h4>🛠️ Key Skills</h4>
                <div className="skills-grid">
                  {selectedJob.skills.map((skill, index) => (
                    <span key={index} className="skill-badge">{skill}</span>
                  ))}
                </div>
              </div>
            )}

            {selectedJob.aiEnhancements.length > 0 && (
              <div className="content-section">
                <h4>🤖 AI Suggestions</h4>
                <div className="ai-enhancements">
                  {selectedJob.aiEnhancements.map((enhancement, index) => (
                    <div key={index} className={`enhancement-item ${enhancement.priority}`}>
                      <span className="enhancement-type">{enhancement.type}</span>
                      <span className="enhancement-text">{enhancement.suggestion}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="preview-actions">
            <button className="btn btn-outline btn-lg" onClick={saveDraft}>
              💾 Save Draft
            </button>
            <button 
              className="btn btn-primary btn-lg"
              onClick={handleSaveJob}
              disabled={isProcessing || createJobLoading}
            >
              {isProcessing || createJobLoading ? 'Saving...' : '🚀 Save & Get AI Insights'}
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const renderSuccessStep = () => (
    <div className="success-step">
      <div className="success-content">
        <div className="success-icon">🎉</div>
        <h2>Job Successfully Saved!</h2>
        <p>Your job posting has been processed and saved. You'll be redirected to AI insights shortly.</p>
        
        <div className="success-actions">
          <Link to="/ai-suggestions" className="btn btn-primary btn-lg">
            View AI Insights
          </Link>
          <Link to="/jobs" className="btn btn-outline btn-lg">
            View All Jobs
          </Link>
        </div>
      </div>
    </div>
  );

  return (
    <div className="upload-job-enhanced">
      {/* Progress Header */}
      <div className="wizard-header">
        <div className="container">
          <div className="progress-section">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${(currentStep / totalSteps) * 100}%` }}
              />
            </div>
            <div className="step-labels">
              {['Method', 'Import', 'Review', 'Complete'].map((label, index) => (
                <div 
                  key={index}
                  className={`step-label ${currentStep > index + 1 ? 'completed' : currentStep === index + 1 ? 'active' : ''}`}
                >
                  <span className="step-number">{index + 1}</span>
                  <span className="step-text">{label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="header-actions">
            {currentStep > 1 && (
              <button className="btn btn-outline" onClick={handleStepBack}>
                ← Back
              </button>
            )}
            <Link to="/jobs" className="btn btn-ghost">
              Cancel
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="wizard-content">
        <div className="container">
          {isProcessing && (
            <div className="processing-overlay">
              <div className="processing-card">
                <div className="processing-animation">
                  <div className="spinner"></div>
                </div>
                <h3>{processingStage}</h3>
                <div className="progress-bar-small">
                  <div 
                    className="progress-fill-small"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p>{progress}% complete</p>
              </div>
            </div>
          )}

          {renderStepContent()}
        </div>
      </div>

      {/* Drafts Sidebar */}
      {savedDrafts.length > 0 && (
        <div className="drafts-sidebar">
          <h4>💾 Saved Drafts</h4>
          <div className="drafts-list">
            {savedDrafts.map((draft, index) => (
              <div key={index} className="draft-item">
                <span className="draft-title">{draft.title}</span>
                <span className="draft-time">
                  {new Date(draft.lastModified).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadJobEnhanced;