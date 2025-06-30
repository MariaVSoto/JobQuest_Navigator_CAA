/**
 * Authentication service for JobQuest Navigator
 * Handles user authentication, token management, and API communication
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class AuthService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.tokenKey = 'jobquest_access_token';
    this.refreshTokenKey = 'jobquest_refresh_token';
    this.userKey = 'jobquest_user';
  }

  /**
   * Make authenticated API request
   */
  async makeRequest(endpoint, options = {}) {
    const token = this.getToken();
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      // Handle token refresh if needed
      if (response.status === 401 && token) {
        const refreshed = await this.refreshToken();
        if (refreshed) {
          // Retry with new token
          config.headers.Authorization = `Bearer ${this.getToken()}`;
          return await fetch(url, config);
        } else {
          // Refresh failed, logout user
          this.logout();
          throw new Error('Authentication failed');
        }
      }

      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * User registration
   */
  async register(userData) {
    try {
      const response = await this.makeRequest('/auth/register/', {
        method: 'POST',
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const data = await response.json();
        this.saveAuthData(data);
        return { success: true, data };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData };
      }
    } catch (error) {
      return { success: false, error: { message: 'Network error' } };
    }
  }

  /**
   * User login
   */
  async login(credentials) {
    try {
      const response = await this.makeRequest('/auth/login/', {
        method: 'POST',
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        this.saveAuthData(data);
        return { success: true, data };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData };
      }
    } catch (error) {
      return { success: false, error: { message: 'Network error' } };
    }
  }

  /**
   * User logout
   */
  async logout() {
    try {
      const token = this.getToken();
      if (token) {
        await this.makeRequest('/auth/logout/', {
          method: 'POST',
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearAuthData();
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken() {
    try {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) {
        return false;
      }

      const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem(this.tokenKey, data.access);
        if (data.refresh) {
          localStorage.setItem(this.refreshTokenKey, data.refresh);
        }
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  }

  /**
   * Get current user profile
   */
  async getCurrentUser() {
    try {
      const response = await this.makeRequest('/auth/user/profile/');
      if (response.ok) {
        const userData = await response.json();
        localStorage.setItem(this.userKey, JSON.stringify(userData));
        return userData;
      }
      return null;
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  }

  /**
   * Alias for getCurrentUser - for compatibility
   */
  async getUserProfile() {
    return await this.getCurrentUser();
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData) {
    try {
      const response = await this.makeRequest('/auth/user/profile/update/', {
        method: 'PUT',
        body: JSON.stringify(profileData),
      });

      if (response.ok) {
        const userData = await response.json();
        localStorage.setItem(this.userKey, JSON.stringify(userData));
        return { success: true, data: userData };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData };
      }
    } catch (error) {
      return { success: false, error: { message: 'Network error' } };
    }
  }

  /**
   * Alias for updateProfile - for compatibility
   */
  async updateUserProfile(profileData) {
    const result = await this.updateProfile(profileData);
    if (result.success) {
      return result.data;
    } else {
      throw new Error(result.error.message || 'Failed to update profile');
    }
  }

  /**
   * Change password
   */
  async changePassword(passwordData) {
    try {
      const response = await this.makeRequest('/auth/password/change/', {
        method: 'POST',
        body: JSON.stringify(passwordData),
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData };
      }
    } catch (error) {
      return { success: false, error: { message: 'Network error' } };
    }
  }

  /**
   * Save authentication data to localStorage
   */
  saveAuthData(data) {
    if (data.tokens) {
      localStorage.setItem(this.tokenKey, data.tokens.access);
      localStorage.setItem(this.refreshTokenKey, data.tokens.refresh);
    }
    if (data.user) {
      localStorage.setItem(this.userKey, JSON.stringify(data.user));
    }
  }

  /**
   * Clear authentication data from localStorage
   */
  clearAuthData() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    localStorage.removeItem(this.userKey);
  }

  /**
   * Get stored access token
   */
  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Get stored access token (alias for compatibility)
   */
  getAccessToken() {
    return this.getToken();
  }

  /**
   * Get stored refresh token
   */
  getRefreshToken() {
    return localStorage.getItem(this.refreshTokenKey);
  }

  /**
   * Get stored user data
   */
  getUser() {
    const userData = localStorage.getItem(this.userKey);
    return userData ? JSON.parse(userData) : null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.getToken();
  }

  /**
   * Check if token is expired (basic check)
   */
  isTokenExpired() {
    const token = this.getToken();
    if (!token) return true;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp < currentTime;
    } catch (error) {
      return true;
    }
  }
}

export default new AuthService();