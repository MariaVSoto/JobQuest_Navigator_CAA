import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './NavBar.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const NavBar = () => {
  const location = useLocation();
  
  // Group navigation items
  const mainNavItems = [
    { path: '/jobs', label: 'Jobs' },
    { path: '/map', label: 'Map' },
    { path: '/dashboard', label: 'Dashboard' }
  ];

  const jobManagementItems = [
    { path: '/saved-jobs', label: 'Saved Jobs' },
    { path: '/application-history', label: 'Application History' }
  ];

  const careerToolsItems = [
    { path: '/resume-builder', label: 'Resume Builder' },
    { path: '/interview-prep', label: 'Interview Prep' }
  ];

  const accountItems = [
    { path: '/profile', label: 'Profile' },
    { path: '/settings', label: 'Settings' }
  ];

  const authItems = [
    { path: '/login', label: 'Login' },
    { path: '/signup', label: 'Sign Up' }
  ];

  return (
    <nav className="navbar">
      <div className="navbar-content">
        {/* <img src={logo} alt="JobQuest Logo" className="navbar-logo" /> */}
        <span className="navbar-title">JobQuest Navigator</span>
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

          {/* Account */}
          {accountItems.map(item => (
            <Link 
              key={item.path}
              to={item.path} 
              className={location.pathname === item.path ? 'active' : ''}
            >
              {item.label}
            </Link>
          ))}

          {/* Authentication */}
          {authItems.map(item => (
            <Link 
              key={item.path}
              to={item.path} 
              className={location.pathname === item.path ? 'active' : ''}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default NavBar; 