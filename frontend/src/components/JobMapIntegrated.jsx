import React, { useState, useContext, useCallback, useRef } from 'react';
import { GoogleMap, Marker, useJsApiLoader } from '@react-google-maps/api';
import { JobContext } from '../context/JobContext';
import './JobMapIntegrated.css';

const containerStyle = {
  width: '100%',
  height: '280px',
  borderRadius: '12px',
  marginBottom: '1rem',
};

const defaultCenter = { lat: 39.8283, lng: -98.5795 }; // Center of USA

const JobMapIntegrated = () => {
  const { jobs, selectedJob, setSelectedJob, loading, error } = useContext(JobContext);
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

  // Only show jobs with valid lat/lng
  const jobsWithCoords = jobs.filter(job => job.latitude && job.longitude);

  // Handle job selection from map
  const handleJobClick = (job) => {
    setSelectedJob(job);
  };

  return (
    <div className="job-map-integrated">
      <div className="map-header">
        <h3>Job Locations</h3>
        <span className="map-info">
          {jobsWithCoords.length} jobs with location data
        </span>
      </div>
      
      <div className="map-container">
        {loading ? (
          <div className="map-placeholder">
            <div className="loading-spinner"></div>
            <p>Loading job locations...</p>
          </div>
        ) : error ? (
          <div className="map-placeholder error">
            <p>Unable to load map: {error}</p>
          </div>
        ) : !hasGoogleMapsKey ? (
          <div className="map-placeholder">
            <div className="map-fallback">
              <div className="map-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
              </div>
              <h4>Map View Unavailable</h4>
              <p>Google Maps API key required to view job locations on map.</p>
              {jobsWithCoords.length > 0 && (
                <div className="location-list">
                  <h5>Job Locations ({jobsWithCoords.length} jobs):</h5>
                  <div className="location-items">
                    {jobsWithCoords.slice(0, 5).map(job => (
                      <div 
                        key={job.id} 
                        className="location-item"
                        onClick={() => handleJobClick(job)}
                      >
                        <span className="job-title">{job.title}</span>
                        <span className="job-location">
                          {job.location?.city}, {job.location?.country}
                        </span>
                      </div>
                    ))}
                    {jobsWithCoords.length > 5 && (
                      <div className="more-locations">
                        +{jobsWithCoords.length - 5} more locations
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : isLoaded ? (
          <GoogleMap
            mapContainerStyle={containerStyle}
            center={userLocation || defaultCenter}
            zoom={userLocation ? 6 : 4}
            onLoad={onLoad}
            options={{
              styles: [
                {
                  featureType: 'poi',
                  elementType: 'labels',
                  stylers: [{ visibility: 'off' }]
                }
              ]
            }}
          >
            {userLocation && (
              <Marker
                position={userLocation}
                icon={{
                  url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                }}
                title="Your Location"
              />
            )}
            {jobsWithCoords.map(job => (
              <Marker
                key={job.id || job.__unique_id}
                position={{ lat: job.latitude, lng: job.longitude }}
                onClick={() => handleJobClick(job)}
                title={`${job.title} at ${job.company?.name || 'Unknown Company'}`}
                icon={{
                  url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                  scaledSize: new window.google.maps.Size(32, 32)
                }}
              />
            ))}
          </GoogleMap>
        ) : (
          <div className="map-placeholder">
            <div className="loading-spinner"></div>
            <p>Loading map...</p>
          </div>
        )}
      </div>

      {/* Job Details Modal */}
      {selectedJob && (
        <div className="job-modal-overlay" onClick={() => setSelectedJob(null)}>
          <div className="job-modal" onClick={e => e.stopPropagation()}>
            <div className="job-modal-header">
              <h4>{selectedJob.title}</h4>
              <button 
                className="close-btn"
                onClick={() => setSelectedJob(null)}
                aria-label="Close"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            
            <div className="job-modal-content">
              <div className="job-info">
                <p><strong>Company:</strong> {selectedJob.company?.name || 'Unknown Company'}</p>
                <p><strong>Location:</strong> {selectedJob.location?.city}, {selectedJob.location?.country}</p>
                {selectedJob.salary_min && selectedJob.salary_max && (
                  <p><strong>Salary:</strong> ${selectedJob.salary_min} - ${selectedJob.salary_max} {selectedJob.salary_currency}</p>
                )}
                <p><strong>Type:</strong> {selectedJob.job_type?.replace('_', ' ') || 'N/A'}</p>
                <p><strong>Experience:</strong> {selectedJob.experience_level || 'N/A'}</p>
                <p><strong>Remote:</strong> {selectedJob.remote_type?.replace('_', ' ') || 'N/A'}</p>
              </div>
              
              {selectedJob.description && (
                <div className="job-description">
                  <strong>Description:</strong>
                  <p>{selectedJob.description.substring(0, 300)}...</p>
                </div>
              )}
              
              <div className="job-modal-actions">
                <button 
                  className="view-details-btn"
                  onClick={() => window.location.href = `/jobs/${selectedJob.id}`}
                >
                  View Details
                </button>
                <button 
                  className="apply-btn"
                  onClick={() => window.location.href = `/apply/${selectedJob.id}`}
                >
                  Apply Now
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobMapIntegrated;