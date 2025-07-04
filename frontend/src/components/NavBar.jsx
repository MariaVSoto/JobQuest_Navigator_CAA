import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './NavBar.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const NavBar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const [activeDropdown, setActiveDropdown] = useState(null);
  const timeoutRef = useRef(null);
  
  // Don't show navbar on login/signup pages
  if (location.pathname === '/login' || location.pathname === '/signup') {
    return null;
  }

  // Modern grouped navigation structure
  const navigationGroups = {
    jobs: {
      label: 'Jobs',
      basePath: '/jobs',
      items: [
        { path: '/jobs', label: 'Browse Jobs', description: 'Search and discover opportunities' },
        { path: '/saved-jobs', label: 'Saved Jobs', description: 'Your bookmarked positions' },
        { path: '/application-history', label: 'Applications', description: 'Track your applications' }
      ]
    },
    career: {
      label: 'Career Tools',
      basePath: '/career',
      items: [
        { path: '/resume-builder', label: 'Resume Builder', description: 'Create professional resumes' },
        { path: '/ai-suggestions', label: 'AI Insights', description: 'Personalized job recommendations' },
        { path: '/skills', label: 'Skills & Certifications', description: 'Enhance your qualifications' },
        { path: '/interview-prep', label: 'Interview Prep', description: 'Practice and improve' }
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
    }
    setActiveDropdown(groupKey);
  };

  const handleMouseLeave = () => {
    // Set a timeout before closing
    timeoutRef.current = setTimeout(() => {
      setActiveDropdown(null);
    }, 200);
  };

  const handleDropdownMouseEnter = () => {
    // Cancel the timeout when mouse enters dropdown
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  };

  const handleDropdownClose = () => {
    setActiveDropdown(null);
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const isGroupActive = (group) => {
    return group.items.some(item => location.pathname === item.path);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          {/* <img src={logo} alt="JobQuest Logo" className="navbar-logo" /> */}
          <Link to="/dashboard" className="navbar-title">
            <span className="brand-icon">🎯</span>
            JobQuest Navigator
          </Link>
        </div>
        
        {isAuthenticated ? (
          <div className="navbar-nav">
            {/* Dashboard Link */}
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
                    className="nav-dropdown-menu"
                    onMouseEnter={handleDropdownMouseEnter}
                    onMouseLeave={handleMouseLeave}
                  >
                    <div className="dropdown-content">
                      {group.items.map(item => (
                        <Link
                          key={item.path}
                          to={item.path}
                          className={`dropdown-item ${location.pathname === item.path ? 'active' : ''}`}
                          onClick={handleDropdownClose}
                        >
                          <div className="dropdown-item-content">
                            <span className="dropdown-item-label">{item.label}</span>
                            <span className="dropdown-item-description">{item.description}</span>
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
                  className="nav-dropdown-menu user-dropdown"
                  onMouseEnter={handleDropdownMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  <div className="dropdown-content">
                    <div className="user-info">
                      <div className="user-details">
                        <span className="user-display-name">{user?.full_name || user?.first_name || 'User'}</span>
                        <span className="user-email">{user?.email}</span>
                      </div>
                    </div>
                    <div className="dropdown-divider"></div>
                    <Link
                      to="/profile"
                      className={`dropdown-item ${location.pathname === '/profile' ? 'active' : ''}`}
                      onClick={handleDropdownClose}
                    >
                      <span className="dropdown-item-label">Profile</span>
                    </Link>
                    <Link
                      to="/settings"
                      className={`dropdown-item ${location.pathname === '/settings' ? 'active' : ''}`}
                      onClick={handleDropdownClose}
                    >
                      <span className="dropdown-item-label">Settings</span>
                    </Link>
                    <div className="dropdown-divider"></div>
                    <button onClick={handleLogout} className="dropdown-item logout-item">
                      <span className="dropdown-item-label">Sign Out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="navbar-nav">
            <Link to="/login" className="btn btn-outline btn-sm">Sign In</Link>
            <Link to="/signup" className="btn btn-primary btn-sm">Get Started</Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default NavBar; 