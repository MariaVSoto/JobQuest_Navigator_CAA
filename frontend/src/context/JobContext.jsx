import React, { createContext, useState, useEffect } from 'react';
import { jobService } from '../services/jobService';
import authService from '../services/authService';

export const JobContext = createContext();

export const JobProvider = ({ children }) => {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    company: '',
    type: '',
    experience_level: '',
    remote_type: '',
    salary_min: '',
    sort: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [totalJobs, setTotalJobs] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const fetchJobs = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Check if user is authenticated first
        if (!authService.isAuthenticated()) {
          // For jobs listing, we can show public jobs or require login
          // For demo purposes, let's continue without authentication
          console.log('User not authenticated, but continuing to fetch jobs for demo');
        }

        // Use Django backend instead of external API
        // Default to 20 jobs per page
        const searchFilters = {
          ...filters,
          page_size: 20
        };
        
        const response = await jobService.searchJobs(searchFilters);
        
        if (response) {
          // Handle both paginated and non-paginated responses
          if (response.results) {
            // Paginated response
            const transformedJobs = jobService.transformJobsResponse(response);
            setJobs(transformedJobs.results);
            setTotalJobs(response.count || transformedJobs.results.length);
          } else if (Array.isArray(response)) {
            // Direct array response
            const transformedJobs = jobService.transformJobsResponse(response);
            // Limit to 20 jobs for display
            const limitedJobs = transformedJobs.slice(0, 20);
            setJobs(limitedJobs);
            setTotalJobs(transformedJobs.length);
          } else {
            // Single job or other format
            setJobs([]);
            setTotalJobs(0);
          }
        } else {
          setJobs([]);
          setTotalJobs(0);
        }
      } catch (err) {
        console.error('Failed to fetch jobs:', err);
        setError(`Failed to fetch jobs: ${err.message}`);
        setJobs([]);
        setTotalJobs(0);
      }
      
      setLoading(false);
    };

    fetchJobs();
  }, [filters, currentPage]);

  // Function to load more jobs (for pagination)
  const loadMoreJobs = async (page = currentPage + 1) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await jobService.searchJobs({ 
        ...filters, 
        page,
        page_size: 20
      });
      
      if (response && response.results) {
        const transformedJobs = jobService.transformJobsResponse(response);
        setJobs(prevJobs => [...prevJobs, ...transformedJobs.results]);
        setCurrentPage(page);
      }
    } catch (err) {
      console.error('Failed to load more jobs:', err);
      setError(`Failed to load more jobs: ${err.message}`);
    }
    
    setLoading(false);
  };

  // Function to refresh jobs
  const refreshJobs = () => {
    setCurrentPage(1);
    setJobs([]);
  };

  // Function to save a job
  const saveJob = async (jobId, notes = '') => {
    try {
      await jobService.saveJob(jobId, notes);
      return { success: true };
    } catch (err) {
      console.error('Failed to save job:', err);
      return { success: false, error: err.message };
    }
  };

  // Function to unsave a job
  const unsaveJob = async (jobId) => {
    try {
      await jobService.unsaveJob(jobId);
      return { success: true };
    } catch (err) {
      console.error('Failed to unsave job:', err);
      return { success: false, error: err.message };
    }
  };

  // Function to apply to a job
  const applyToJob = async (jobId, applicationData) => {
    try {
      const response = await jobService.applyToJob(jobId, applicationData);
      return { success: true, data: response };
    } catch (err) {
      console.error('Failed to apply to job:', err);
      return { success: false, error: err.message };
    }
  };

  const contextValue = {
    // Job data
    jobs,
    setJobs,
    selectedJob,
    setSelectedJob,
    totalJobs,
    currentPage,
    
    // Filters and search
    filters,
    setFilters,
    
    // Loading states
    loading,
    error,
    
    // Actions
    loadMoreJobs,
    refreshJobs,
    saveJob,
    unsaveJob,
    applyToJob,
  };

  return (
    <JobContext.Provider value={contextValue}>
      {children}
    </JobContext.Provider>
  );
}; 