import React, { useState, useContext } from 'react';
import { JobContext } from '../context/JobContext';
import './JobApplicationForm.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const JobApplicationForm = () => {
  const { selectedJob } = useContext(JobContext);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [coverLetter, setCoverLetter] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const jobTitle = selectedJob?.title || '';
  const jobCompany = selectedJob?.company?.display_name || '';

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="application-container">
      <div className="application-box">
        {/* <img src={logo} alt="JobQuest Logo" className="application-logo" /> */}
        <h1 className="application-title">Job Application</h1>
        {selectedJob && (
          <div className="application-jobinfo">
            <div><strong>Job:</strong> {jobTitle}</div>
            <div><strong>Company:</strong> {jobCompany}</div>
          </div>
        )}
        {submitted ? (
          <div className="application-success">Application submitted successfully!</div>
        ) : (
          <form className="application-form" onSubmit={handleSubmit}>
            <label htmlFor="name">Name</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={e => setName(e.target.value)}
              required
            />
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
            <label htmlFor="resume">Resume</label>
            <input
              type="file"
              id="resume"
              accept=".pdf,.doc,.docx"
              required
            />
            <label htmlFor="coverLetter">Cover Letter</label>
            <textarea
              id="coverLetter"
              value={coverLetter}
              onChange={e => setCoverLetter(e.target.value)}
              rows={5}
              required
            />
            <button type="submit" className="application-btn">Submit Application</button>
          </form>
        )}
      </div>
    </div>
  );
};

export default JobApplicationForm; 