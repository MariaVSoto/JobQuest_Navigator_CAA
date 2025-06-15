import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './CompanyProfile.css';

const CompanyProfile = () => {
  const { companyId } = useParams();
  const [company, setCompany] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching company data
    const fetchCompanyData = async () => {
      setIsLoading(true);
      // TODO: Replace with actual API call
      const mockCompany = {
        id: companyId,
        name: "TechCorp Solutions",
        logo: "https://via.placeholder.com/150",
        industry: "Technology",
        size: "500-1000 employees",
        founded: "2010",
        location: "San Francisco, CA",
        website: "https://techcorp.com",
        description: "TechCorp Solutions is a leading technology company specializing in innovative software solutions...",
        benefits: [
          "Health Insurance",
          "401(k) Matching",
          "Remote Work Options",
          "Professional Development",
          "Flexible Hours"
        ],
        openPositions: [
          {
            id: 1,
            title: "Senior Software Engineer",
            type: "Full-time",
            location: "San Francisco, CA",
            posted: "2 days ago"
          },
          {
            id: 2,
            title: "Product Manager",
            type: "Full-time",
            location: "Remote",
            posted: "1 week ago"
          }
        ],
        reviews: [
          {
            id: 1,
            rating: 4.5,
            title: "Great company culture",
            content: "Excellent work environment with supportive management...",
            author: "John Doe",
            position: "Software Engineer",
            date: "2024-01-15"
          },
          {
            id: 2,
            rating: 4.0,
            title: "Good opportunities for growth",
            content: "Lots of learning opportunities and career advancement...",
            author: "Jane Smith",
            position: "Product Manager",
            date: "2024-01-10"
          }
        ]
      };
      setCompany(mockCompany);
      setIsLoading(false);
    };

    fetchCompanyData();
  }, [companyId]);

  if (isLoading) {
    return <div className="loading">Loading company information...</div>;
  }

  if (!company) {
    return <div className="error">Company not found</div>;
  }

  return (
    <div className="company-profile-container">
      {/* Company Header */}
      <div className="company-header">
        <div className="company-logo">
          <img src={company.logo} alt={company.name} />
        </div>
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
            <button className="follow-button">Follow</button>
            <button className="website-button" onClick={() => window.open(company.website, '_blank')}>
              Visit Website
            </button>
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
          className={activeTab === 'jobs' ? 'active' : ''}
          onClick={() => setActiveTab('jobs')}
        >
          Open Positions
        </button>
        <button
          className={activeTab === 'reviews' ? 'active' : ''}
          onClick={() => setActiveTab('reviews')}
        >
          Reviews
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
                <p>{company.founded}</p>
              </div>
              <div className="detail-item">
                <h3>Company Size</h3>
                <p>{company.size}</p>
              </div>
              <div className="detail-item">
                <h3>Industry</h3>
                <p>{company.industry}</p>
              </div>
              <div className="detail-item">
                <h3>Location</h3>
                <p>{company.location}</p>
              </div>
            </div>
            <div className="company-benefits">
              <h2>Benefits & Perks</h2>
              <ul>
                {company.benefits.map((benefit, index) => (
                  <li key={index}>{benefit}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'jobs' && (
          <div className="jobs-section">
            <h2>Open Positions</h2>
            <div className="job-listings">
              {company.openPositions.map(job => (
                <div key={job.id} className="job-card">
                  <h3>{job.title}</h3>
                  <div className="job-meta">
                    <span>{job.type}</span>
                    <span>•</span>
                    <span>{job.location}</span>
                    <span>•</span>
                    <span>Posted {job.posted}</span>
                  </div>
                  <button className="apply-button">Apply Now</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'reviews' && (
          <div className="reviews-section">
            <h2>Company Reviews</h2>
            <div className="reviews-list">
              {company.reviews.map(review => (
                <div key={review.id} className="review-card">
                  <div className="review-header">
                    <div className="review-rating">
                      {Array.from({ length: 5 }).map((_, index) => (
                        <span
                          key={index}
                          className={`star ${index < review.rating ? 'filled' : ''}`}
                        >
                          ★
                        </span>
                      ))}
                    </div>
                    <h3>{review.title}</h3>
                  </div>
                  <p className="review-content">{review.content}</p>
                  <div className="review-author">
                    <span className="author-name">{review.author}</span>
                    <span className="author-position">{review.position}</span>
                    <span className="review-date">{review.date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompanyProfile; 