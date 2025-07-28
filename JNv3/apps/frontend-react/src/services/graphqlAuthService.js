/**
 * GraphQL Authentication service for JobQuest Navigator
 * Handles user authentication using Apollo Client and GraphQL mutations
 */

import client from '../apolloClient';
import { TOKEN_AUTH, VERIFY_TOKEN, REGISTER_USER } from '../graphql/mutations';
import { gql } from '@apollo/client';

const GET_USER_QUERY = gql`
  query GetMe {
    me {
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
      dateJoined
      lastLogin
    }
  }
`;

class GraphQLAuthService {
  constructor() {
    this.tokenKey = 'jobquest_access_token';
    this.userKey = 'jobquest_user';
  }

  /**
   * Register new user
   */
  async register(userData) {
    try {
      const { data } = await client.mutate({
        mutation: REGISTER_USER,
        variables: {
          email: userData.email,
          username: userData.username,
          password: userData.password,
          firstName: userData.firstName || userData.first_name,
          lastName: userData.lastName || userData.last_name,
        },
      });

      if (data.registerUser && data.registerUser.success) {
        // After successful registration, automatically log in the user
        const loginResult = await this.login({
          username: userData.username,
          password: userData.password,
        });
        
        return {
          success: true,
          user: data.registerUser.user,
          ...loginResult
        };
      } else {
        return {
          success: false,
          errors: data.registerUser?.errors || ['Registration failed'],
        };
      }
    } catch (error) {
      console.error('GraphQL registration error:', error);
      return {
        success: false,
        errors: error.graphQLErrors?.map(e => e.message) || ['Registration failed - network error'],
      };
    }
  }

  /**
   * Login user with username and password
   */
  async login(credentials) {
    try {
      console.log('GraphQL login called with credentials:', credentials);
      
      // Ensure we have the required username parameter
      const username = credentials.username || credentials.email;
      const password = credentials.password;
      
      if (!username || !password) {
        throw new Error('Username/email and password are required');
      }
      
      console.log('Calling tokenAuth with:', { username, password: '***' });
      
      const { data } = await client.mutate({
        mutation: TOKEN_AUTH,
        variables: {
          username: username,
          password: password,
        },
      });

      console.log('GraphQL tokenAuth response:', data.tokenAuth);
      
      if (data.tokenAuth && data.tokenAuth.success && data.tokenAuth.token) {
        // Store the token
        localStorage.setItem(this.tokenKey, data.tokenAuth.token);
        
        // Use user data from response if available, otherwise get current user
        let userData = data.tokenAuth.user;
        if (!userData) {
          userData = await this.getCurrentUser();
        }
        
        // Store user data
        if (userData) {
          localStorage.setItem(this.userKey, JSON.stringify(userData));
        }
        
        return {
          success: true,
          data: {
            user: userData || {
              username: username,
              email: credentials.email || username,
            },
            tokens: { access: data.tokenAuth.token }
          },
          message: data.tokenAuth.message || 'Login successful'
        };
      } else {
        return {
          success: false,
          error: {
            message: data.tokenAuth?.message || 'Login failed - invalid response'
          }
        };
      }
    } catch (error) {
      console.error('GraphQL login error:', error);
      return {
        success: false,
        error: {
          message: error.graphQLErrors?.[0]?.message || 'Login failed - network error'
        }
      };
    }
  }

  /**
   * Get current user data using GraphQL
   */
  async getCurrentUser() {
    try {
      const { data } = await client.query({
        query: GET_USER_QUERY,
        fetchPolicy: 'network-only', // Always fetch fresh data
      });

      if (data.me) {
        // Store user data in localStorage
        localStorage.setItem(this.userKey, JSON.stringify(data.me));
        return data.me;
      }
      return null;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  }

  /**
   * Logout user
   */
  logout() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    
    // Clear Apollo Client cache
    client.clearStore();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    const token = this.getToken();
    
    // Development bypass
    if (process.env.NODE_ENV === 'development' && 
        process.env.REACT_APP_DEV_AUTH_BYPASS === 'true' && 
        token === 'dev-bypass-token') {
      return true;
    }
    
    return !!token && !this.isTokenExpired();
  }

  /**
   * Get stored token
   */
  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Get stored user data
   */
  getUser() {
    const userData = localStorage.getItem(this.userKey);
    return userData ? JSON.parse(userData) : null;
  }

  /**
   * Check if token is expired (basic check)
   */
  isTokenExpired() {
    const token = this.getToken();
    if (!token) return true;

    // Development bypass tokens never expire
    if (process.env.NODE_ENV === 'development' && 
        process.env.REACT_APP_DEV_AUTH_BYPASS === 'true' && 
        token === 'dev-bypass-token') {
      return false;
    }

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      return payload.exp < now;
    } catch (error) {
      return true;
    }
  }

  /**
   * Verify token using GraphQL
   */
  async verifyToken(token = null) {
    const tokenToVerify = token || this.getToken();
    if (!tokenToVerify) return false;

    try {
      const { data } = await client.mutate({
        mutation: VERIFY_TOKEN,
        variables: { token: tokenToVerify },
      });

      return !!data.verifyToken;
    } catch (error) {
      console.error('Token verification error:', error);
      return false;
    }
  }

  /**
   * Clear all authentication data
   */
  clearAuthData() {
    this.logout();
  }
}

export default new GraphQLAuthService();