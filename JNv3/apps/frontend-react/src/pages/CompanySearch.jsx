import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './CompanySearch.css';

const CompanySearch = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [savedCompanies, setSavedCompanies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('search');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newCompany, setNewCompany] = useState({
    name: '',
    industry: '',
    website: '',
    location: '',
    description: '',
    size: '',
    foundedYear: ''
  });

  useEffect(() => {
    fetchSavedCompanies();
  }, []);

  const fetchSavedCompanies = async () => {
    setIsLoading(true);
    try {
      // Mock data for now - replace with actual API call
      const mockCompanies = [
        {
          id: '1',
          name: 'TELUS',
          industry: 'Telecommunications',
          website: 'https://telus.com',
          location: 'Vancouver, Canada',
          description: 'Leading telecommunications company',
          size: '10,000+ employees',
          founded_year: 2000,
          logo_url: 'https://via.placeholder.com/100x100',
          user_added: true
        },
        {
          id: '2',
          name: 'Google',
          industry: 'Technology',
          website: 'https://google.com',
          location: 'Mountain View, CA',
          description: 'Global technology company',
          size: '100,000+ employees',
          founded_year: 1998,
          logo_url: 'https://via.placeholder.com/100x100',
          user_added: false
        }
      ];
      setSavedCompanies(mockCompanies);
    } catch (err) {
      console.error('Error fetching saved companies:', err);
      setError('Failed to load saved companies');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setError(null);

    try {
      // Mock search results - replace with actual API call
      const mockResults = [
        {
          id: 'search-1',
          name: searchQuery,
          industry: 'Technology',
          website: `https://${searchQuery.toLowerCase().replace(/\s+/g, '')}.com`,
          location: 'Unknown',
          description: `Search result for ${searchQuery}`,
          size: 'Unknown',
          founded_year: null,
          logo_url: 'https://via.placeholder.com/100x100',
          match_score: 0.95
        },
        {
          id: 'search-2',
          name: `${searchQuery} Inc`,
          industry: 'Business Services',
          website: '',
          location: 'Unknown',
          description: `Alternative result for ${searchQuery}`,
          size: 'Unknown',
          founded_year: null,
          logo_url: 'https://via.placeholder.com/100x100',
          match_score: 0.8
        }
      ];

      setSearchResults(mockResults);
    } catch (err) {
      console.error('Error searching companies:', err);
      setError('Failed to search companies. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddCompany = async (companyData) => {
    try {
      // Mock API call - replace with actual implementation
      const newCompanyData = {
        id: `user-${Date.now()}`,
        ...companyData,
        user_added: true,
        logo_url: 'https://via.placeholder.com/100x100'
      };

      setSavedCompanies(prev => [newCompanyData, ...prev]);
      setShowAddForm(false);
      setNewCompany({
        name: '',
        industry: '',
        website: '',
        location: '',
        description: '',
        size: '',
        foundedYear: ''
      });
      
      // Show success message
      console.log('Company added successfully:', newCompanyData);
    } catch (err) {
      console.error('Error adding company:', err);
      setError('Failed to add company. Please try again.');
    }
  };

  const handleSaveCompany = async (company) => {
    try {
      // Check if company is already saved
      const isAlreadySaved = savedCompanies.some(saved => saved.name === company.name);
      
      if (isAlreadySaved) {
        setError('Company is already in your saved list');
        return;
      }

      // Mock API call - replace with actual implementation
      const savedCompany = {
        ...company,
        id: `saved-${Date.now()}`,
        user_added: false
      };

      setSavedCompanies(prev => [savedCompany, ...prev]);
      setError(null);
      
      console.log('Company saved successfully:', savedCompany);
    } catch (err) {
      console.error('Error saving company:', err);
      setError('Failed to save company. Please try again.');
    }
  };

  const handleDeleteCompany = async (companyId) => {
    if (!window.confirm('Are you sure you want to remove this company?')) {
      return;
    }

    try {
      setSavedCompanies(prev => prev.filter(company => company.id !== companyId));
      console.log('Company removed successfully');
    } catch (err) {
      console.error('Error removing company:', err);
      setError('Failed to remove company. Please try again.');
    }
  };

  const handleCompanySubmit = (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!newCompany.name.trim()) {
      setError('Company name is required');
      return;
    }

    handleAddCompany(newCompany);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewCompany(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="company-search-container">
      <div className="company-search-header">
        <h1>Company Research</h1>
        <p className="header-subtitle">Search and manage company information for your job applications</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="company-tabs">
        <button
          className={activeTab === 'search' ? 'active' : ''}
          onClick={() => setActiveTab('search')}
        >
          Search Companies
        </button>
        <button
          className={activeTab === 'saved' ? 'active' : ''}
          onClick={() => setActiveTab('saved')}
        >
          My Companies ({savedCompanies.length})
        </button>
        <button
          className={activeTab === 'add' ? 'active' : ''}
          onClick={() => setActiveTab('add')}
        >
          Add Company
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'search' && (
          <div className="search-section">
            <form onSubmit={handleSearch} className="search-form">
              <div className="search-input-group">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for companies by name..."
                  className="search-input"
                />
                <button 
                  type="submit" 
                  className="search-button"
                  disabled={isSearching || !searchQuery.trim()}
                >
                  {isSearching ? 'Searching...' : 'Search'}
                </button>
              </div>
            </form>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="search-results">
                <h3>Search Results</h3>
                <div className="company-grid">
                  {searchResults.map(company => (
                    <div key={company.id} className="company-card">
                      <div className="company-card-header">
                        <div className="company-info">
                          <h3>{company.name}</h3>
                          <div className="company-meta">
                            <span>{company.industry}</span>
                            {company.location && (
                              <>
                                <span>•</span>
                                <span>{company.location}</span>
                              </>
                            )}
                          </div>
                        </div>
                        <div className="match-score">
                          {Math.round(company.match_score * 100)}% match
                        </div>
                      </div>
                      
                      <div className="company-description">
                        <p>{company.description}</p>
                      </div>

                      <div className="company-actions">
                        <button 
                          className="btn btn-primary"
                          onClick={() => handleSaveCompany(company)}
                        >
                          Save Company
                        </button>
                        {company.website && (
                          <button 
                            className="btn btn-secondary"
                            onClick={() => window.open(company.website, '_blank')}
                          >
                            Visit Website
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'saved' && (
          <div className="saved-section">
            {isLoading ? (
              <div className="loading">Loading saved companies...</div>
            ) : savedCompanies.length > 0 ? (
              <div className="company-grid">
                {savedCompanies.map(company => (
                  <div key={company.id} className="company-card">
                    <div className="company-card-header">
                      <div className="company-info">
                        <h3>{company.name}</h3>
                        <div className="company-meta">
                          <span>{company.industry}</span>
                          {company.location && (
                            <>
                              <span>•</span>
                              <span>{company.location}</span>
                            </>
                          )}
                          {company.user_added && (
                            <>
                              <span>•</span>
                              <span className="user-added-badge">User Added</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="company-description">
                      <p>{company.description}</p>
                    </div>

                    <div className="company-details">
                      {company.size && (
                        <div className="detail-item">
                          <span className="label">Size:</span>
                          <span>{company.size}</span>
                        </div>
                      )}
                      {company.founded_year && (
                        <div className="detail-item">
                          <span className="label">Founded:</span>
                          <span>{company.founded_year}</span>
                        </div>
                      )}
                    </div>

                    <div className="company-actions">
                      <button 
                        className="btn btn-primary"
                        onClick={() => navigate(`/company/${company.id}`)}
                      >
                        View Profile
                      </button>
                      {company.website && (
                        <button 
                          className="btn btn-secondary"
                          onClick={() => window.open(company.website, '_blank')}
                        >
                          Website
                        </button>
                      )}
                      <button 
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDeleteCompany(company.id)}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-companies">
                <div className="no-companies-icon">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M3 21h18"/>
                    <path d="M5 21V7l8-4v18"/>
                    <path d="M19 21V11l-6-4"/>
                  </svg>
                </div>
                <h3>No Companies Saved</h3>
                <p>Start by searching for companies or adding them manually.</p>
                <button 
                  onClick={() => setActiveTab('search')}
                  className="btn btn-primary"
                >
                  Search Companies
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'add' && (
          <div className="add-section">
            <div className="add-company-form">
              <h3>Add Company Manually</h3>
              <p>Add company information that you want to research for job applications.</p>
              
              <form onSubmit={handleCompanySubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="name">Company Name *</label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={newCompany.name}
                      onChange={handleInputChange}
                      placeholder="e.g., Apple Inc."
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="industry">Industry</label>
                    <input
                      type="text"
                      id="industry"
                      name="industry"
                      value={newCompany.industry}
                      onChange={handleInputChange}
                      placeholder="e.g., Technology"
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="website">Website</label>
                    <input
                      type="url"
                      id="website"
                      name="website"
                      value={newCompany.website}
                      onChange={handleInputChange}
                      placeholder="https://example.com"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="location">Location</label>
                    <input
                      type="text"
                      id="location"
                      name="location"
                      value={newCompany.location}
                      onChange={handleInputChange}
                      placeholder="e.g., San Francisco, CA"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="description">Description</label>
                  <textarea
                    id="description"
                    name="description"
                    value={newCompany.description}
                    onChange={handleInputChange}
                    placeholder="Brief description of the company..."
                    rows={3}
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="size">Company Size</label>
                    <select
                      id="size"
                      name="size"
                      value={newCompany.size}
                      onChange={handleInputChange}
                    >
                      <option value="">Select size</option>
                      <option value="1-10">1-10 employees</option>
                      <option value="11-50">11-50 employees</option>
                      <option value="51-200">51-200 employees</option>
                      <option value="201-500">201-500 employees</option>
                      <option value="501-1000">501-1000 employees</option>
                      <option value="1001-5000">1001-5000 employees</option>
                      <option value="5000+">5000+ employees</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="foundedYear">Founded Year</label>
                    <input
                      type="number"
                      id="foundedYear"
                      name="foundedYear"
                      value={newCompany.foundedYear}
                      onChange={handleInputChange}
                      placeholder="e.g., 1976"
                      min="1800"
                      max={new Date().getFullYear()}
                    />
                  </div>
                </div>

                <div className="form-actions">
                  <button 
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {
                      setNewCompany({
                        name: '',
                        industry: '',
                        website: '',
                        location: '',
                        description: '',
                        size: '',
                        foundedYear: ''
                      });
                    }}
                  >
                    Clear
                  </button>
                  <button 
                    type="submit"
                    className="btn btn-primary"
                  >
                    Add Company
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompanySearch;