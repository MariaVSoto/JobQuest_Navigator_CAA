import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import unifiedJobService from '../services/unifiedJobService';
import companyResearchService from '../services/companyResearchService';
import './CompanyProfile.css';

const CompanyProfile = () => {
  const { companyId } = useParams();
  const { user } = useAuth();
  const [company, setCompany] = useState(null);
  const [companyResearch, setCompanyResearch] = useState(null);
  const [companyJobs, setCompanyJobs] = useState([]);
  const [companyInsights, setCompanyInsights] = useState([]);
  const [companyNews, setCompanyNews] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingResearch, setIsGeneratingResearch] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCompanyData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Mock company data - replace with actual API when available
        const mockCompanyData = {
          id: companyId,
          name: 'TELUS',
          description: 'About the job Join Our Team And What We\'ll Accomplish Together We are a service management team that equips organizations to be agile and innovative, focusing on process-driven solutions to be productive, creative, and create value for business stakeholders. We foster a "think service management first" mindset to build solutions using best practices for the workplace of tomorrow, enabling businesses to drive optimization and workforce excellence.',
          industry: 'Telecommunications',
          size: '10,000+ employees',
          location: 'Vancouver, Canada',
          website: 'https://telus.com',
          founded_year: 2000,
          // Remove logo to fix display issue
          logo_url: null
        };
        
        setCompany(mockCompanyData);

        // Mock company jobs
        const mockJobs = [
          {
            id: '1',
            title: 'Enterprise Architect',
            job_type: 'full_time',
            contract_type: 'permanent',
            location: { display_name: 'hybrid' },
            created_at: new Date().toISOString(),
            salary_min: 120000,
            salary_max: 180000
          },
          {
            id: '2',
            title: 'Senior Software Developer',
            job_type: 'full_time',
            contract_type: 'permanent', 
            location: { display_name: 'remote' },
            created_at: new Date().toISOString(),
            salary_min: 100000,
            salary_max: 140000
          }
        ];
        setCompanyJobs(mockJobs);

        // Mock research data
        const mockResearch = {
          id: '1',
          title: 'TELUS Company Research',
          research_date: new Date().toISOString(),
          confidence_score: 0.92,
          overview: 'TELUS is a leading telecommunications company in Canada, known for innovation in digital services and customer experience.',
          culture_analysis: 'TELUS promotes a collaborative culture focused on giving back to communities and environmental sustainability.',
          recent_news: 'Recent expansion into healthcare technology and 5G infrastructure development.',
          financial_highlights: 'Strong revenue growth and investment in digital transformation initiatives.',
          growth_prospects: 'Expanding into health tech, agriculture tech, and sustainable technology solutions.',
          is_saved: false
        };
        setCompanyResearch(mockResearch);

        // Mock insights
        const mockInsights = [
          {
            id: '1',
            title: 'Company Culture',
            insight_type_display: 'Culture',
            content: 'Strong focus on employee wellbeing and community involvement.',
            source: 'Employee reviews'
          }
        ];
        setCompanyInsights(mockInsights);

        // Mock news
        const mockNews = [
          {
            id: '1',
            title: 'TELUS announces new sustainability initiatives',
            summary: 'Company commits to carbon neutrality by 2030.',
            source: 'TELUS Press Release',
            published_date: new Date().toISOString(),
            relevance_score: 0.8,
            url: 'https://telus.com/news'
          }
        ];
        setCompanyNews(mockNews);

      } catch (err) {
        console.error('Error fetching company data:', err);
        setError('Failed to load company information. Please try again later.');
        setCompany(null);
      } finally {
        setIsLoading(false);
      }
    };

    if (companyId) {
      fetchCompanyData();
    }
  }, [companyId]);

  const handleGenerateResearch = async () => {
    if (!user) {
      setError('Please log in to generate company research');
      return;
    }

    setIsGeneratingResearch(true);
    try {
      const research = await companyResearchService.generateCompanyResearch(companyId);
      setCompanyResearch(research);
      setError(null);
    } catch (err) {
      console.error('Error generating research:', err);
      setError('Failed to generate company research');
    } finally {
      setIsGeneratingResearch(false);
    }
  };

  const handleSaveResearch = async () => {
    if (!companyResearch) return;

    try {
      await companyResearchService.saveResearchItem(companyResearch.id);
      setCompanyResearch(prev => ({ ...prev, is_saved: true }));
    } catch (err) {
      console.error('Error saving research:', err);
      setError('Failed to save research');
    }
  };

  if (isLoading) {
    return <div className="loading">Loading company information...</div>;
  }

  if (error && !company) {
    return (
      <div className="company-profile-container">
        <div className="error-container">
          <h2>Company Not Found</h2>
          <p>{error}</p>
          <button onClick={() => window.history.back()} className="back-button">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="company-profile-container">
      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Company Header */}
      <div className="company-header">
        {company.logo_url && (
          <div className="company-logo">
            <img src={company.logo_url} alt={company.name} />
          </div>
        )}
        <div className="company-info">
          <h1>{company.name}</h1>
          <div className="company-meta">
            <span>{company.industry}</span>
            <span>•</span>
            <span>{company.size}</span>
            <span>•</span>
            <span>{company.location}</span>
          </div>
          <div className="company-actions">
            {user && (
              <>
                {!companyResearch ? (
                  <button 
                    className="research-button" 
                    onClick={handleGenerateResearch}
                    disabled={isGeneratingResearch}
                  >
                    {isGeneratingResearch ? 'Generating...' : 'Generate Research'}
                  </button>
                ) : (
                  <button 
                    className="save-button" 
                    onClick={handleSaveResearch}
                    disabled={companyResearch.is_saved}
                  >
                    {companyResearch.is_saved ? 'Saved' : 'Save Research'}
                  </button>
                )}
              </>
            )}
            {company.website && (
              <button className="website-button" onClick={() => window.open(company.website, '_blank')}>
                Visit Website
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="company-tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={activeTab === 'research' ? 'active' : ''}
          onClick={() => setActiveTab('research')}
        >
          Research & Insights
        </button>
        <button
          className={activeTab === 'jobs' ? 'active' : ''}
          onClick={() => setActiveTab('jobs')}
        >
          Open Positions ({companyJobs.length})
        </button>
        <button
          className={activeTab === 'news' ? 'active' : ''}
          onClick={() => setActiveTab('news')}
        >
          News & Updates
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <div className="company-description">
              <h2>About {company.name}</h2>
              <p>{company.description}</p>
            </div>
            <div className="company-details">
              <div className="detail-item">
                <h3>Founded</h3>
                <p>{company.founded_year || company.founded || 'N/A'}</p>
              </div>
              <div className="detail-item">
                <h3>Company Size</h3>
                <p>{company.size || 'N/A'}</p>
              </div>
              <div className="detail-item">
                <h3>Industry</h3>
                <p>{company.industry || 'N/A'}</p>
              </div>
              <div className="detail-item">
                <h3>Location</h3>
                <p>{company.location || 'N/A'}</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'research' && (
          <div className="research-section">
            {companyResearch ? (
              <div className="research-content">
                <div className="research-header">
                  <h2>{companyResearch.title}</h2>
                  <div className="research-meta">
                    <span>Generated: {new Date(companyResearch.research_date).toLocaleDateString()}</span>
                    <span>•</span>
                    <span>Confidence: {Math.round(companyResearch.confidence_score * 100)}%</span>
                  </div>
                </div>

                <div className="research-sections">
                  <div className="research-item">
                    <h3>Company Overview</h3>
                    <p>{companyResearch.overview}</p>
                  </div>

                  <div className="research-item">
                    <h3>Culture Analysis</h3>
                    <p>{companyResearch.culture_analysis}</p>
                  </div>

                  {companyResearch.recent_news && (
                    <div className="research-item">
                      <h3>Recent News</h3>
                      <p>{companyResearch.recent_news}</p>
                    </div>
                  )}

                  {companyResearch.financial_highlights && (
                    <div className="research-item">
                      <h3>Financial Highlights</h3>
                      <p>{companyResearch.financial_highlights}</p>
                    </div>
                  )}

                  {companyResearch.growth_prospects && (
                    <div className="research-item">
                      <h3>Growth Prospects</h3>
                      <p>{companyResearch.growth_prospects}</p>
                    </div>
                  )}
                </div>

                {/* Company Insights */}
                {companyInsights.length > 0 && (
                  <div className="insights-section">
                    <h3>Company Insights</h3>
                    <div className="insights-list">
                      {companyInsights.map(insight => (
                        <div key={insight.id} className="insight-card">
                          <h4>{insight.title}</h4>
                          <span className="insight-type">{insight.insight_type_display}</span>
                          <p>{insight.content}</p>
                          {insight.source && (
                            <small>Source: {insight.source}</small>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="no-research">
                <h3>No Research Available</h3>
                <p>Generate AI-powered company research to get insights about culture, interview process, and more.</p>
                {user && (
                  <button 
                    className="generate-research-btn" 
                    onClick={handleGenerateResearch}
                    disabled={isGeneratingResearch}
                  >
                    {isGeneratingResearch ? 'Generating Research...' : 'Generate Company Research'}
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'jobs' && (
          <div className="jobs-section">
            <h2>Open Positions</h2>
            <div className="job-listings">
              {companyJobs.length > 0 ? (
                companyJobs.map(job => (
                  <div key={job.id} className="job-card">
                    <h3>{job.title}</h3>
                    <div className="job-meta">
                      <span>{job.job_type || job.contract_type || 'Full-time'}</span>
                      <span>•</span>
                      <span>{job.location?.display_name || 'Remote'}</span>
                      <span>•</span>
                      <span>Posted {new Date(job.created_at).toLocaleDateString()}</span>
                    </div>
                    {job.salary_min && job.salary_max && (
                      <div className="job-salary">
                        ${parseInt(job.salary_min).toLocaleString()} - ${parseInt(job.salary_max).toLocaleString()}
                      </div>
                    )}
                    <button 
                      className="apply-button"
                      onClick={() => window.location.href = `/jobs/${job.id}`}
                    >
                      View Details
                    </button>
                  </div>
                ))
              ) : (
                <div className="no-jobs">
                  <p>No open positions available at this time.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'news' && (
          <div className="news-section">
            <h2>Company News & Updates</h2>
            <div className="news-list">
              {companyNews.length > 0 ? (
                companyNews.map(article => (
                  <div key={article.id} className="news-card">
                    <h3>{article.title}</h3>
                    <p>{article.summary}</p>
                    <div className="news-meta">
                      <span>{article.source}</span>
                      <span>•</span>
                      <span>{new Date(article.published_date).toLocaleDateString()}</span>
                      {article.relevance_score > 0 && (
                        <>
                          <span>•</span>
                          <span>Relevance: {Math.round(article.relevance_score * 100)}%</span>
                        </>
                      )}
                    </div>
                    {article.url && (
                      <a 
                        href={article.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="read-more"
                      >
                        Read Full Article
                      </a>
                    )}
                  </div>
                ))
              ) : (
                <div className="no-news">
                  <p>No recent news available for this company.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompanyProfile; 