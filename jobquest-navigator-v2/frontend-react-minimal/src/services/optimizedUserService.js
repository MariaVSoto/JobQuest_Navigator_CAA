/**
 * Optimized User Service with Unified Fallback Management
 * Uses FallbackManager for consistent error handling and circuit breaker pattern
 */

import graphqlUserService from './graphqlUserService';
import graphqlAuthService from './graphqlAuthService';
import { fallbackManager } from './fallbackManager';
import { fallbackService } from './fallbackService';

class OptimizedUserService {
  constructor() {
    this.primaryService = graphqlUserService;
    this.fallbackService = graphqlAuthService;
    
    console.log('🔧 OptimizedUserService initialized with FallbackManager');
  }

  /**
   * Register user with optimized fallback chain
   */
  async register(userData) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (data) => this.primaryService.register(data),
      fallbackOperation: (data) => this.fallbackService.register(data),
      mockOperation: (data) => this.getMockRegisterResponse(data),
      operationName: 'register',
      args: [userData]
    });
  }

  /**
   * Login user with optimized fallback chain
   */
  async login(credentials) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (creds) => this.primaryService.login(creds),
      fallbackOperation: (creds) => this.fallbackService.login(creds),
      mockOperation: (creds) => this.getMockLoginResponse(creds),
      operationName: 'login',
      args: [credentials]
    });
  }

  /**
   * Get current user with optimized fallback chain
   */
  async getCurrentUser() {
    return await fallbackManager.executeWithFallback({
      primaryOperation: () => this.primaryService.getCurrentUser(),
      fallbackOperation: () => this.fallbackService.getCurrentUser(),
      mockOperation: () => this.getMockCurrentUserResponse(),
      operationName: 'getCurrentUser',
      args: []
    });
  }

  /**
   * Update user profile with optimized fallback chain
   */
  async updateUserProfile(profileData) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (data) => this.primaryService.updateUserProfile(data),
      fallbackOperation: (data) => this.fallbackService.updateUserProfile(data),
      mockOperation: (data) => this.getMockUpdateResponse(data),
      operationName: 'updateUserProfile',
      args: [profileData]
    });
  }

  /**
   * Logout user
   */
  async logout() {
    try {
      // Try primary service first
      if (this.primaryService.logout) {
        await this.primaryService.logout();
      }
    } catch (error) {
      console.warn('Primary logout failed:', error);
    }

    try {
      // Try fallback service
      if (this.fallbackService.logout) {
        await this.fallbackService.logout();
      }
    } catch (error) {
      console.warn('Fallback logout failed:', error);
    }

    // Always clear local storage as final step
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    
    console.log('✅ User logged out (local cleanup completed)');
    return { success: true, message: 'Logged out successfully' };
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    const token = localStorage.getItem('token');
    if (!token) return false;

    try {
      // Basic token validation (check if it's not expired)
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch (error) {
      return false;
    }
  }

  /**
   * Get authentication token
   */
  getAuthToken() {
    return localStorage.getItem('token');
  }

  // Mock response generators
  getMockRegisterResponse(userData) {
    const mockUser = {
      ...fallbackService.getMockUser(),
      email: userData.email,
      full_name: userData.full_name || userData.firstName + ' ' + userData.lastName
    };

    return {
      success: true,
      data: {
        user: mockUser,
        tokens: { access: 'mock-jwt-token-for-demo-register' }
      },
      message: 'Mock registration successful - backend services unavailable'
    };
  }

  getMockLoginResponse(credentials) {
    const mockUser = {
      ...fallbackService.getMockUser(),
      email: credentials.email
    };

    return {
      success: true,
      data: {
        user: mockUser,
        tokens: { access: 'mock-jwt-token-for-demo-login' }
      },
      message: 'Mock login successful - backend services unavailable'
    };
  }

  getMockCurrentUserResponse() {
    return fallbackService.getMockUser();
  }

  getMockUpdateResponse(profileData) {
    const updatedUser = {
      ...fallbackService.getMockUser(),
      ...profileData,
      updated_at: new Date().toISOString()
    };

    return {
      success: true,
      data: updatedUser,
      message: 'Mock profile update - changes not persisted'
    };
  }

  /**
   * Get service health status
   */
  getHealthStatus() {
    return {
      ...fallbackManager.getHealthStatus(),
      service: 'OptimizedUserService',
      isAuthenticated: this.isAuthenticated()
    };
  }
}

// Export singleton instance
export const optimizedUserService = new OptimizedUserService();
export default optimizedUserService;