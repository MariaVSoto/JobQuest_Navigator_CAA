/**
 * Tests for NavBar component
 * Tests navigation, authentication states, and user interactions
 */

import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import NavBar from '../../components/NavBar';
import { renderWithAuth, mockAuthContext } from '../utils/testUtils';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/' })
}));

describe('NavBar', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('when user is authenticated', () => {
    test('renders user navigation items', () => {
      renderWithAuth(<NavBar />);

      // Check for authenticated navigation items
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Jobs')).toBeInTheDocument();
      expect(screen.getByText('Profile')).toBeInTheDocument();
      
      // Check for user name or email
      expect(screen.getByText(/Test User|test@example.com/)).toBeInTheDocument();
    });

    test('shows logout button', () => {
      renderWithAuth(<NavBar />);
      
      // Look for logout button (might be in a dropdown)
      const logoutButton = screen.getByRole('button', { name: /logout|sign out/i });
      expect(logoutButton).toBeInTheDocument();
    });

    test('calls logout function when logout button is clicked', async () => {
      const user = userEvent.setup();
      const mockLogout = jest.fn();
      const authContext = {
        ...mockAuthContext,
        logout: mockLogout
      };

      renderWithAuth(<NavBar />, authContext);

      const logoutButton = screen.getByRole('button', { name: /logout|sign out/i });
      await user.click(logoutButton);

      expect(mockLogout).toHaveBeenCalledTimes(1);
    });

    test('navigates to dashboard when logo is clicked', async () => {
      const user = userEvent.setup();
      renderWithAuth(<NavBar />);

      const logo = screen.getByText(/JobQuest Navigator/i);
      await user.click(logo);

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });

    test('navigates to jobs page when Jobs link is clicked', async () => {
      const user = userEvent.setup();
      renderWithAuth(<NavBar />);

      const jobsLink = screen.getByText('Jobs');
      await user.click(jobsLink);

      expect(mockNavigate).toHaveBeenCalledWith('/jobs');
    });

    test('navigates to profile page when Profile link is clicked', async () => {
      const user = userEvent.setup();
      renderWithAuth(<NavBar />);

      const profileLink = screen.getByText('Profile');
      await user.click(profileLink);

      expect(mockNavigate).toHaveBeenCalledWith('/profile');
    });
  });

  describe('when user is not authenticated', () => {
    const unauthenticatedContext = {
      ...mockAuthContext,
      user: null,
      isAuthenticated: false,
      token: null
    };

    test('renders guest navigation items', () => {
      renderWithAuth(<NavBar />, unauthenticatedContext);

      // Check for guest navigation items
      expect(screen.getByText('Login')).toBeInTheDocument();
      expect(screen.getByText('Sign Up')).toBeInTheDocument();
      
      // Should not show authenticated items
      expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
      expect(screen.queryByText('Profile')).not.toBeInTheDocument();
    });

    test('shows login and signup buttons', () => {
      renderWithAuth(<NavBar />, unauthenticatedContext);

      const loginButton = screen.getByRole('button', { name: /login/i });
      const signupButton = screen.getByRole('button', { name: /sign up/i });

      expect(loginButton).toBeInTheDocument();
      expect(signupButton).toBeInTheDocument();
    });

    test('navigates to login page when Login button is clicked', async () => {
      const user = userEvent.setup();
      renderWithAuth(<NavBar />, unauthenticatedContext);

      const loginButton = screen.getByRole('button', { name: /login/i });
      await user.click(loginButton);

      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });

    test('navigates to signup page when Sign Up button is clicked', async () => {
      const user = userEvent.setup();
      renderWithAuth(<NavBar />, unauthenticatedContext);

      const signupButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(signupButton);

      expect(mockNavigate).toHaveBeenCalledWith('/signup');
    });

    test('navigates to home when logo is clicked', async () => {
      const user = userEvent.setup();
      renderWithAuth(<NavBar />, unauthenticatedContext);

      const logo = screen.getByText(/JobQuest Navigator/i);
      await user.click(logo);

      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('loading state', () => {
    test('shows loading indicator when authentication is loading', () => {
      const loadingContext = {
        ...mockAuthContext,
        isLoading: true,
        isAuthenticated: false,
        user: null
      };

      renderWithAuth(<NavBar />, loadingContext);

      // Should show loading state
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
      
      // Should not show login/signup buttons while loading
      expect(screen.queryByRole('button', { name: /login/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /sign up/i })).not.toBeInTheDocument();
    });
  });

  describe('responsive behavior', () => {
    test('shows mobile menu button on small screens', () => {
      // Mock window.matchMedia to simulate mobile viewport
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(max-width: 768px)',
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      renderWithAuth(<NavBar />);

      // Should show mobile menu button
      const mobileMenuButton = screen.getByRole('button', { name: /menu/i });
      expect(mobileMenuButton).toBeInTheDocument();
    });

    test('toggles mobile menu when menu button is clicked', async () => {
      const user = userEvent.setup();
      
      // Mock mobile viewport
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(max-width: 768px)',
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      renderWithAuth(<NavBar />);

      const mobileMenuButton = screen.getByRole('button', { name: /menu/i });
      
      // Initially menu should be closed
      expect(screen.queryByTestId('mobile-menu')).not.toBeInTheDocument();
      
      // Click to open menu
      await user.click(mobileMenuButton);
      expect(screen.getByTestId('mobile-menu')).toBeInTheDocument();
      
      // Click again to close menu
      await user.click(mobileMenuButton);
      expect(screen.queryByTestId('mobile-menu')).not.toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    test('has proper ARIA attributes', () => {
      renderWithAuth(<NavBar />);

      // Check for navigation landmark
      const nav = screen.getByRole('navigation');
      expect(nav).toBeInTheDocument();
      expect(nav).toHaveAttribute('aria-label', 'Main navigation');
    });

    test('navigation links have proper accessibility attributes', () => {
      renderWithAuth(<NavBar />);

      const dashboardLink = screen.getByRole('link', { name: /dashboard/i });
      expect(dashboardLink).toHaveAttribute('href', '/dashboard');

      const jobsLink = screen.getByRole('link', { name: /jobs/i });
      expect(jobsLink).toHaveAttribute('href', '/jobs');
    });

    test('buttons have proper labels for screen readers', () => {
      const unauthenticatedContext = {
        ...mockAuthContext,
        user: null,
        isAuthenticated: false
      };

      renderWithAuth(<NavBar />, unauthenticatedContext);

      const loginButton = screen.getByRole('button', { name: /login/i });
      const signupButton = screen.getByRole('button', { name: /sign up/i });

      expect(loginButton).toHaveAccessibleName();
      expect(signupButton).toHaveAccessibleName();
    });
  });

  describe('error handling', () => {
    test('gracefully handles auth context errors', () => {
      const errorContext = {
        ...mockAuthContext,
        user: null,
        isAuthenticated: false,
        error: 'Authentication failed'
      };

      // Should not throw error when rendering with error state
      expect(() => {
        renderWithAuth(<NavBar />, errorContext);
      }).not.toThrow();
    });
  });
});