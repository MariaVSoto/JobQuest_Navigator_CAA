import { useState, useEffect } from 'react';

/**
 * Custom hook for responsive design breakpoints and device detection
 * Provides current breakpoint and device-specific booleans
 */
const useResponsive = () => {
  // Breakpoint definitions
  const breakpoints = {
    mobileSmall: 320,
    mobileLarge: 480,
    tablet: 768,
    desktop: 1024,
    desktopLarge: 1440
  };

  // Initialize state with current window dimensions
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768
  });

  // Initialize device type
  const [deviceType, setDeviceType] = useState('desktop');
  const [orientation, setOrientation] = useState('landscape');

  // Update window size and device type
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setWindowSize({ width, height });
      
      // Determine device type based on width
      if (width < breakpoints.mobileLarge) {
        setDeviceType('mobile');
      } else if (width < breakpoints.tablet) {
        setDeviceType('mobileLarge');
      } else if (width < breakpoints.desktop) {
        setDeviceType('tablet');
      } else {
        setDeviceType('desktop');
      }
      
      // Determine orientation
      setOrientation(width > height ? 'landscape' : 'portrait');
    };

    // Set initial values
    handleResize();

    // Add event listener
    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, [breakpoints]);

  // Derived boolean values for easier usage
  const isMobileSmall = windowSize.width < breakpoints.mobileLarge;
  const isMobile = windowSize.width < breakpoints.tablet;
  const isTablet = windowSize.width >= breakpoints.tablet && windowSize.width < breakpoints.desktop;
  const isDesktop = windowSize.width >= breakpoints.desktop;
  const isLargeDesktop = windowSize.width >= breakpoints.desktopLarge;

  // Touch device detection
  const isTouchDevice = () => {
    return (
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      navigator.msMaxTouchPoints > 0
    );
  };

  // Check if device supports hover
  const supportsHover = () => {
    if (typeof window === 'undefined') return true;
    return window.matchMedia('(hover: hover)').matches;
  };

  // Get appropriate grid columns based on screen size
  const getGridColumns = (mobileColumns = 1, tabletColumns = 2, desktopColumns = 3) => {
    if (isMobile) return mobileColumns;
    if (isTablet) return tabletColumns;
    return desktopColumns;
  };

  // Get appropriate container max-width
  const getContainerMaxWidth = () => {
    if (isMobile) return '100%';
    if (isTablet) return '768px';
    if (isDesktop) return '1024px';
    return '1440px';
  };

  // Get responsive padding
  const getResponsivePadding = (mobilePadding = '16px', desktopPadding = '24px') => {
    return isMobile ? mobilePadding : desktopPadding;
  };

  // Get responsive font size
  const getResponsiveFontSize = (mobileSize = '14px', desktopSize = '16px') => {
    return isMobile ? mobileSize : desktopSize;
  };

  // Check if current breakpoint matches
  const isBreakpoint = (breakpoint) => {
    switch (breakpoint) {
      case 'mobile':
        return isMobile;
      case 'tablet':
        return isTablet;
      case 'desktop':
        return isDesktop;
      case 'desktop-large':
        return isLargeDesktop;
      default:
        return false;
    }
  };

  // Get CSS classes for responsive behavior
  const getResponsiveClasses = (baseClass = '') => {
    const classes = [baseClass];
    
    if (isMobileSmall) classes.push(`${baseClass}--mobile-small`);
    if (isMobile) classes.push(`${baseClass}--mobile`);
    if (isTablet) classes.push(`${baseClass}--tablet`);
    if (isDesktop) classes.push(`${baseClass}--desktop`);
    if (isLargeDesktop) classes.push(`${baseClass}--desktop-large`);
    if (orientation === 'portrait') classes.push(`${baseClass}--portrait`);
    if (orientation === 'landscape') classes.push(`${baseClass}--landscape`);
    
    return classes.filter(Boolean).join(' ');
  };

  return {
    // Window dimensions
    windowSize,
    
    // Device type and orientation
    deviceType,
    orientation,
    
    // Breakpoint booleans
    isMobileSmall,
    isMobile,
    isTablet,
    isDesktop,
    isLargeDesktop,
    
    // Device capabilities
    isTouchDevice: isTouchDevice(),
    supportsHover: supportsHover(),
    
    // Utility functions
    getGridColumns,
    getContainerMaxWidth,
    getResponsivePadding,
    getResponsiveFontSize,
    isBreakpoint,
    getResponsiveClasses,
    
    // Breakpoint values
    breakpoints
  };
};

export default useResponsive;