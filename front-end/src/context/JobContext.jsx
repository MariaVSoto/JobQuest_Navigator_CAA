import React, { createContext, useState, useEffect } from 'react';

export const JobContext = createContext();

const APP_ID = 'd811904d';
const API_KEY = 'f6dcebd1ea84828498459295555a1cf2';
const COUNTRY = 'us';

export const JobProvider = ({ children }) => {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    company: '',
    type: '',
    remote: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJobs = async () => {
      setLoading(true);
      setError(null);
      let url = `https://api.adzuna.com/v1/api/jobs/${COUNTRY}/search/1?app_id=${APP_ID}&app_key=${API_KEY}&results_per_page=20`;
      if (filters.search) url += `&what=${encodeURIComponent(filters.search)}`;
      if (filters.location) url += `&where=${encodeURIComponent(filters.location)}`;
      if (filters.company) url += `&company=${encodeURIComponent(filters.company)}`;
      if (filters.type) url += `&contract_type=${encodeURIComponent(filters.type.toLowerCase())}`;
      if (filters.remote) url += `&remote=1`;
      try {
        const res = await fetch(url);
        const data = await res.json();
        if (data.results) {
          setJobs(data.results);
        } else {
          setJobs([]);
        }
      } catch (err) {
        setError('Failed to fetch jobs.');
        setJobs([]);
      }
      setLoading(false);
    };
    fetchJobs();
  }, [filters]);

  return (
    <JobContext.Provider value={{ jobs, selectedJob, setSelectedJob, filters, setFilters, loading, error }}>
      {children}
    </JobContext.Provider>
  );
}; 