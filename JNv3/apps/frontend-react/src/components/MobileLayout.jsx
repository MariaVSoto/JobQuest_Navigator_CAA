import React from 'react';
import PropTypes from 'prop-types';
import useResponsive from '../hooks/useResponsive';
import useMobileMenu from '../hooks/useMobileMenu';
import BottomNavigation from './BottomNavigation';
import './MobileLayout.css';

/**
 * Mobile Layout Component
 * Provides consistent layout structure for mobile devices
 * Handles spacing for fixed navigation elements
 */
const MobileLayout = ({ 
  children, 
  showBottomNav = true, 
  fullHeight = false,
  className = '',
  padding = true 
}) => {
  const { isMobile, getResponsiveClasses } = useResponsive();
  const { showBottomNav: shouldShowBottomNav } = useMobileMenu();

  // Determine if we should actually show bottom navigation
  const displayBottomNav = showBottomNav && shouldShowBottomNav && isMobile;

  // Build CSS classes
  const layoutClasses = [
    'mobile-layout',
    getResponsiveClasses('mobile-layout'),
    fullHeight ? 'mobile-layout--full-height' : '',
    padding ? 'mobile-layout--padding' : '',
    displayBottomNav ? 'mobile-layout--with-bottom-nav' : '',
    className
  ].filter(Boolean).join(' ');

  if (!isMobile) {
    // For non-mobile devices, just render children with minimal wrapper
    return (
      <div className={`desktop-layout ${className}`}>
        {children}
      </div>
    );
  }

  return (
    <div className={layoutClasses}>
      {/* Mobile top spacer for fixed navigation */}
      <div className="mobile-nav-spacer" />
      
      {/* Main content area */}
      <main className="mobile-content">
        <div className="mobile-content-inner">
          {children}
        </div>
      </main>
      
      {/* Mobile bottom spacer and navigation */}
      {displayBottomNav && (
        <>
          <div className="mobile-bottom-spacer" />
          <BottomNavigation />
        </>
      )}
    </div>
  );
};

MobileLayout.propTypes = {
  children: PropTypes.node.isRequired,
  showBottomNav: PropTypes.bool,
  fullHeight: PropTypes.bool,
  className: PropTypes.string,
  padding: PropTypes.bool
};

export default MobileLayout;