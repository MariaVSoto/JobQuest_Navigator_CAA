/**
 * useAuth Hook - Unified authentication management with GraphQL/REST fallback
 * Provides authentication operations and state management
 */

import { useState, useCallback } from 'react';
import { useAuth as useAuthContext } from '../context/AuthContext';
import unifiedUserService from '../services/unifiedUserService';

export const useAuth = () => {
  const authContext = useAuthContext();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Enhanced login with error handling
  const login = useCallback(async (credentials) => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔐 Attempting login...');
      const result = await authContext.login(credentials);
      
      if (result.success) {
        console.log('✅ Login successful');
        return result;
      } else {
        const errorMessage = result.error?.message || 'Login failed';
        setError(errorMessage);
        console.log('❌ Login failed:', errorMessage);
        return result;
      }
    } catch (err) {
      const errorMessage = err.message || 'Login failed';
      setError(errorMessage);
      console.error('❌ Login error:', err);
      return { success: false, error: { message: errorMessage } };
    } finally {
      setLoading(false);
    }
  }, [authContext]);

  // Enhanced register with error handling
  const register = useCallback(async (userData) => {
    try {
      setLoading(true);
      setError(null);

      console.log('📝 Attempting registration...');
      const result = await authContext.register(userData);
      
      if (result.success) {
        console.log('✅ Registration successful');
        return result;
      } else {
        const errorMessage = result.errors?.[0] || 'Registration failed';
        setError(errorMessage);
        console.log('❌ Registration failed:', errorMessage);
        return result;
      }
    } catch (err) {
      const errorMessage = err.message || 'Registration failed';
      setError(errorMessage);
      console.error('❌ Registration error:', err);
      return { success: false, errors: [errorMessage] };
    } finally {
      setLoading(false);
    }
  }, [authContext]);

  // Enhanced logout with error handling
  const logout = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('🚪 Logging out...');
      await authContext.logout();
      console.log('✅ Logout successful');
      return { success: true };
    } catch (err) {
      const errorMessage = err.message || 'Logout failed';
      setError(errorMessage);
      console.error('❌ Logout error:', err);
      return { success: false, error: { message: errorMessage } };
    } finally {
      setLoading(false);
    }
  }, [authContext]);

  // Enhanced profile update with error handling
  const updateProfile = useCallback(async (profileData) => {
    try {
      setLoading(true);
      setError(null);

      console.log('👤 Updating profile...');
      const result = await authContext.updateProfile(profileData);
      
      if (result.success) {
        console.log('✅ Profile updated successfully');
        return result;
      } else {
        const errorMessage = result.error?.message || 'Profile update failed';
        setError(errorMessage);
        console.log('❌ Profile update failed:', errorMessage);
        return result;
      }
    } catch (err) {
      const errorMessage = err.message || 'Profile update failed';
      setError(errorMessage);
      console.error('❌ Profile update error:', err);
      return { success: false, error: { message: errorMessage } };
    } finally {
      setLoading(false);
    }
  }, [authContext]);

  // Enhanced password change with error handling
  const changePassword = useCallback(async (passwordData) => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔒 Changing password...');
      const result = await authContext.changePassword(passwordData);
      
      if (result.success) {
        console.log('✅ Password changed successfully');
        return result;
      } else {
        const errorMessage = result.error?.message || 'Password change failed';
        setError(errorMessage);
        console.log('❌ Password change failed:', errorMessage);
        return result;
      }
    } catch (err) {
      const errorMessage = err.message || 'Password change failed';
      setError(errorMessage);
      console.error('❌ Password change error:', err);
      return { success: false, error: { message: errorMessage } };
    } finally {
      setLoading(false);
    }
  }, [authContext]);

  // Refresh user data
  const refreshUser = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('🔄 Refreshing user data...');
      const userData = await authContext.refreshUser();
      
      if (userData) {
        console.log('✅ User data refreshed');
        return userData;
      } else {
        console.log('❌ Failed to refresh user data');
        return null;
      }
    } catch (err) {
      const errorMessage = err.message || 'Failed to refresh user data';
      setError(errorMessage);
      console.error('❌ Refresh user error:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [authContext]);

  // Check if token is valid
  const checkTokenValidity = useCallback(async () => {
    try {
      const token = unifiedUserService.getToken();
      if (!token) return false;

      console.log('🔍 Checking token validity...');
      const isValid = await unifiedUserService.verifyToken(token);
      console.log(`✅ Token is ${isValid ? 'valid' : 'invalid'}`);
      return isValid;
    } catch (err) {
      console.error('❌ Token validation error:', err);
      return false;
    }
  }, []);

  // Get user statistics
  const getUserStats = useCallback(async () => {
    try {
      console.log('📊 Loading user statistics...');
      const stats = await unifiedUserService.getUserStats();
      console.log('✅ User statistics loaded');
      return stats;
    } catch (err) {
      console.error('❌ Failed to load user statistics:', err);
      return {
        applications: 0,
        savedJobs: 0,
        profileViews: 0,
        skillsAssessed: 0,
        resumesCreated: 0,
      };
    }
  }, []);

  // Check service health
  const checkServiceHealth = useCallback(async () => {
    try {
      console.log('🏥 Checking service health...');
      const health = await unifiedUserService.checkHealth();
      console.log('✅ Service health checked');
      return health;
    } catch (err) {
      console.error('❌ Service health check failed:', err);
      return {
        graphql: false,
        rest: false,
        primary: 'unknown'
      };
    }
  }, []);

  // Switch primary service
  const switchService = useCallback((useGraphQL = true) => {
    console.log(`🔄 Switching to ${useGraphQL ? 'GraphQL' : 'REST'} service`);
    unifiedUserService.switchToPrimary(useGraphQL);
  }, []);

  // Computed values
  const isLoggedIn = authContext.isAuthenticated;
  const user = authContext.user;
  const contextLoading = authContext.loading;
  const isLoading = loading || contextLoading;

  // User profile completeness
  const profileCompleteness = user ? (() => {
    const fields = [
      'fullName', 'full_name',
      'bio',
      'currentJobTitle', 'current_job_title',
      'yearsOfExperience', 'years_of_experience',
      'industry',
      'careerLevel', 'career_level'
    ];
    
    const filledFields = fields.filter(field => 
      user[field] && user[field].toString().trim().length > 0
    );
    
    return Math.round((filledFields.length / (fields.length / 2)) * 100);
  })() : 0;

  // User display name
  const displayName = user?.fullName || user?.full_name || 
                     `${user?.first_name || ''} ${user?.last_name || ''}`.trim() || 
                     user?.username || 
                     user?.email || 
                     'User';

  return {
    // State from context
    user,
    isLoggedIn,
    isAuthenticated: isLoggedIn,
    
    // Enhanced loading state
    loading: isLoading,
    error,
    
    // Computed values
    profileCompleteness,
    displayName,
    
    // Enhanced actions
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    refreshUser,
    
    // Additional utilities
    checkTokenValidity,
    getUserStats,
    checkServiceHealth,
    switchService,
    
    // Error management
    setError: (error) => setError(error),
    clearError: () => setError(null),
    
    // Context actions (direct access)
    updateUserProfile: authContext.updateUserProfile,
  };
};

export default useAuth;