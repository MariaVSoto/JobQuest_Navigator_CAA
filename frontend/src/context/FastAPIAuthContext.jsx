/**
 * FastAPI Authentication Context for JobQuest Navigator
 * Provides authentication state and functions using FastAPI User Service
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import fastapiAuthService from '../services/fastapiAuthService';

const FastAPIAuthContext = createContext();

export const useFastAPIAuth = () => {
  const context = useContext(FastAPIAuthContext);
  if (!context) {
    throw new Error('useFastAPIAuth must be used within a FastAPIAuthProvider');
  }
  return context;
};

export const FastAPIAuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Development bypass: Auto-login with test user
  const enableDevBypass = process.env.NODE_ENV === 'development' && process.env.REACT_APP_DEV_AUTH_BYPASS === 'true';

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Development bypass: automatically set authenticated user
        if (enableDevBypass) {
          console.log('🔧 Development bypass: Auto-authenticating with test user');
          const devUser = {
            id: '77e71138-e2f1-4d49-a83d-2264746f20ce',
            email: 'test@example.com',
            first_name: 'Test',
            last_name: 'User',
            full_name: 'Test User',
            bio: 'Development test user',
            current_job_title: 'Software Developer',
            years_of_experience: 5,
            industry: 'Technology',
            career_level: 'mid',
            job_search_status: 'actively_looking',
            preferred_work_type: 'hybrid',
            is_active: true,
            is_verified: true
          };
          
          setUser(devUser);
          setIsAuthenticated(true);
          setLoading(false);
          
          // Store mock user data
          fastapiAuthService.setUser(devUser);
          fastapiAuthService.setToken('dev-bypass-token');
          
          console.log('✅ Development bypass authentication complete');
          return;
        }

        if (fastapiAuthService.isAuthenticated() && !fastapiAuthService.isTokenExpired()) {
          console.log('Token exists and not expired, checking user data...');
          const userData = fastapiAuthService.getUser();
          if (userData) {
            console.log('User data found in localStorage:', userData);
            setUser(userData);
            setIsAuthenticated(true);
          } else {
            console.log('No user data in localStorage, fetching from server...');
            // Fetch fresh user data if not in localStorage
            const currentUser = await fastapiAuthService.getCurrentUser();
            if (currentUser.success) {
              console.log('User data fetched from server:', currentUser.user);
              setUser(currentUser.user);
              setIsAuthenticated(true);
            } else {
              console.log('Failed to fetch user data from server');
              // Clear auth data if we can't get user info
              fastapiAuthService.clearAuthData();
              setIsAuthenticated(false);
            }
          }
        } else {
          console.log('No valid token found');
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        fastapiAuthService.clearAuthData();
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, [enableDevBypass]);

  /**
   * Login function
   */
  const login = async (email, password) => {
    try {
      setLoading(true);
      const result = await fastapiAuthService.login(email, password);
      
      if (result.success) {
        setUser(result.user);
        setIsAuthenticated(true);
        console.log('✅ Login successful');
        return { success: true, message: result.message };
      } else {
        console.error('❌ Login failed:', result.error);
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Login failed' };
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
      const result = await fastapiAuthService.register(userData);
      
      if (result.success) {
        // For now, don't auto-login after registration
        // User might need to verify email first
        console.log('✅ Registration successful');
        return { success: true, message: result.message };
      } else {
        console.error('❌ Registration failed:', result.error);
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Registration failed' };
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
      await fastapiAuthService.logout();
      setUser(null);
      setIsAuthenticated(false);
      console.log('✅ Logout successful');
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false, error: 'Logout failed' };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Update user profile
   */
  const updateProfile = async (profileData) => {
    try {
      const result = await fastapiAuthService.updateProfile(profileData);
      
      if (result.success) {
        setUser(result.user);
        console.log('✅ Profile updated successfully');
        return { success: true, message: result.message };
      } else {
        console.error('❌ Profile update failed:', result.error);
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Profile update error:', error);
      return { success: false, error: 'Profile update failed' };
    }
  };

  /**
   * Update career preferences
   */
  const updateCareerPreferences = async (preferences) => {
    try {
      const result = await fastapiAuthService.updateCareerPreferences(preferences);
      
      if (result.success) {
        setUser(result.user);
        console.log('✅ Career preferences updated successfully');
        return { success: true, message: result.message };
      } else {
        console.error('❌ Career preferences update failed:', result.error);
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Career preferences update error:', error);
      return { success: false, error: 'Career preferences update failed' };
    }
  };

  /**
   * Update notification settings
   */
  const updateNotificationSettings = async (settings) => {
    try {
      const result = await fastapiAuthService.updateNotificationSettings(settings);
      
      if (result.success) {
        setUser(result.user);
        console.log('✅ Notification settings updated successfully');
        return { success: true, message: result.message };
      } else {
        console.error('❌ Notification settings update failed:', result.error);
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Notification settings update error:', error);
      return { success: false, error: 'Notification settings update failed' };
    }
  };

  /**
   * Request password reset
   */
  const requestPasswordReset = async (email) => {
    try {
      const result = await fastapiAuthService.requestPasswordReset(email);
      
      if (result.success) {
        console.log('✅ Password reset email sent');
        return { success: true, message: result.message };
      } else {
        console.error('❌ Password reset request failed:', result.error);
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Password reset request error:', error);
      return { success: false, error: 'Password reset request failed' };
    }
  };

  /**
   * Reset password with token
   */
  const resetPassword = async (token, newPassword) => {
    try {
      const result = await fastapiAuthService.resetPassword(token, newPassword);
      
      if (result.success) {
        console.log('✅ Password reset successful');
        return { success: true, message: result.message };
      } else {
        console.error('❌ Password reset failed:', result.error);
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Password reset error:', error);
      return { success: false, error: 'Password reset failed' };
    }
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateProfile,
    updateCareerPreferences,
    updateNotificationSettings,
    requestPasswordReset,
    resetPassword,
    // Service reference for direct access if needed
    authService: fastapiAuthService
  };

  return (
    <FastAPIAuthContext.Provider value={value}>
      {children}
    </FastAPIAuthContext.Provider>
  );
};

export default FastAPIAuthContext;