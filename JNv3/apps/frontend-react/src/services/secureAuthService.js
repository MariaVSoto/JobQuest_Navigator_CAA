/**
 * Secure Authentication Service with HttpOnly Cookies
 * Enhanced security implementation using secure HTTP-only cookies
 * Prevents XSS attacks by storing tokens in secure cookies instead of localStorage
 */

import { gql } from '@apollo/client';
import apolloClient from '../apolloClient';

// GraphQL Mutations for secure authentication
const SECURE_LOGIN_MUTATION = gql`
  mutation SecureLogin($username: String!, $password: String!) {
    secureLogin(username: $username, password: $password) {
      success
      user {
        id
        email
        username
        fullName
        bio
        currentJobTitle
        yearsOfExperience
        industry
        careerLevel
        jobSearchStatus
        preferredWorkType
      }
      message
      errors
    }
  }
`;

const SECURE_LOGOUT_MUTATION = gql`
  mutation SecureLogout {
    secureLogout {
      success
      message
    }
  }
`;

const REFRESH_TOKEN_MUTATION = gql`
  mutation RefreshToken {
    refreshToken {
      success
      user {
        id
        email
        username
        fullName
        bio
        currentJobTitle
        yearsOfExperience
        industry
        careerLevel
        jobSearchStatus
        preferredWorkType
      }
      message
    }
  }
`;

const VALIDATE_SESSION_QUERY = gql`
  query ValidateSession {
    validateSession {
      valid
      user {
        id
        email
        username
        fullName
        bio
        currentJobTitle
        yearsOfExperience
        industry
        careerLevel
        jobSearchStatus
        preferredWorkType
      }
    }
  }
`;

class SecureAuthService {
  constructor() {
    this.userKey = 'jobquest_user_data';
    this.sessionCheckInterval = null;
    this.refreshTokenTimeout = null;
    
    // Set up automatic session validation
    this.startSessionValidation();
  }

  /**
   * Secure login with HttpOnly cookies
   */
  async login(credentials) {
    try {
      console.log('🔐 Attempting secure login...');
      
      const { data } = await apolloClient.mutate({
        mutation: SECURE_LOGIN_MUTATION,
        variables: {
          username: credentials.username,
          password: credentials.password,
        },
        // Include credentials to ensure cookies are sent/received
        context: {
          fetchOptions: {
            credentials: 'include',
          },
        },
      });

      const result = data.secureLogin;
      
      if (result.success && result.user) {
        console.log('✅ Secure login successful');
        
        // Store minimal user data in localStorage (non-sensitive)
        this.saveUserData(result.user);
        
        // Start token refresh cycle
        this.startTokenRefreshCycle();
        
        return {
          success: true,
          data: {
            user: this.transformUserDataToFrontend(result.user)
          },
          message: result.message || 'Login successful'
        };
      } else {
        console.error('❌ Secure login failed:', result.errors);
        return {
          success: false,
          error: {
            message: result.errors?.join(', ') || result.message || 'Login failed'
          }
        };
      }
    } catch (error) {
      console.error('❌ Secure login error:', error);
      return {
        success: false,
        error: { message: error.message || 'Login failed' }
      };
    }
  }

  /**
   * Secure logout with HttpOnly cookie cleanup
   */
  async logout() {
    try {
      console.log('🚪 Attempting secure logout...');
      
      const { data } = await apolloClient.mutate({
        mutation: SECURE_LOGOUT_MUTATION,
        context: {
          fetchOptions: {
            credentials: 'include',
          },
        },
      });

      const result = data.secureLogout;
      
      if (result.success) {
        console.log('✅ Secure logout successful');
      } else {
        console.warn('⚠️ Logout response indicated failure, but proceeding with cleanup');
      }
    } catch (error) {
      console.error('❌ Secure logout error (proceeding with cleanup):', error);
    } finally {
      // Always clean up local state regardless of server response
      this.clearUserData();
      this.stopTokenRefreshCycle();
      this.stopSessionValidation();
      
      // Clear Apollo Client cache
      await apolloClient.clearStore();
      
      console.log('✅ Secure logout cleanup complete');
      return { success: true };
    }
  }

  /**
   * Validate current session using HttpOnly cookies
   */
  async validateSession() {
    try {
      console.log('🔍 Validating session...');
      
      const { data } = await apolloClient.query({
        query: VALIDATE_SESSION_QUERY,
        fetchPolicy: 'network-only', // Always check with server
        context: {
          fetchOptions: {
            credentials: 'include',
          },
        },
      });

      const result = data.validateSession;
      
      if (result.valid && result.user) {
        console.log('✅ Session is valid');
        this.saveUserData(result.user);
        return {
          valid: true,
          user: this.transformUserDataToFrontend(result.user)
        };
      } else {
        console.log('❌ Session is invalid');
        this.clearUserData();
        return { valid: false, user: null };
      }
    } catch (error) {
      console.error('❌ Session validation error:', error);
      this.clearUserData();
      return { valid: false, user: null };
    }
  }

  /**
   * Refresh authentication token using HttpOnly cookies
   */
  async refreshToken() {
    try {
      console.log('🔄 Refreshing authentication token...');
      
      const { data } = await apolloClient.mutate({
        mutation: REFRESH_TOKEN_MUTATION,
        context: {
          fetchOptions: {
            credentials: 'include',
          },
        },
      });

      const result = data.refreshToken;
      
      if (result.success && result.user) {
        console.log('✅ Token refresh successful');
        this.saveUserData(result.user);
        return {
          success: true,
          user: this.transformUserDataToFrontend(result.user)
        };
      } else {
        console.log('❌ Token refresh failed');
        this.clearUserData();
        return { success: false };
      }
    } catch (error) {
      console.error('❌ Token refresh error:', error);
      this.clearUserData();
      return { success: false };
    }
  }

