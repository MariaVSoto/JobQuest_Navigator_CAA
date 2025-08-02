import React, { useState, useRef } from 'react';
import { useMutation } from '@apollo/client';
import { gql } from '@apollo/client';
import './PDFUploadComponent.css';

const UPLOAD_RESUME_FILE_MUTATION = gql`
  mutation UploadResumeFile($input: UploadResumeFileInput!) {
    uploadResumeFile(input: $input) {
      success
      message
      errors
      resumeId
      processingStatus
      downloadUrl
    }
  }
`;

const PROCESS_PDF_RESUME_MUTATION = gql`
  mutation ProcessPDFResume($resumeId: String!) {
    processPdfResume(resumeId: $resumeId) {
      success
      message
      errors
      processingTime
    }
  }
`;

const PDFUploadComponent = ({ onUploadSuccess, onProcessSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadedResumeId, setUploadedResumeId] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [title, setTitle] = useState('');
  const fileInputRef = useRef(null);

  const [uploadResumeMutation] = useMutation(UPLOAD_RESUME_FILE_MUTATION);
  const [processPDFMutation] = useMutation(PROCESS_PDF_RESUME_MUTATION);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      if (file.type !== 'application/pdf') {
        setError('Please select a PDF file only.');
        return;
      }

      // Validate file size (max 10MB)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        setError('File size must be less than 10MB.');
        return;
      }

      setSelectedFile(file);
      setError(null);
      
      // Auto-generate title from filename if not set
      if (!title) {
        const filename = file.name.replace('.pdf', '');
        setTitle(filename + ' Resume');
      }
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setUploadedResumeId(null);
    setError(null);
    setSuccess(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const convertFileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        // Remove the "data:application/pdf;base64," prefix
        const base64String = reader.result.split(',')[1];
        resolve(base64String);
      };
      reader.onerror = (error) => reject(error);
    });
  };

  const handleUpload = async () => {
    if (!selectedFile || !title.trim()) {
      setError('Please select a file and enter a title.');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      // Convert file to base64
      const fileData = await convertFileToBase64(selectedFile);

      // Upload file
      const { data } = await uploadResumeMutation({
        variables: {
          input: {
            title: title.trim(),
            fileData: fileData,
            filename: selectedFile.name,
            contentType: selectedFile.type
          }
        }
      });

      const result = data.uploadResumeFile;

      if (result.success) {
        setUploadedResumeId(result.resumeId);
        setSuccess('PDF uploaded successfully! You can now process it to extract data.');
        
        // Notify parent component
        if (onUploadSuccess) {
          onUploadSuccess({
            resumeId: result.resumeId,
            filename: selectedFile.name,
            downloadUrl: result.downloadUrl
          });
        }
      } else {
        setError(result.errors?.join(', ') || 'Upload failed');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError('Upload failed: ' + (err.message || 'Unknown error'));
    } finally {
      setUploading(false);
    }
  };

  const handleProcessPDF = async () => {
    if (!uploadedResumeId) {
      setError('No uploaded file to process.');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      const { data } = await processPDFMutation({
        variables: {
          resumeId: uploadedResumeId
        }
      });

      const result = data.processPdfResume;

      if (result.success) {
        setSuccess(`PDF processed successfully in ${result.processingTime?.toFixed(2) || 'N/A'}s! Resume data has been extracted.`);
        
        // Notify parent component with extracted data
        if (onProcessSuccess) {
          onProcessSuccess({
            resumeId: uploadedResumeId,
            extractedData: null, // Temporarily disabled
            processingTime: result.processingTime
          });
        }
      } else {
        setError(result.errors?.join(', ') || 'Processing failed');
      }
    } catch (err) {
      console.error('Processing error:', err);
      setError('Processing failed: ' + (err.message || 'Unknown error'));
    } finally {
      setProcessing(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="pdf-upload-component">
      <div className="upload-header">
        <h3>Upload PDF Resume</h3>
        <p>Upload your existing resume in PDF format to extract and edit the information</p>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      {/* Resume Title Input */}
      <div className="form-group">
        <label>Resume Title *</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Software Engineer Resume"
          disabled={uploading || processing}
        />
      </div>

      {/* File Selection */}
      <div className="upload-section">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={uploading || processing}
        />

        {!selectedFile ? (
          <div 
            className="file-drop-zone"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="drop-zone-content">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" fill="none"/>
                <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" fill="none"/>
                <path d="M16 13H8" stroke="currentColor" strokeWidth="2"/>
                <path d="M16 17H8" stroke="currentColor" strokeWidth="2"/>
                <path d="M10 9H9H8" stroke="currentColor" strokeWidth="2"/>
              </svg>
              <p>Click to select PDF file</p>
              <span>Max file size: 10MB</span>
            </div>
          </div>
        ) : (
          <div className="selected-file">
            <div className="file-info">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" fill="none"/>
                <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" fill="none"/>
              </svg>
              <div className="file-details">
                <span className="filename">{selectedFile.name}</span>
                <span className="filesize">{formatFileSize(selectedFile.size)}</span>
              </div>
            </div>
            <button
              className="remove-file-btn"
              onClick={handleRemoveFile}
              disabled={uploading || processing}
            >
              ×
            </button>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="upload-actions">
        {!uploadedResumeId ? (
          <button
            className="upload-btn"
            onClick={handleUpload}
            disabled={!selectedFile || !title.trim() || uploading}
          >
            {uploading ? 'Uploading...' : 'Upload PDF'}
          </button>
        ) : (
          <div className="process-section">
            <div className="upload-success-info">
              ✓ File uploaded successfully
            </div>
            <button
              className="process-btn"
              onClick={handleProcessPDF}
              disabled={processing}
            >
              {processing ? 'Processing PDF...' : 'Extract Resume Data'}
            </button>
          </div>
        )}
      </div>

      {/* Processing Status */}
      {(uploading || processing) && (
        <div className="processing-status">
          <div className="loading-spinner"></div>
          <span>
            {uploading ? 'Uploading your PDF...' : 'Extracting resume data...'}
          </span>
        </div>
      )}
    </div>
  );
};

export default PDFUploadComponent;