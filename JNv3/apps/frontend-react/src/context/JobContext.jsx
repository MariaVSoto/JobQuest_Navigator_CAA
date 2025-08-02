import React, { createContext, useState, useEffect } from 'react';
import unifiedJobService from '../services/unifiedJobService';
import unifiedUserService from '../services/unifiedUserService';

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
        if (!unifiedUserService.isAuthenticated()) {
          console.log('User not authenticated, skipping job fetch to prevent infinite loop');
          setJobs([]);
          setTotalJobs(0);
          setLoading(false);
          return;
        }

        // Use Django backend instead of external API
        // Default to 20 jobs per page
        const searchFilters = {
          ...filters,
          page_size: 20
        };
        
        const response = await unifiedJobService.getJobs({
          ...searchFilters,
          limit: 20,
          offset: 0
        });
        
        console.log('✅ Jobs loaded via UnifiedJobService:', response);
        
        if (response && response.results) {
          setJobs(response.results);
          setTotalJobs(response.count || response.results.length);
        } else if (Array.isArray(response)) {
          // Direct array response
          setJobs(response.slice(0, 20));
          setTotalJobs(response.length);
        } else {
          // No jobs found
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
      const response = await unifiedJobService.getJobs({ 
        ...filters, 
        limit: 20,
        offset: (page - 1) * 20
      });
      
      if (response && response.results) {
        setJobs(prevJobs => [...prevJobs, ...response.results]);
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
      const result = await unifiedJobService.saveJob(jobId, notes);
      // Update local state to reflect saved status
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId ? { ...job, isSaved: true, is_saved: true } : job
        )
      );
      return result;
    } catch (err) {
      console.error('Failed to save job:', err);
      return { success: false, error: err.message };
    }
  };

  // Function to unsave a job
  const unsaveJob = async (jobId) => {
    try {
      const result = await unifiedJobService.saveJob(jobId); // Same endpoint, toggle behavior
      // Update local state to reflect unsaved status
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId ? { ...job, isSaved: false, is_saved: false } : job
        )
      );
      return result;
    } catch (err) {
      console.error('Failed to unsave job:', err);
      return { success: false, error: err.message };
    }
  };

  // Function to apply to a job
  const applyToJob = async (jobId, applicationData) => {
    try {
      const result = await unifiedJobService.applyToJob(jobId, applicationData);
      // Update local state to reflect applied status
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId ? { ...job, isApplied: true, is_applied: true } : job
        )
      );
      return result;
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