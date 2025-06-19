import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { JobContext } from '../context/JobContext';
import './ApplicationHistory.css';

const ApplicationHistory = () => {
  const navigate = useNavigate();
  const { jobs } = React.useContext(JobContext);
  const [applications, setApplications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // In a real application, this would be an API call
    const fetchApplications = async () => {
      setIsLoading(true);
      try {
        // Simulating API call with mock data
        const mockApplications = jobs.slice(0, 8).map(job => ({
          id: job.id || job.__unique_id || job.redirect_url,
          jobTitle: job.title,
          company: job.company?.display_name || 'Unknown Company',
          location: job.location?.display_name || 'Unknown Location',
          appliedDate: new Date(Date.now() - Math.random() * 10000000000),
          status: ['applied', 'interviewing', 'offered', 'rejected'][Math.floor(Math.random() * 4)],
          lastUpdated: new Date(Date.now() - Math.random() * 1000000000),
          notes: [
            'Application submitted',
            'Resume reviewed',
            'Initial screening completed',
            'Technical interview scheduled',
            'Final interview completed'
          ].slice(0, Math.floor(Math.random() * 5) + 1),
          nextSteps: Math.random() > 0.5 ? 'Follow up with recruiter' : null
        }));
        setApplications(mockApplications);
      } catch (error) {
        console.error('Error fetching applications:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchApplications();
  }, [jobs]);

  const handleStatusChange = (e, applicationId) => {
    const newStatus = e.target.value;
    setApplications(prev => prev.map(app => 
      app.id === applicationId ? { ...app, status: newStatus } : app
    ));
    // Here we would typically make an API call to update the status
  };

  const handleAddNote = (applicationId) => {
    const note = prompt('Enter a new note:');
    if (note) {
      setApplications(prev => prev.map(app => 
        app.id === applicationId 
          ? { 
              ...app, 
              notes: [...app.notes, note],
              lastUpdated: new Date()
            } 
          : app
      ));
      // Here we would typically make an API call to add the note
    }
  };

  const handleJobClick = (jobId) => {
    navigate(`/jobs/${jobId}`);
  };

  const filteredApplications = applications
    .filter(app => {
      const matchesStatus = filterStatus === 'all' || app.status === filterStatus;
      const matchesSearch = searchQuery === '' || 
        app.jobTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
        app.company.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesStatus && matchesSearch;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return b.appliedDate - a.appliedDate;
        case 'company':
          return a.company.localeCompare(b.company);
        case 'status':
          return a.status.localeCompare(b.status);
        default:
          return 0;
      }
    });

  if (isLoading) {
    return (
      <div className="application-history-container">
        <div className="loading">Loading application history...</div>
      </div>
    );
  }

  return (
    <div className="application-history-container">
      <div className="application-history-header">
        <h1>Application History</h1>
        <div className="application-controls">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search jobs or companies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="filter-sort-controls">
            <div className="control-group">
              <label>Filter by status:</label>
              <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                <option value="all">All Statuses</option>
                <option value="applied">Applied</option>
                <option value="interviewing">Interviewing</option>
                <option value="offered">Offered</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            <div className="control-group">
              <label>Sort by:</label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="date">Date Applied</option>
                <option value="company">Company</option>
                <option value="status">Status</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="applications-list">
        {filteredApplications.length === 0 ? (
          <div className="no-applications">
            {searchQuery 
              ? "No applications found matching your search."
              : filterStatus === 'all'
                ? "You haven't applied to any jobs yet."
                : `No applications with status "${filterStatus}" found.`}
          </div>
        ) : (
          filteredApplications.map(app => (
            <div key={app.id} className="application-card">
              <div className="application-header">
                <div className="application-title" onClick={() => handleJobClick(app.id)}>
                  <h3>{app.jobTitle}</h3>
                  <p className="company">{app.company}</p>
                  <p className="location">{app.location}</p>
                </div>
                <div className="application-status">
                  <select 
                    value={app.status}
                    onChange={(e) => handleStatusChange(e, app.id)}
                    className={`status-select ${app.status}`}
                  >
                    <option value="applied">Applied</option>
                    <option value="interviewing">Interviewing</option>
                    <option value="offered">Offered</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>
              </div>

              <div className="application-details">
                <div className="application-dates">
                  <div className="date-info">
                    <span className="label">Applied:</span>
                    <span className="value">{app.appliedDate.toLocaleDateString()}</span>
                  </div>
                  <div className="date-info">
                    <span className="label">Last Updated:</span>
                    <span className="value">{app.lastUpdated.toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="application-notes">
                  <div className="notes-header">
                    <h4>Application Notes</h4>
                    <button 
                      className="add-note-btn"
                      onClick={() => handleAddNote(app.id)}
                    >
                      Add Note
                    </button>
                  </div>
                  <ul className="notes-list">
                    {app.notes.map((note, index) => (
                      <li key={index}>{note}</li>
                    ))}
                  </ul>
                </div>

                {app.nextSteps && (
                  <div className="next-steps">
                    <h4>Next Steps</h4>
                    <p>{app.nextSteps}</p>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ApplicationHistory; 