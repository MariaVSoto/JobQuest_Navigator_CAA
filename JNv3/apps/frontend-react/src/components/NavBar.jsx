import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import useResponsive from '../hooks/useResponsive';
import useMobileMenu from '../hooks/useMobileMenu';
import HamburgerMenu from './HamburgerMenu';
import './NavBar.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const NavBar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const { isMobile } = useResponsive();
  const { toggleMenu } = useMobileMenu();
  const [activeDropdown, setActiveDropdown] = useState(null);
  const timeoutRef = useRef(null);
  
  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  // Don't show navbar on login/signup pages
  if (location.pathname === '/login' || location.pathname === '/signup') {
    return null;
  }

  // V2 Navigation Structure - Aligned with 4 Core Functions
  const navigationGroups = {
    resume: {
      label: 'Resume Management',
      basePath: '/resume-builder',
      items: [
        { path: '/resume-builder', label: 'Resume Builder', description: 'Create and edit professional resumes' },
        { path: '/resume-versions', label: 'Version Management', description: 'Manage multiple resume versions' }
      ]
    },
    jobs: {
      label: 'Job Optimization',
      basePath: '/jobs',
      items: [
        { path: '/upload-job', label: 'Upload Job Position', description: 'Add job postings for optimization' },
        { path: '/my-jobs', label: 'My Job Listings', description: 'View and manage your uploaded jobs' },
        { path: '/application-history', label: 'Application Tracing', description: 'Track your job applications' },
        { path: '/ai-suggestions', label: 'AI Insights', description: 'Get AI-powered job recommendations' }
      ]
    },
    skills: {
      label: 'Skills & Learning',
      basePath: '/skills',
      items: [
        { path: '/skills', label: 'Skills & Certifications', description: 'Enhance your qualifications' },
        { path: '/skill-job-mapping', label: 'Skill-Job Mapping', description: 'Analyze skill matches with jobs' },
        { path: '/learning-paths', label: 'Learning Paths', description: 'Structured learning roadmaps' }
      ]
    },
    interview: {
      label: 'Company & Interview',
      basePath: '/interview-prep',
      items: [
        { path: '/interview-prep', label: 'Interview Prep', description: 'Practice and improve' },
        { path: '/company-search', label: 'Company Research', description: 'Search and manage company information' }
      ]
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleDropdownToggle = (groupKey) => {
    setActiveDropdown(activeDropdown === groupKey ? null : groupKey);
  };

  const handleMouseEnter = (groupKey) => {
    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setActiveDropdown(groupKey);
  };

  const handleMouseLeave = () => {
    // Set a shorter timeout before closing to improve responsiveness
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      setActiveDropdown(null);
      timeoutRef.current = null;
    }, 150);
  };

  const handleDropdownMouseEnter = () => {
    // Cancel the timeout when mouse enters dropdown
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  const handleDropdownClose = () => {
    // Clear any pending timeout and close immediately
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setActiveDropdown(null);
  };

  const isGroupActive = (group) => {
    return group.items.some(item => location.pathname === item.path);
  };

  return (
    <>
      <nav className={`navbar ${isMobile ? 'navbar--mobile' : ''}`}>
        <div className="navbar-container">
          <div className="navbar-brand">
            {/* Mobile hamburger menu button */}
            {isMobile && isAuthenticated && (
              <button 
                className="mobile-menu-trigger"
                onClick={toggleMenu}
                aria-label="Open navigation menu"
              >
                <svg className="hamburger-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="3" y1="6" x2="21" y2="6"></line>
                  <line x1="3" y1="12" x2="21" y2="12"></line>
                  <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
              </button>
            )}
            
            {/* <img src={logo} alt="JobQuest Logo" className="navbar-logo" /> */}
            <Link to="/dashboard" className="navbar-title">
              <span className="brand-icon">🎯</span>
              <span className={`brand-text ${isMobile ? 'mobile-hide-text' : ''}`}>JobQuest Navigator</span>
            </Link>
          </div>
          
          {isAuthenticated ? (
            <div className={`navbar-nav ${isMobile ? 'mobile-hide' : ''}`}>
              {/* Dashboard Link - Desktop only */}
              <Link 
                to="/dashboard" 
                className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
              >
                Dashboard
              </Link>

            {/* Grouped Navigation with Dropdowns */}
            {Object.entries(navigationGroups).map(([key, group]) => (
              <div 
                key={key}
                className="nav-dropdown"
                onMouseEnter={() => handleMouseEnter(key)}
                onMouseLeave={handleMouseLeave}
              >
                <button 
                  className={`nav-dropdown-trigger ${isGroupActive(group) ? 'active' : ''}`}
                  onClick={() => handleDropdownToggle(key)}
                >
                  {group.label}
                  <svg className="dropdown-icon" width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                    <path d="M6 8.5L2.5 5H9.5L6 8.5Z"/>
                  </svg>
                </button>
                
                {activeDropdown === key && (
                  <div 
                    className="navbar-dropdown-menu"
                    onMouseEnter={handleDropdownMouseEnter}
                    onMouseLeave={handleMouseLeave}
                  >
                    <div className="navbar-dropdown-content">
                      {group.items.map(item => (
                        <Link
                          key={item.path}
                          to={item.path}
                          className={`navbar-dropdown-item ${location.pathname === item.path ? 'active' : ''}`}
                          onClick={handleDropdownClose}
                        >
                          <div className="navbar-dropdown-item-content">
                            <span className="navbar-dropdown-item-label">{item.label}</span>
                            <span className="navbar-dropdown-item-description">{item.description}</span>
                          </div>
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* User Menu */}
            <div 
              className="nav-dropdown user-menu"
              onMouseEnter={() => handleMouseEnter('user')}
              onMouseLeave={handleMouseLeave}
            >
              <button 
                className="nav-dropdown-trigger user-trigger"
                onClick={() => handleDropdownToggle('user')}
              >
                <div className="user-avatar">
                  {user?.profile_picture ? (
                    <img src={user.profile_picture} alt="Profile" />
                  ) : (
                    <span>{user?.first_name?.[0] || user?.email?.[0] || 'U'}</span>
                  )}
                </div>
                <span className="user-name">{user?.first_name || 'Profile'}</span>
                <svg className="dropdown-icon" width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                  <path d="M6 8.5L2.5 5H9.5L6 8.5Z"/>
                </svg>
              </button>
              
              {activeDropdown === 'user' && (
                <div 
                  className="navbar-dropdown-menu user-dropdown"
                  onMouseEnter={handleDropdownMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  <div className="navbar-dropdown-content">
                    <div className="user-info">
                      <div className="user-details">
                        <span className="user-display-name">{user?.full_name || user?.first_name || 'User'}</span>
                        <span className="user-email">{user?.email}</span>
                      </div>
                    </div>
                    <div className="dropdown-divider"></div>
                    <Link
                      to="/profile"
                      className={`navbar-dropdown-item ${location.pathname === '/profile' ? 'active' : ''}`}
                      onClick={handleDropdownClose}
                    >
                      <span className="navbar-dropdown-item-label">Profile</span>
                    </Link>
                    <Link
                      to="/settings"
                      className={`navbar-dropdown-item ${location.pathname === '/settings' ? 'active' : ''}`}
                      onClick={handleDropdownClose}
                    >
                      <span className="navbar-dropdown-item-label">Settings</span>
                    </Link>
                    <div className="dropdown-divider"></div>
                    <button onClick={handleLogout} className="navbar-dropdown-item logout-item">
                      <span className="navbar-dropdown-item-label">Sign Out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
            
            {isMobile && (
              <div className="mobile-user-section">
                {user && (
                  <Link to="/profile" className="mobile-user-avatar">
                    {user?.profile_picture ? (
                      <img src={user.profile_picture} alt="Profile" />
                    ) : (
                      <span>{user?.first_name?.[0] || user?.email?.[0] || 'U'}</span>
                    )}
                  </Link>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="navbar-nav">
            <Link to="/login" className="btn btn-outline btn-sm">Sign In</Link>
            <Link to="/signup" className="btn btn-primary btn-sm">Get Started</Link>
          </div>
        )}
      </div>
    </nav>
    
    {/* Hamburger Menu */}
    <HamburgerMenu />
  </>
  );
};

export default NavBar; 