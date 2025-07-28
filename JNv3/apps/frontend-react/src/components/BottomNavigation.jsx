import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import useMobileMenu from '../hooks/useMobileMenu';
import useResponsive from '../hooks/useResponsive';
import './BottomNavigation.css';

/**
 * Bottom Navigation Component for Mobile
 * Provides quick access to main sections of the app
 */
const BottomNavigation = () => {
  const location = useLocation();
  const { isMobile } = useResponsive();
  const { getBottomNavItems, showBottomNav } = useMobileMenu();

  // Don't render on desktop or if explicitly hidden
  if (!isMobile || !showBottomNav) {
    return null;
  }

  const navItems = getBottomNavItems();

  return (
    <nav className="bottom-navigation" role="navigation" aria-label="Main Navigation">
      <div className="bottom-nav-container">
        {navItems.map((item) => (
          <Link
            key={item.id}
            to={item.path}
            className={`bottom-nav-item ${item.isActive ? 'active' : ''}`}
            aria-label={item.label}
            aria-current={item.isActive ? 'page' : undefined}
          >
            <span className="bottom-nav-icon" role="img" aria-hidden="true">
              {item.icon}
            </span>
            <span className="bottom-nav-label">{item.label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default BottomNavigation;