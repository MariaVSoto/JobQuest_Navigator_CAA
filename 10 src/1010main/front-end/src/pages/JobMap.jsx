import React, { useState, useContext, useCallback, useRef } from 'react';
import './JobMap.css';
import { GoogleMap, Marker, useJsApiLoader } from '@react-google-maps/api';
import { JobContext } from '../context/JobContext';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const containerStyle = {
  width: '100%',
  height: '340px',
  borderRadius: '12px',
  marginBottom: '2rem',
};

const defaultCenter = { lat: 39.8283, lng: -98.5795 }; // Center of USA

const JobMap = () => {
  const { jobs, filters, setFilters, selectedJob, setSelectedJob, loading, error } = useContext(JobContext);
  const [userLocation, setUserLocation] = useState(null);
  const mapRef = useRef(null);

  // Check if Google Maps API key is available
  const hasGoogleMapsKey = !!process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: process.env.REACT_APP_GOOGLE_MAPS_API_KEY || '',
  });

  // Get user location on mount
  React.useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        () => {},
        { enableHighAccuracy: true }
      );
    }
  }, []);

  const onLoad = useCallback((map) => {
    mapRef.current = map;
  }, []);

  const handleFilterChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  // Only show jobs with valid lat/lng
  const jobsWithCoords = jobs.filter(job => job.latitude && job.longitude);

  return (
    <div className="jobmap-container">
      <aside className="jobmap-sidebar">
        <h3>Filters</h3>
        <label>Location
          <input name="location" type="text" value={filters.location} onChange={handleFilterChange} placeholder="e.g. New York" />
        </label>
        <label>Company
          <input name="company" type="text" value={filters.company} onChange={handleFilterChange} placeholder="e.g. TechCorp" />
        </label>
        <label>Job Type
          <select name="type" value={filters.type} onChange={handleFilterChange}>
            <option value="">All</option>
            <option value="Full-time">Full-time</option>
            <option value="Part-time">Part-time</option>
            <option value="Contract">Contract</option>
          </select>
        </label>
        <label className="remote-checkbox">
          <input name="remote" type="checkbox" checked={filters.remote} onChange={handleFilterChange} /> Remote only
        </label>
      </aside>
      <main className="jobmap-main">
        {/* <img src={logo} alt="JobQuest Logo" className="jobmap-logo" /> */}
        <h1 className="jobmap-title">Job Map</h1>
        <div className="jobmap-searchbar">
          <input
            name="search"
            type="text"
            value={filters.search}
            onChange={handleFilterChange}
            placeholder="Search job titles..."
          />
        </div>
        <div className="jobmap-maparea">
          {loading ? (
            <div className="map-placeholder">Loading jobs...</div>
          ) : error ? (
            <div className="map-placeholder">{error}</div>
          ) : !hasGoogleMapsKey ? (
            <div className="map-placeholder">
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <h3>Google Maps API Key Required</h3>
                <p>To view jobs on the map, please add your Google Maps API key to the .env file.</p>
                <p>Found {jobsWithCoords.length} jobs with location data.</p>
                {jobsWithCoords.length > 0 && (
                  <div style={{ marginTop: '20px' }}>
                    <h4>Available Jobs:</h4>
                    <div style={{ maxHeight: '200px', overflowY: 'auto', textAlign: 'left' }}>
                      {jobsWithCoords.map(job => (
                        <div key={job.id} style={{ padding: '10px', border: '1px solid #ddd', margin: '5px', borderRadius: '4px', cursor: 'pointer' }}
                             onClick={() => setSelectedJob(job)}>
                          <strong>{job.title}</strong><br/>
                          <span>{job.company?.display_name}</span><br/>
                          <span>{job.location?.display_name}</span><br/>
                          <small>Coordinates: {job.latitude}, {job.longitude}</small><br/>
                          <small style={{ color: '#666' }}>Click to view details</small>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : isLoaded ? (
            <GoogleMap
              mapContainerStyle={containerStyle}
              center={userLocation || defaultCenter}
              zoom={userLocation ? 5 : 4}
              onLoad={onLoad}
            >
              {userLocation && (
                <Marker
                  position={userLocation}
                  icon={{
                    url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                  }}
                />
              )}
              {jobsWithCoords.map(job => (
                <Marker
                  key={job.id || job.__unique_id}
                  position={{ lat: job.latitude, lng: job.longitude }}
                  onClick={() => setSelectedJob(job)}
                />
              ))}
            </GoogleMap>
          ) : (
            <div className="map-placeholder">Loading map...</div>
          )}
        </div>
        {selectedJob && (
          <div className="jobmap-modal">
            <div className="jobmap-modal-content">
              <h4>{selectedJob.title}</h4>
              <p><strong>Company:</strong> {selectedJob.company?.display_name || 'Unknown Company'}</p>
              <p><strong>Location:</strong> {selectedJob.location?.display_name || 'Unknown Location'}</p>
              {selectedJob.salary_min && selectedJob.salary_max && (
                <p><strong>Salary:</strong> ${selectedJob.salary_min} - ${selectedJob.salary_max} {selectedJob.salary_currency}/{selectedJob.salary_period}</p>
              )}
              <p><strong>Type:</strong> {selectedJob.job_type?.replace('_', ' ') || 'N/A'}</p>
              <p><strong>Experience:</strong> {selectedJob.experience_level || 'N/A'}</p>
              <p><strong>Remote:</strong> {selectedJob.remote_type?.replace('_', ' ') || 'N/A'}</p>
              {selectedJob.description && (
                <div style={{ marginTop: '10px', maxHeight: '100px', overflowY: 'auto' }}>
                  <strong>Description:</strong>
                  <p style={{ fontSize: '0.9em', color: '#666' }}>{selectedJob.description.substring(0, 200)}...</p>
                </div>
              )}
              <div style={{ marginTop: '15px' }}>
                <button className="apply-btn" onClick={() => window.location.href = `/apply/${selectedJob.id}`}>Apply Now</button>
                <button className="close-btn" onClick={() => setSelectedJob(null)}>Close</button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default JobMap; 