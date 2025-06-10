import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './NavBar.css';
// import logo from '../assets/logo.png'; // Uncomment and use if you have a logo

const NavBar = () => {
  const location = useLocation();
  return (
    <nav className="navbar">
      <div className="navbar-content">
        {/* <img src={logo} alt="JobQuest Logo" className="navbar-logo" /> */}
        <span className="navbar-title">JobQuest Navigator</span>
        <div className="navbar-links">
          <Link to="/login" className={location.pathname === '/login' ? 'active' : ''}>Login</Link>
          <Link to="/signup" className={location.pathname === '/signup' ? 'active' : ''}>Sign Up</Link>
          <Link to="/jobs" className={location.pathname === '/jobs' ? 'active' : ''}>Jobs</Link>
          <Link to="/map" className={location.pathname === '/map' ? 'active' : ''}>Map</Link>
          <Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''}>Dashboard</Link>
        </div>
      </div>
    </nav>
  );
};

export default NavBar; 