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

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: process.env.REACT_APP_GOOGLE_MAPS_API_KEY,
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
                  key={job.id || job.__unique_id || job.redirect_url}
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
              <p>{selectedJob.company?.display_name || 'Unknown Company'}</p>
              <p>{selectedJob.location?.display_name || 'Unknown Location'}</p>
              <button className="apply-btn" onClick={() => window.location.href = `/apply/${selectedJob.id || selectedJob.__unique_id || selectedJob.redirect_url}`}>Apply</button>
              <button className="close-btn" onClick={() => setSelectedJob(null)}>Close</button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default JobMap; 