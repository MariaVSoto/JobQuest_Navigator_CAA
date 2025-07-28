import { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Custom hook for managing mobile menu state and behavior
 * Handles hamburger menu, bottom navigation, and mobile-specific interactions
 */
const useMobileMenu = () => {
  const location = useLocation();
  
  // Menu state - ensure it starts closed
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [activeBottomTab, setActiveBottomTab] = useState('dashboard');
  const [showBottomNav, setShowBottomNav] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  // Close menu when route changes
  useEffect(() => {
    setIsMenuOpen(false);
  }, [location.pathname]);

  // Update active bottom tab based on current route
  useEffect(() => {
    const path = location.pathname;
    
    if (path === '/dashboard') {
      setActiveBottomTab('dashboard');
    } else if (path.includes('/jobs') || path.includes('/my-jobs') || path.includes('/create-job')) {
      setActiveBottomTab('jobs');
    } else if (path.includes('/skills') || path.includes('/learning')) {
      setActiveBottomTab('skills');
    } else if (path.includes('/interview') || path.includes('/company')) {
      setActiveBottomTab('interview');
    } else if (path.includes('/profile') || path.includes('/settings')) {
      setActiveBottomTab('profile');
    } else {
      setActiveBottomTab('dashboard'); // Default
    }
  }, [location.pathname]);

  // Handle scroll to hide/show bottom navigation
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      
      // Hide bottom nav when scrolling down, show when scrolling up
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        setShowBottomNav(false);
      } else {
        setShowBottomNav(true);
      }
      
      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [lastScrollY]);

  // Prevent body scroll when menu is open - only on mobile devices
  useEffect(() => {
    // Only apply body scroll lock on actual mobile devices to avoid desktop interference
    const isMobileDevice = window.innerWidth < 768;
    
    if (isMenuOpen && isMobileDevice) {
      // Store original scroll position to restore later
      const scrollY = window.scrollY;
      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollY}px`;
      document.body.style.width = '100%';
    } else if (!isMobileDevice) {
      // Don't manipulate body styles on desktop at all
      return;
    } else {
      // Restore original scroll position on mobile only
      const scrollY = document.body.style.top;
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.top = '';
      document.body.style.width = '';
      
      if (scrollY) {
        window.scrollTo(0, parseInt(scrollY || '0', 10) * -1);
      }
    }

    // Cleanup on unmount - only if we modified styles
    return () => {
      if (isMobileDevice) {
        document.body.style.overflow = '';
        document.body.style.position = '';
        document.body.style.top = '';
        document.body.style.width = '';
      }
    };
  }, [isMenuOpen]);

  // Menu control functions
  const toggleMenu = useCallback(() => {
    setIsMenuOpen(prev => !prev);
  }, []);

  const openMenu = useCallback(() => {
    setIsMenuOpen(true);
  }, []);

  const closeMenu = useCallback(() => {
    setIsMenuOpen(false);
  }, []);

  // Bottom navigation control
  const toggleBottomNav = useCallback(() => {
    setShowBottomNav(prev => !prev);
  }, []);

  const hideBottomNav = useCallback(() => {
    setShowBottomNav(false);
  }, []);

  const showBottomNavigation = useCallback(() => {
    setShowBottomNav(true);
  }, []);

  // Handle ESC key to close menu
  useEffect(() => {
    const handleEscKey = (event) => {
      if (event.key === 'Escape' && isMenuOpen) {
        closeMenu();
      }
    };

    document.addEventListener('keydown', handleEscKey);
    
    return () => {
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [isMenuOpen, closeMenu]);

  // Handle click outside menu to close
  const handleMenuBackdropClick = useCallback((event) => {
    if (event.target.classList.contains('hamburger-menu-backdrop')) {
      closeMenu();
    }
  }, [closeMenu]);

  // Get bottom navigation items
  const getBottomNavItems = () => [
    {
      id: 'dashboard',
      label: 'Dashboard',
      path: '/dashboard',
      icon: '🏠',
      isActive: activeBottomTab === 'dashboard'
    },
    {
      id: 'jobs',
      label: 'Jobs',
      path: '/my-jobs',
      icon: '💼',
      isActive: activeBottomTab === 'jobs'
    },
    {
      id: 'skills',
      label: 'Skills',
      path: '/skills',
      icon: '🎯',
      isActive: activeBottomTab === 'skills'
    },
    {
      id: 'interview',
      label: 'Interview',
      path: '/interview-prep',
      icon: '💬',
      isActive: activeBottomTab === 'interview'
    },
    {
      id: 'profile',
      label: 'Profile',
      path: '/profile',
      icon: '👤',
      isActive: activeBottomTab === 'profile'
    }
  ];

  // Get main menu items for hamburger menu
  const getMainMenuItems = () => [
    {
      category: 'Resume Management',
      items: [
        { path: '/resume-builder', label: 'Resume Builder', description: 'Create and edit professional resumes' },
        { path: '/resume-versions', label: 'Version Management', description: 'Manage multiple resume versions' }
      ]
    },
    {
      category: 'Job Optimization',
      items: [
        { path: '/upload-job', label: 'Upload Job Position', description: 'Add job postings for optimization' },
        { path: '/my-jobs', label: 'My Job Listings', description: 'View and manage your uploaded jobs' },
        { path: '/application-history', label: 'Application Tracing', description: 'Track your job applications' },
        { path: '/ai-suggestions', label: 'AI Insights', description: 'Get AI-powered job recommendations' }
      ]
    },
    {
      category: 'Skills & Learning',
      items: [
        { path: '/skills', label: 'Skills & Certifications', description: 'Enhance your qualifications' },
        { path: '/skill-job-mapping', label: 'Skill-Job Mapping', description: 'Analyze skill matches with jobs' },
        { path: '/learning-paths', label: 'Learning Paths', description: 'Structured learning roadmaps' }
      ]
    },
    {
      category: 'Company & Interview',
      items: [
        { path: '/interview-prep', label: 'Interview Prep', description: 'Practice and improve' },
        { path: '/company-search', label: 'Company Research', description: 'Search and manage company information' }
      ]
    }
  ];

  // Check if current page should show bottom navigation
  const shouldShowBottomNav = () => {
    const hiddenPaths = ['/login', '/signup', '/auth-test', '/services-test'];
    return !hiddenPaths.includes(location.pathname) && showBottomNav;
  };

  return {
    // Menu state
    isMenuOpen,
    activeBottomTab,
    showBottomNav: shouldShowBottomNav(),
    
    // Menu control functions
    toggleMenu,
    openMenu,
    closeMenu,
    
    // Bottom navigation control
    toggleBottomNav,
    hideBottomNav,
    showBottomNavigation,
    
    // Event handlers
    handleMenuBackdropClick,
    
    // Menu items
    getBottomNavItems,
    getMainMenuItems,
    
    // Current location info
    currentPath: location.pathname
  };
};

export default useMobileMenu;