  /**
   * Check if user is authenticated (based on local user data)
   */
  isAuthenticated() {
    const userData = this.getUser();
    return userData !== null && userData.id;
  }

  /**
   * Get stored user data (non-sensitive data from localStorage)
   */
  getUser() {
    try {
      const userData = localStorage.getItem(this.userKey);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error retrieving user data:', error);
      return null;
    }
  }

  /**
   * Save user data to localStorage (non-sensitive data only)
   */
  saveUserData(userData) {
    try {
      // Only store non-sensitive user information
      const safeUserData = {
        id: userData.id,
        email: userData.email,
        username: userData.username,
        fullName: userData.fullName,
        bio: userData.bio,
        currentJobTitle: userData.currentJobTitle,
        yearsOfExperience: userData.yearsOfExperience,
        industry: userData.industry,
        careerLevel: userData.careerLevel,
        jobSearchStatus: userData.jobSearchStatus,
        preferredWorkType: userData.preferredWorkType,
        lastUpdated: new Date().toISOString(),
      };
      
      localStorage.setItem(this.userKey, JSON.stringify(safeUserData));
      console.log('💾 User data saved to localStorage');
    } catch (error) {
      console.error('Error saving user data:', error);
    }
  }

  /**
   * Clear user data from localStorage
   */
  clearUserData() {
    try {
      localStorage.removeItem(this.userKey);
      console.log('🗑️ User data cleared from localStorage');
    } catch (error) {
      console.error('Error clearing user data:', error);
    }
  }

  /**
   * Start automatic session validation
   */
  startSessionValidation() {
    // Validate session every 5 minutes
    this.sessionCheckInterval = setInterval(async () => {
      if (this.isAuthenticated()) {
        const validation = await this.validateSession();
        if (!validation.valid) {
          console.log('🚨 Session expired, user will need to log in again');
          // Emit custom event for components to handle
          window.dispatchEvent(new CustomEvent('sessionExpired'));
        }
      }
    }, 5 * 60 * 1000); // 5 minutes
  }

  /**
   * Stop automatic session validation
   */
  stopSessionValidation() {
    if (this.sessionCheckInterval) {
      clearInterval(this.sessionCheckInterval);
      this.sessionCheckInterval = null;
    }
  }

  /**
   * Start automatic token refresh cycle
   */
  startTokenRefreshCycle() {
    // Refresh token every 15 minutes
    this.refreshTokenTimeout = setInterval(async () => {
      if (this.isAuthenticated()) {
        await this.refreshToken();
      }
    }, 15 * 60 * 1000); // 15 minutes
  }

  /**
   * Stop automatic token refresh cycle
   */
  stopTokenRefreshCycle() {
    if (this.refreshTokenTimeout) {
      clearInterval(this.refreshTokenTimeout);
      this.refreshTokenTimeout = null;
    }
  }

  /**
   * Transform GraphQL user data to frontend format
   */
  transformUserDataToFrontend(user) {
    return {
      id: user.id,
      email: user.email,
      username: user.username,
      full_name: user.fullName,
      first_name: user.fullName?.split(' ')[0] || '',
      last_name: user.fullName?.split(' ').slice(1).join(' ') || '',
      bio: user.bio,
      current_job_title: user.currentJobTitle,
      years_of_experience: user.yearsOfExperience,
      industry: user.industry,
      career_level: user.careerLevel,
      job_search_status: user.jobSearchStatus,
      preferred_work_type: user.preferredWorkType,
      // Legacy format compatibility
      fullName: user.fullName,
      currentJobTitle: user.currentJobTitle,
      yearsOfExperience: user.yearsOfExperience,
      careerLevel: user.careerLevel,
      jobSearchStatus: user.jobSearchStatus,
      preferredWorkType: user.preferredWorkType,
    };
  }

  /**
   * Initialize secure authentication
   * Should be called when the app starts
   */
  async initialize() {
    try {
      console.log('🔧 Initializing secure authentication...');
      
      if (this.isAuthenticated()) {
        // Validate existing session
        const validation = await this.validateSession();
        if (validation.valid) {
          this.startTokenRefreshCycle();
          console.log('✅ Secure authentication initialized with valid session');
          return validation.user;
        } else {
          console.log('❌ Invalid session, user needs to log in');
          return null;
        }
      } else {
        console.log('ℹ️ No existing session found');
        return null;
      }
    } catch (error) {
      console.error('❌ Failed to initialize secure authentication:', error);
      return null;
    }
  }

  /**
   * Get security status information
   */
  getSecurityStatus() {
    return {
      isAuthenticated: this.isAuthenticated(),
      hasSessionValidation: this.sessionCheckInterval !== null,
      hasTokenRefresh: this.refreshTokenTimeout !== null,
      cookieAuthEnabled: true,
      lastUserUpdate: this.getUser()?.lastUpdated || null,
    };
  }

  /**
   * Cleanup method for when the service is destroyed
   */
  destroy() {
    this.stopSessionValidation();
    this.stopTokenRefreshCycle();
    console.log('🧹 Secure authentication service destroyed');
  }
}

export default new SecureAuthService();