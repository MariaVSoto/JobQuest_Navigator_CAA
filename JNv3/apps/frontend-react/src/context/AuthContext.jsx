/**
 * Authentication Context for JobQuest Navigator
 * Provides authentication state and functions throughout the app
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import unifiedUserService from '../services/unifiedUserService';
import secureAuthService from '../services/secureAuthService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Development bypass: Auto-login with test user
  const enableDevBypass = process.env.NODE_ENV === 'development' && process.env.REACT_APP_DEV_AUTH_BYPASS === 'true';
  
  // Security configuration: Use secure authentication with HttpOnly cookies
  const useSecureAuth = process.env.REACT_APP_USE_SECURE_AUTH === 'true';

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Development bypass: automatically set authenticated user
        if (enableDevBypass) {
          console.log('🔧 Development bypass: Auto-authenticating with test user');
          const devUser = {
            id: '77e71138-e2f1-4d49-a83d-2264746f20ce',
            username: 'testuser',
            email: 'test@example.com',
            fullName: 'Test User',
            bio: 'Development test user',
            currentJobTitle: 'Software Developer',
            yearsOfExperience: 5,
            industry: 'Technology',
            careerLevel: 'mid',
            jobSearchStatus: 'actively_looking',
            preferredWorkType: 'hybrid'
          };
          
          setUser(devUser);
          setIsAuthenticated(true);
          setLoading(false);
          
          // Store mock user data
          localStorage.setItem('jobquest_user', JSON.stringify(devUser));
          localStorage.setItem('jobquest_access_token', 'dev-bypass-token');
          
          console.log('✅ Development bypass authentication complete');
          return;
        }

        if (unifiedUserService.isAuthenticated()) {
          console.log('Token exists, checking user data...');
          const userData = unifiedUserService.getUser();
          if (userData) {
            console.log('User data found in localStorage:', userData);
            setUser(userData);
            setIsAuthenticated(true);
          } else {
            console.log('No user data in localStorage, fetching from server...');
            // Fetch fresh user data if not in localStorage
            const currentUser = await unifiedUserService.getCurrentUser();
            if (currentUser) {
              console.log('User data fetched from server:', currentUser);
              setUser(currentUser);
              setIsAuthenticated(true);
            } else {
              console.log('Failed to fetch user data from server');
              // Logout to clear any invalid auth state
              await unifiedUserService.logout();
              setIsAuthenticated(false);
            }
          }
        } else {
          console.log('No valid token found');
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        await unifiedUserService.logout();
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  /**
   * Login function
   */
  const login = async (credentials) => {
    try {
      setLoading(true);
      
      // Use secure authentication if configured
      if (useSecureAuth) {
        console.log('🔐 Using secure authentication with HttpOnly cookies');
        const result = await secureAuthService.login(credentials);
        
        if (result.success) {
          console.log('Secure login successful, setting user state:', result.data.user);
          setUser(result.data.user);
          setIsAuthenticated(true);
          return { success: true };
        } else {
          console.log('Secure login failed:', result.error.message);
          return { success: false, error: { message: result.error.message } };
        }
      } else {
        // Use regular unified service
        const result = await unifiedUserService.login(credentials);
        
        if (result.success) {
          console.log('Login successful, setting user state:', result.data.user);
          setUser(result.data.user);
          setIsAuthenticated(true);
          return { success: true };
        } else {
          console.log('Login failed:', result.error.message);
          return { success: false, error: { message: result.error.message } };
        }
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: { message: 'Login failed' } };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Register function
   */
  const register = async (userData) => {
    try {
      setLoading(true);
      const result = await unifiedUserService.register(userData);
      
      if (result.success) {
        console.log('Registration successful, setting user state:', result.data.user);
        setUser(result.data.user);
        setIsAuthenticated(true);
        return { success: true };
      } else {
        console.log('Registration failed:', result.error.message);
        return { success: false, errors: [result.error.message] };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, errors: ['Registration failed'] };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Logout function
   */
  const logout = async () => {
    try {
      setLoading(true);
      
      // Use secure authentication if configured
      if (useSecureAuth) {
        console.log('🚪 Using secure logout with HttpOnly cookie cleanup');
        await secureAuthService.logout();
      } else {
        await unifiedUserService.logout();
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      setLoading(false);
    }
  };

  /**
   * Update user profile
   */
  const updateProfile = async (profileData) => {
    try {
      setLoading(true);
      const result = await unifiedUserService.updateProfile(profileData);
      
      if (result.success) {
        console.log('Profile updated successfully:', result.data);
        setUser(result.data);
        return { success: true, data: result.data };
      } else {
        console.log('Profile update failed:', result.error.message);
        return { success: false, error: { message: result.error.message } };
      }
    } catch (error) {
      console.error('Profile update error:', error);
      return { success: false, error: { message: 'Profile update failed' } };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Change password
   */
  const changePassword = async (passwordData) => {
    try {
      const result = await unifiedUserService.changePassword(passwordData);
      return result;
    } catch (error) {
      console.error('Password change error:', error);
      return { success: false, error: { message: 'Password change failed' } };
    }
  };

  /**
   * Refresh user data
   */
  const refreshUser = async () => {
    try {
      const userData = await unifiedUserService.getCurrentUser();
      if (userData) {
        setUser(userData);
        return userData;
      }
      return null;
    } catch (error) {
      console.error('Failed to refresh user data:', error);
      return null;
    }
  };

  const value = {
    // State
    user,
    loading,
    isAuthenticated,
    
    // Functions
    login,
    register,
    logout,
    updateProfile,
    updateUserProfile: updateProfile, // Alias for compatibility
    changePassword,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;