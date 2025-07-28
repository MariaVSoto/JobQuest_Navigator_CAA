/**
 * useApplications Hook - Unified application management with GraphQL
 * Provides application-related operations and state management
 */

import { useState, useEffect, useCallback } from 'react';
import graphqlApplicationService from '../services/graphqlApplicationService';

export const useApplications = (initialFilters = {}) => {
  const [applications, setApplications] = useState([]);
  const [savedJobs, setSavedJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [totalApplications, setTotalApplications] = useState(0);
  const [totalSavedJobs, setTotalSavedJobs] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState(initialFilters);

  // Load applications with current filters
  const loadApplications = useCallback(async (newFilters = {}, page = 1) => {
    try {
      setLoading(true);
      setError(null);

      const searchFilters = {
        ...filters,
        ...newFilters,
        limit: 20,
        offset: (page - 1) * 20
      };

      console.log('📋 Loading applications with filters:', searchFilters);

      const response = await graphqlApplicationService.getApplications(searchFilters);

      if (response && response.results) {
        if (page === 1) {
          // Replace applications for new search
          setApplications(response.results);
        } else {
          // Append applications for pagination
          setApplications(prevApps => [...prevApps, ...response.results]);
        }
        setTotalApplications(response.count || response.results.length);
        setCurrentPage(page);
      } else {
        // No applications found
        setApplications([]);
        setTotalApplications(0);
        setCurrentPage(1);
      }

      console.log('✅ Applications loaded successfully');
    } catch (err) {
      console.error('❌ Failed to load applications:', err);
      // Fallback to mock data
      const mockApplications = graphqlApplicationService.getMockApplicationData();
      setApplications(mockApplications);
      setTotalApplications(mockApplications.length);
      setError(`Using demo data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Load saved jobs
  const loadSavedJobs = useCallback(async (newFilters = {}, page = 1) => {
    try {
      setLoading(true);
      setError(null);

      const searchFilters = {
        ...newFilters,
        limit: 20,
        offset: (page - 1) * 20
      };

      console.log('💾 Loading saved jobs with filters:', searchFilters);

      const response = await graphqlApplicationService.getSavedJobs(searchFilters);

      if (response && response.results) {
        if (page === 1) {
          // Replace saved jobs for new search
          setSavedJobs(response.results);
        } else {
          // Append saved jobs for pagination
          setSavedJobs(prevSaved => [...prevSaved, ...response.results]);
        }
        setTotalSavedJobs(response.count || response.results.length);
      } else {
        // No saved jobs found
        setSavedJobs([]);
        setTotalSavedJobs(0);
      }

      console.log('✅ Saved jobs loaded successfully');
    } catch (err) {
      console.error('❌ Failed to load saved jobs:', err);
      // Fallback to mock data
      const mockSavedJobs = graphqlApplicationService.getMockSavedJobData();
      setSavedJobs(mockSavedJobs);
      setTotalSavedJobs(mockSavedJobs.length);
      setError(`Using demo data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load more applications (pagination)
  const loadMoreApplications = useCallback(async () => {
    if (loading || applications.length >= totalApplications) return;
    
    await loadApplications(filters, currentPage + 1);
  }, [loading, applications.length, totalApplications, filters, currentPage, loadApplications]);

  // Refresh applications (reload from beginning)
  const refreshApplications = useCallback(async () => {
    await loadApplications(filters, 1);
  }, [filters, loadApplications]);

  // Refresh saved jobs
  const refreshSavedJobs = useCallback(async () => {
    await loadSavedJobs({}, 1);
  }, [loadSavedJobs]);

  // Update filters and reload
  const updateFilters = useCallback(async (newFilters) => {
    setFilters(prevFilters => ({ ...prevFilters, ...newFilters }));
    await loadApplications(newFilters, 1);
  }, [loadApplications]);

  // Get a specific application by ID
  const getApplication = useCallback(async (applicationId) => {
    try {
      setLoading(true);
      setError(null);

      console.log('📋 Loading application details for:', applicationId);
      const application = await graphqlApplicationService.getApplication(applicationId);
      console.log('✅ Application details loaded');
      return application;
    } catch (err) {
      console.error('❌ Failed to load application details:', err);
      setError(`Failed to load application: ${err.message}`);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Create a new application
  const createApplication = useCallback(async (applicationData) => {
    try {
      setLoading(true);
      setError(null);

      console.log('📝 Creating new application for job:', applicationData.jobId || applicationData.job_id);
      const result = await graphqlApplicationService.createApplication(applicationData);
      
      if (result.success) {
        console.log('✅ Application created successfully');
        // Add the new application to the beginning of the list
        setApplications(prevApps => [result.data, ...prevApps]);
        setTotalApplications(prev => prev + 1);
        return result;
      } else {
        throw new Error(result.message || 'Failed to create application');
      }
    } catch (err) {
      console.error('❌ Failed to create application:', err);
      setError(`Failed to create application: ${err.message}`);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Update an application
  const updateApplication = useCallback(async (applicationId, applicationData) => {
    try {
      setLoading(true);
      setError(null);

      console.log('📝 Updating application:', applicationId);
      const result = await graphqlApplicationService.updateApplication(applicationId, applicationData);
      
      if (result.success) {
        console.log('✅ Application updated successfully');
        // Update the application in the list
        setApplications(prevApps => 
          prevApps.map(app => 
            app.id === applicationId ? { ...app, ...result.data } : app
          )
        );
        return result;
      } else {
        throw new Error(result.message || 'Failed to update application');
      }
    } catch (err) {
      console.error('❌ Failed to update application:', err);
      setError(`Failed to update application: ${err.message}`);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Save a job
  const saveJob = useCallback(async (jobId, notes = '') => {
    try {
      console.log('💾 Saving job:', jobId);
      const result = await graphqlApplicationService.saveJob(jobId, notes);
      
      if (result.success) {
        console.log('✅ Job saved successfully');
        // Add the saved job to the beginning of the list
        setSavedJobs(prevSaved => [result.data, ...prevSaved]);
        setTotalSavedJobs(prev => prev + 1);
        return result;
      } else {
        throw new Error(result.message || 'Failed to save job');
      }
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
      const result = await graphqlApplicationService.unsaveJob(jobId);
      
      if (result.success) {
        console.log('✅ Job unsaved successfully');
        // Remove the job from the saved jobs list
        setSavedJobs(prevSaved => prevSaved.filter(saved => saved.job_id !== jobId));
        setTotalSavedJobs(prev => Math.max(0, prev - 1));
        return result;
      } else {
        throw new Error(result.message || 'Failed to unsave job');
      }
    } catch (err) {
      console.error('❌ Failed to unsave job:', err);
      setError(`Failed to unsave job: ${err.message}`);
      return { success: false, error: err.message };
    }
  }, []);

  // Filter applications by status
  const getApplicationsByStatus = useCallback(async (status) => {
    const statusFilters = {
      ...filters,
      status: status
    };
    await updateFilters(statusFilters);
  }, [filters, updateFilters]);

  // Get application statistics
  const getApplicationStats = useCallback(async () => {
    try {
      console.log('📊 Loading application statistics...');
      const stats = await graphqlApplicationService.getApplicationStats();
      console.log('✅ Application statistics loaded');
      return stats;
    } catch (err) {
      console.error('❌ Failed to load application statistics:', err);
      return {
        total: 0,
        byStatus: {},
        recent: 0,
      };
    }
  }, []);

  // Check if a job is saved
  const isJobSaved = useCallback((jobId) => {
    return savedJobs.some(saved => saved.job_id === jobId);
  }, [savedJobs]);

  // Check if a job has been applied to
  const isJobApplied = useCallback((jobId) => {
    return applications.some(app => app.job_id === jobId);
  }, [applications]);

  // Get application for a specific job
  const getApplicationForJob = useCallback((jobId) => {
    return applications.find(app => app.job_id === jobId);
  }, [applications]);

  // Initial load effect
  useEffect(() => {
    loadApplications(filters, 1);
    loadSavedJobs({}, 1);
  }, []); // Empty dependency array for initial load only

  // Computed values
  const hasMoreApplications = applications.length < totalApplications;
  const hasMoreSavedJobs = savedJobs.length < totalSavedJobs;
  const isEmpty = !loading && applications.length === 0 && savedJobs.length === 0;
  const isInitialLoading = loading && applications.length === 0 && savedJobs.length === 0;

  // Status statistics
  const applicationsByStatus = applications.reduce((stats, app) => {
    stats[app.status] = (stats[app.status] || 0) + 1;
    return stats;
  }, {});

  return {
    // State
    applications,
    savedJobs,
    loading,
    error,
    totalApplications,
    totalSavedJobs,
    currentPage,
    filters,
    hasMoreApplications,
    hasMoreSavedJobs,
    isEmpty,
    isInitialLoading,
    applicationsByStatus,

    // Actions
    loadApplications,
    loadSavedJobs,
    loadMoreApplications,
    refreshApplications,
    refreshSavedJobs,
    updateFilters,
    getApplication,
    createApplication,
    updateApplication,
    saveJob,
    unsaveJob,
    getApplicationsByStatus,
    getApplicationStats,

    // Utilities
    isJobSaved,
    isJobApplied,
    getApplicationForJob,
    setError: (error) => setError(error),
    clearError: () => setError(null),
  };
};

export default useApplications;