/**
 * useJobs Hook - Unified job management with GraphQL/REST fallback
 * Provides job-related operations and state management
 */

import { useState, useEffect, useCallback } from 'react';
import unifiedJobService from '../services/unifiedJobService';

export const useJobs = (initialFilters = {}) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [totalJobs, setTotalJobs] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState(initialFilters);

  // Load jobs with current filters
  const loadJobs = useCallback(async (newFilters = {}, page = 1) => {
    try {
      setLoading(true);
      setError(null);

      const searchFilters = {
        ...filters,
        ...newFilters,
        limit: 20,
        offset: (page - 1) * 20
      };

      console.log('🔍 Loading jobs with filters:', searchFilters);

      const response = await unifiedJobService.getJobs(searchFilters);

      if (response && response.results) {
        if (page === 1) {
          // Replace jobs for new search
          setJobs(response.results);
        } else {
          // Append jobs for pagination
          setJobs(prevJobs => [...prevJobs, ...response.results]);
        }
        setTotalJobs(response.count || response.results.length);
        setCurrentPage(page);
      } else if (Array.isArray(response)) {
        // Direct array response
        const pagedResults = response.slice((page - 1) * 20, page * 20);
        if (page === 1) {
          setJobs(pagedResults);
        } else {
          setJobs(prevJobs => [...prevJobs, ...pagedResults]);
        }
        setTotalJobs(response.length);
        setCurrentPage(page);
      } else {
        // No jobs found
        setJobs([]);
        setTotalJobs(0);
        setCurrentPage(1);
      }

      console.log('✅ Jobs loaded successfully');
    } catch (err) {
      console.error('❌ Failed to load jobs:', err);
      setError(`Failed to load jobs: ${err.message}`);
      setJobs([]);
      setTotalJobs(0);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Load more jobs (pagination)
  const loadMoreJobs = useCallback(async () => {
    if (loading || jobs.length >= totalJobs) return;
    
    await loadJobs(filters, currentPage + 1);
  }, [loading, jobs.length, totalJobs, filters, currentPage, loadJobs]);

  // Refresh jobs (reload from beginning)
  const refreshJobs = useCallback(async () => {
    await loadJobs(filters, 1);
  }, [filters, loadJobs]);

  // Update filters and reload
  const updateFilters = useCallback(async (newFilters) => {
    setFilters(prevFilters => ({ ...prevFilters, ...newFilters }));
    await loadJobs(newFilters, 1);
  }, [loadJobs]);

  // Clear all filters
  const clearFilters = useCallback(async () => {
    const clearedFilters = {
      search: '',
      location: '',
      company: '',
      type: '',
      experience_level: '',
      remote_type: '',
      salary_min: '',
      sort: ''
    };
    setFilters(clearedFilters);
    await loadJobs(clearedFilters, 1);
  }, [loadJobs]);

  // Get a specific job by ID
  const getJob = useCallback(async (jobId) => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔍 Loading job details for:', jobId);
      const job = await unifiedJobService.getJob(jobId);
      console.log('✅ Job details loaded');
      return job;
    } catch (err) {
      console.error('❌ Failed to load job details:', err);
      setError(`Failed to load job: ${err.message}`);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Create a new job
  const createJob = useCallback(async (jobData) => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔨 Creating new job:', jobData.title);
      const result = await unifiedJobService.createJob(jobData);
      
      if (result.success) {
        console.log('✅ Job created successfully');
        // Refresh the job list to include the new job
        await refreshJobs();
        return result;
      } else {
        throw new Error(result.message || 'Failed to create job');
      }
    } catch (err) {
      console.error('❌ Failed to create job:', err);
      setError(`Failed to create job: ${err.message}`);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [refreshJobs]);

  // Save a job
  const saveJob = useCallback(async (jobId, notes = '') => {
    try {
      console.log('💾 Saving job:', jobId);
      const result = await unifiedJobService.saveJob(jobId, notes);
      
      // Update local state to reflect saved status
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId ? { ...job, isSaved: true, is_saved: true } : job
        )
      );

      console.log('✅ Job saved successfully');
      return result;
    } catch (err) {
      console.error('❌ Failed to save job:', err);
      setError(`Failed to save job: ${err.message}`);
      return { success: false, error: err.message };
    }
  }, []);

  // Unsave a job
  const unsaveJob = useCallback(async (jobId) => {
    try {
      console.log('🗑️ Unsaving job:', jobId);
      const result = await unifiedJobService.saveJob(jobId); // Toggle behavior
      
      // Update local state to reflect unsaved status
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId ? { ...job, isSaved: false, is_saved: false } : job
        )
      );

      console.log('✅ Job unsaved successfully');
      return result;
    } catch (err) {
      console.error('❌ Failed to unsave job:', err);
      setError(`Failed to unsave job: ${err.message}`);
      return { success: false, error: err.message };
    }
  }, []);

  // Apply to a job
  const applyToJob = useCallback(async (jobId, applicationData = {}) => {
    try {
      console.log('📝 Applying to job:', jobId);
      const result = await unifiedJobService.applyToJob(jobId, applicationData);
      
      // Update local state to reflect applied status
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId ? { ...job, isApplied: true, is_applied: true } : job
        )
      );

      console.log('✅ Applied to job successfully');
      return result;
    } catch (err) {
      console.error('❌ Failed to apply to job:', err);
      setError(`Failed to apply to job: ${err.message}`);
      return { success: false, error: err.message };
    }
  }, []);

  // Search jobs
  const searchJobs = useCallback(async (query, additionalFilters = {}) => {
    const searchFilters = {
      ...additionalFilters,
      search: query
    };
    await updateFilters(searchFilters);
  }, [updateFilters]);

  // Get jobs by location
  const getJobsByLocation = useCallback(async (location, additionalFilters = {}) => {
    const locationFilters = {
      ...additionalFilters,
      location: location
    };
    await updateFilters(locationFilters);
  }, [updateFilters]);

  // Get remote jobs
  const getRemoteJobs = useCallback(async (additionalFilters = {}) => {
    const remoteFilters = {
      ...additionalFilters,
      remote_type: 'remote'
    };
    await updateFilters(remoteFilters);
  }, [updateFilters]);

  // Get job statistics
  const getJobStats = useCallback(async () => {
    try {
      console.log('📊 Loading job statistics...');
      const stats = await unifiedJobService.getJobStats();
      console.log('✅ Job statistics loaded');
      return stats;
    } catch (err) {
      console.error('❌ Failed to load job statistics:', err);
      return {
        total: 0,
        byType: {},
        byLocation: {},
        byExperience: {},
        byRemoteType: {},
        saved: 0,
        applied: 0,
      };
    }
  }, []);

  // Initial load effect
  useEffect(() => {
    loadJobs(filters, 1);
  }, []); // Empty dependency array for initial load only

  // Computed values
  const hasMore = jobs.length < totalJobs;
  const isEmpty = !loading && jobs.length === 0;
  const isInitialLoading = loading && jobs.length === 0;

  return {
    // State
    jobs,
    loading,
    error,
    totalJobs,
    currentPage,
    filters,
    hasMore,
    isEmpty,
    isInitialLoading,

    // Actions
    loadJobs,
    loadMoreJobs,
    refreshJobs,
    updateFilters,
    clearFilters,
    getJob,
    createJob,
    saveJob,
    unsaveJob,
    applyToJob,
    searchJobs,
    getJobsByLocation,
    getRemoteJobs,
    getJobStats,

    // Utilities
    setError: (error) => setError(error),
    clearError: () => setError(null),
  };
};

export default useJobs;