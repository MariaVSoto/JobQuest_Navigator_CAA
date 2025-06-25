import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './NavBar.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const NavBar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  
  // Don't show navbar on login/signup pages
  if (location.pathname === '/login' || location.pathname === '/signup') {
    return null;
  }

  // Group navigation items for authenticated users
  const mainNavItems = [
    { path: '/jobs', label: 'Jobs' },
    { path: '/map', label: 'Map' },
    { path: '/dashboard', label: 'Dashboard' }
  ];

  const jobManagementItems = [
    { path: '/saved-jobs', label: 'Saved Jobs' },
    { path: '/application-history', label: 'Applications' }
  ];

  const careerToolsItems = [
    { path: '/resume-builder', label: 'Resume Builder' },
    { path: '/ai-suggestions', label: 'AI Suggestions' },
    { path: '/skills', label: 'Skills & Certifications' },
    { path: '/interview-prep', label: 'Interview Prep' }
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        {/* <img src={logo} alt="JobQuest Logo" className="navbar-logo" /> */}
        <Link to="/dashboard" className="navbar-title">JobQuest Navigator</Link>
        
        {isAuthenticated ? (
          <div className="navbar-links">
            {/* Main Navigation */}
            {mainNavItems.map(item => (
              <Link 
                key={item.path}
                to={item.path} 
                className={location.pathname === item.path ? 'active' : ''}
              >
                {item.label}
              </Link>
            ))}

            {/* Job Management */}
            {jobManagementItems.map(item => (
              <Link 
                key={item.path}
                to={item.path} 
                className={location.pathname === item.path ? 'active' : ''}
              >
                {item.label}
              </Link>
            ))}

            {/* Career Tools */}
            {careerToolsItems.map(item => (
              <Link 
                key={item.path}
                to={item.path} 
                className={location.pathname === item.path ? 'active' : ''}
              >
                {item.label}
              </Link>
            ))}

            {/* User Menu */}
            <div className="user-menu">
              <Link 
                to="/profile" 
                className={location.pathname === '/profile' ? 'active' : ''}
              >
                {user?.first_name || 'Profile'}
              </Link>
              <Link 
                to="/settings" 
                className={location.pathname === '/settings' ? 'active' : ''}
              >
                Settings
              </Link>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </div>
          </div>
        ) : (
          <div className="navbar-links">
            <Link to="/login">Login</Link>
            <Link to="/signup">Sign Up</Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default NavBar; 