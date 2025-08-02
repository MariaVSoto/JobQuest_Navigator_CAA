import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import useMobileMenu from '../hooks/useMobileMenu';
import useResponsive from '../hooks/useResponsive';
import './HamburgerMenu.css';

/**
 * Hamburger Menu Component for Mobile Navigation
 * Full-screen overlay menu with categorized navigation items
 */
const HamburgerMenu = () => {
  const { user, logout } = useAuth();
  const { isMenuOpen, closeMenu, getMainMenuItems, handleMenuBackdropClick } = useMobileMenu();
  const { isMobile } = useResponsive();

  // Don't render on desktop or when menu is closed
  // Also ensure we're authenticated before showing menu
  if (!isMobile || !isMenuOpen || !user) {
    return null;
  }

  const menuItems = getMainMenuItems();

  const handleLogout = async () => {
    await logout();
    closeMenu();
  };

  const handleLinkClick = () => {
    closeMenu();
  };

  return (
    <div 
      className="hamburger-menu-backdrop"
      onClick={handleMenuBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-label="Navigation Menu"
    >
      <div className="hamburger-menu" onClick={(e) => e.stopPropagation()}>
        {/* Menu Header */}
        <div className="hamburger-menu-header">
          <div className="menu-header-content">
            <div className="menu-logo">
              <span className="brand-icon">🎯</span>
              <span className="brand-text">JobQuest Navigator</span>
            </div>
            <button
              className="menu-close-btn"
              onClick={closeMenu}
              aria-label="Close menu"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
        </div>

        {/* User Info Section */}
        {user && (
          <div className="menu-user-section">
            <div className="menu-user-info">
              <div className="menu-user-avatar">
                {user?.profile_picture ? (
                  <img src={user.profile_picture} alt="Profile" />
                ) : (
                  <span>{user?.first_name?.[0] || user?.email?.[0] || 'U'}</span>
                )}
              </div>
              <div className="menu-user-details">
                <div className="menu-user-name">{user?.full_name || user?.first_name || 'User'}</div>
                <div className="menu-user-email">{user?.email}</div>
              </div>
            </div>
          </div>
        )}

        {/* Menu Content */}
        <div className="hamburger-menu-content">
          {/* Dashboard Quick Link */}
          <div className="menu-section">
            <Link 
              to="/dashboard" 
              className="menu-dashboard-link"
              onClick={handleLinkClick}
            >
              <span className="menu-item-icon">🏠</span>
              <span className="menu-item-text">Dashboard</span>
              <svg className="menu-item-arrow" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M6 12L10 8L6 4" stroke="currentColor" strokeWidth="2" fill="none"/>
              </svg>
            </Link>
          </div>

          {/* Categorized Menu Items */}
          {menuItems.map((category, categoryIndex) => (
            <div key={categoryIndex} className="menu-section">
              <div className="menu-section-title">{category.category}</div>
              <div className="menu-section-items">
                {category.items.map((item, itemIndex) => (
                  <Link
                    key={itemIndex}
                    to={item.path}
                    className="menu-item"
                    onClick={handleLinkClick}
                  >
                    <div className="menu-item-content">
                      <div className="menu-item-label">{item.label}</div>
                      <div className="menu-item-description">{item.description}</div>
                    </div>
                    <svg className="menu-item-arrow" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M6 12L10 8L6 4" stroke="currentColor" strokeWidth="2" fill="none"/>
                    </svg>
                  </Link>
                ))}
              </div>
            </div>
          ))}

          {/* User Actions Section */}
          {user && (
            <div className="menu-section menu-user-actions">
              <div className="menu-section-title">Account</div>
              <div className="menu-section-items">
                <Link
                  to="/profile"
                  className="menu-item"
                  onClick={handleLinkClick}
                >
                  <div className="menu-item-content">
                    <div className="menu-item-label">Profile</div>
                    <div className="menu-item-description">View and edit your profile</div>
                  </div>
                  <svg className="menu-item-arrow" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M6 12L10 8L6 4" stroke="currentColor" strokeWidth="2" fill="none"/>
                  </svg>
                </Link>
                
                <Link
                  to="/settings"
                  className="menu-item"
                  onClick={handleLinkClick}
                >
                  <div className="menu-item-content">
                    <div className="menu-item-label">Settings</div>
                    <div className="menu-item-description">App preferences and configuration</div>
                  </div>
                  <svg className="menu-item-arrow" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M6 12L10 8L6 4" stroke="currentColor" strokeWidth="2" fill="none"/>
                  </svg>
                </Link>
                
                <button
                  className="menu-item menu-logout"
                  onClick={handleLogout}
                >
                  <div className="menu-item-content">
                    <div className="menu-item-label">Sign Out</div>
                    <div className="menu-item-description">Exit your account</div>
                  </div>
                  <svg className="menu-item-arrow" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M6 12L10 8L6 4" stroke="currentColor" strokeWidth="2" fill="none"/>
                  </svg>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HamburgerMenu;