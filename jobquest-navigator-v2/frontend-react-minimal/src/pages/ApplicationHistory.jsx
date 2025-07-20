import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import graphqlApplicationService from '../services/graphqlApplicationService';
import './ApplicationHistory.css';

const ApplicationHistory = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [applications, setApplications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (user) {
      fetchApplications();
    }
  }, [user]);

  const fetchApplications = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await graphqlApplicationService.getApplications();
      const applicationsData = response.results || response;
      setApplications(applicationsData);
    } catch (err) {
      console.error('Error fetching applications:', err);
      setError('Failed to load job applications. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStatusChange = async (e, applicationId) => {
    const newStatus = e.target.value;
    
    try {
      await graphqlApplicationService.updateApplication(applicationId, { status: newStatus });
      
      // Update local state
      setApplications(prev => prev.map(app => 
        app.id === applicationId ? { ...app, status: newStatus, last_updated: new Date().toISOString() } : app
      ));
    } catch (err) {
      console.error('Error updating application status:', err);
      setError('Failed to update application status. Please try again.');
    }
  };

  const handleAddNote = async (applicationId) => {
    const note = prompt('Enter a new note:');
    if (note) {
      try {
        // Find the current application to get existing notes
        const currentApp = applications.find(app => app.id === applicationId);
        const updatedNotes = currentApp.notes ? `${currentApp.notes}\n\n${note}` : note;
        
        await graphqlApplicationService.updateApplication(applicationId, { 
          notes: updatedNotes 
        });
        
        // Update local state
        setApplications(prev => prev.map(app => 
          app.id === applicationId 
            ? { 
                ...app, 
                notes: updatedNotes,
                last_updated: new Date().toISOString()
              } 
            : app
        ));
      } catch (err) {
        console.error('Error adding note:', err);
        setError('Failed to add note. Please try again.');
      }
    }
  };

  const handleJobClick = (jobId) => {
    navigate(`/jobs/${jobId}`);
  };

  const filteredApplications = applications
    .filter(app => {
      const matchesStatus = filterStatus === 'all' || app.status === filterStatus;
      const matchesSearch = searchQuery === '' || 
        app.job?.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        app.job?.company?.name?.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesStatus && matchesSearch;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.applied_date) - new Date(a.applied_date);
        case 'company':
          return (a.job?.company?.name || '').localeCompare(b.job?.company?.name || '');
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

      {error && (
        <div className="error-message" style={{ color: '#e74c3c', padding: '10px', marginBottom: '20px', backgroundColor: '#fdf2f2', border: '1px solid #e74c3c', borderRadius: '4px' }}>
          {error}
        </div>
      )}

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
                <div className="application-title" onClick={() => handleJobClick(app.job?.id)}>
                  <h3>{app.job?.title || 'Job Title Unavailable'}</h3>
                  <p className="company">{app.job?.company?.name || 'Company Unavailable'}</p>
                  <p className="location">{app.job?.location?.city ? `${app.job.location.city}, ${app.job.location.state}` : 'Location Unavailable'}</p>
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
                    <span className="value">{new Date(app.applied_date).toLocaleDateString()}</span>
                  </div>
                  <div className="date-info">
                    <span className="label">Last Updated:</span>
                    <span className="value">{new Date(app.last_updated).toLocaleDateString()}</span>
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
                  <div className="notes-content">
                    {app.notes ? (
                      <div className="notes-text">
                        {app.notes.split('\n\n').map((note, index) => (
                          <p key={index} className="note-item">{note}</p>
                        ))}
                      </div>
                    ) : (
                      <p className="no-notes">No notes added yet.</p>
                    )}
                  </div>
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