/**
 * GraphQL User Service for JobQuest Navigator v2
 * Handles all user-related operations via GraphQL queries and mutations
 */

import { gql } from '@apollo/client';
import apolloClient from '../apolloClient';

// GraphQL Queries
const GET_ME_QUERY = gql`
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
    }
  }
`;

const GET_USER_QUERY = gql`
  query GetUser($id: String!) {
    user(id: $id) {
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
`;

// GraphQL Mutations
const REGISTER_USER_MUTATION = gql`
  mutation RegisterUser(
    $email: String!
    $username: String!
    $password: String!
    $firstName: String
    $lastName: String
  ) {
    registerUser(
      email: $email
      username: $username
      password: $password
      firstName: $firstName
      lastName: $lastName
    ) {
      success
      user {
        id
        email
        username
        fullName
      }
      errors
    }
  }
`;

const LOGIN_MUTATION = gql`
  mutation Login($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
      token
    }
  }
`;

const VERIFY_TOKEN_MUTATION = gql`
  mutation VerifyToken($token: String!) {
    verifyToken(token: $token)
  }
`;

const UPDATE_USER_PROFILE_MUTATION = gql`
  mutation UpdateUserProfile($input: UpdateUserProfileInput!) {
    updateUserProfile(input: $input) {
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
      errors
    }
  }
`;

class GraphQLUserService {
  constructor() {
    this.client = apolloClient;
    this.tokenKey = 'jobquest_access_token';
    this.userKey = 'jobquest_user';
  }

  /**
   * Register a new user
   */
  async register(userData) {
    try {
      console.log('Registering user via GraphQL:', userData);
      
      const { data } = await this.client.mutate({
        mutation: REGISTER_USER_MUTATION,
        variables: {
          email: userData.email,
          username: userData.username,
          password: userData.password,
          firstName: userData.firstName || null,
          lastName: userData.lastName || null,
        },
      });

      const result = data.registerUser;
      
      if (result.success && result.user) {
        console.log('✅ User registered successfully via GraphQL');
        
        // Store user data
        const userData = this.transformUserDataToFrontend(result.user);
        localStorage.setItem(this.userKey, JSON.stringify(userData));
        
        return {
          success: true,
          data: {
            user: userData,
            tokens: {
              access: 'mock-jwt-token-for-demo', // In real implementation, get from login
            }
          }
        };
      } else {
        console.error('❌ User registration failed:', result.errors);
        return {
          success: false,
          error: {
            message: result.errors?.join(', ') || 'Registration failed'
          }
        };
      }
    } catch (error) {
      console.error('GraphQL register error:', error);
      return {
        success: false,
        error: { message: error.message || 'Registration failed' }
      };
    }
  }

  /**
   * Login user
   */
  async login(credentials) {
    try {
      console.log('Logging in user via GraphQL:', credentials.username);
      
      const { data } = await this.client.mutate({
        mutation: LOGIN_MUTATION,
        variables: {
          username: credentials.username,
          password: credentials.password,
        },
      });

      const result = data.tokenAuth;
      
      if (result.token) {
        console.log('✅ User logged in successfully via GraphQL');
        
        // Store token
        localStorage.setItem(this.tokenKey, result.token);
        
        // Get user profile
        const userProfile = await this.getCurrentUser();
        
        return {
          success: true,
          data: {
            user: userProfile,
            tokens: {
              access: result.token,
            }
          }
        };
      } else {
        console.error('❌ Login failed: No token received');
        return {
          success: false,
          error: { message: 'Invalid credentials' }
        };
      }
    } catch (error) {
      console.error('GraphQL login error:', error);
      return {
        success: false,
        error: { message: error.message || 'Login failed' }
      };
    }
  }

  /**
   * Get current user profile
   */
  async getCurrentUser() {
    try {
      console.log('Fetching current user via GraphQL...');
      
      const { data } = await this.client.query({
        query: GET_ME_QUERY,
        fetchPolicy: 'cache-first',
      });

      if (data.me) {
        console.log('✅ Current user fetched successfully via GraphQL');
        const userData = this.transformUserDataToFrontend(data.me);
        localStorage.setItem(this.userKey, JSON.stringify(userData));
        return userData;
      } else {
        console.log('ℹ️ No user data returned from GraphQL');
        return null;
      }
    } catch (error) {
      console.error('GraphQL getCurrentUser error:', error);
      return null;
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData) {
    try {
      console.log('Updating user profile via GraphQL:', profileData);
      
      const input = this.transformProfileDataForGraphQL(profileData);
      
      const { data } = await this.client.mutate({
        mutation: UPDATE_USER_PROFILE_MUTATION,
        variables: { input },
        update: (cache, { data: mutationData }) => {
          // Update the cache with new user data
          if (mutationData.updateUserProfile.success && mutationData.updateUserProfile.user) {
            cache.writeQuery({
              query: GET_ME_QUERY,
              data: { me: mutationData.updateUserProfile.user },
            });
          }
        }
      });

      const result = data.updateUserProfile;
      
      if (result.success && result.user) {
        console.log('✅ User profile updated successfully via GraphQL');
        const userData = this.transformUserDataToFrontend(result.user);
        localStorage.setItem(this.userKey, JSON.stringify(userData));
        return {
          success: true,
          data: userData
        };
      } else {
        console.error('❌ Profile update failed:', result.errors);
        return {
          success: false,
          error: {
            message: result.errors?.join(', ') || 'Profile update failed'
          }
        };
      }
    } catch (error) {
      console.error('GraphQL updateProfile error:', error);
      return {
        success: false,
        error: { message: error.message || 'Profile update failed' }
      };
    }
  }

  /**
   * Verify token
   */
  async verifyToken(token) {
    try {
      console.log('Verifying token via GraphQL...');
      
      const { data } = await this.client.mutate({
        mutation: VERIFY_TOKEN_MUTATION,
        variables: { token },
      });

      const isValid = data.verifyToken;
      console.log(`✅ Token verification: ${isValid ? 'valid' : 'invalid'}`);
      return isValid;
    } catch (error) {
      console.error('GraphQL verifyToken error:', error);
      return false;
    }
  }

  /**
   * Logout user
   */
  async logout() {
    try {
      console.log('Logging out user...');
      
      // Clear stored data
      localStorage.removeItem(this.tokenKey);
      localStorage.removeItem(this.userKey);
      
      // Clear Apollo Client cache
      await this.client.clearStore();
      
      console.log('✅ User logged out successfully');
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false, error: { message: error.message } };
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!localStorage.getItem(this.tokenKey);
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
   * Transform frontend profile data to GraphQL input format
   */
  transformProfileDataForGraphQL(profileData) {
    return {
      fullName: profileData.full_name || profileData.fullName || null,
      bio: profileData.bio || null,
      currentJobTitle: profileData.current_job_title || profileData.currentJobTitle || null,
      yearsOfExperience: profileData.years_of_experience || profileData.yearsOfExperience || null,
      industry: profileData.industry || null,
      careerLevel: profileData.career_level || profileData.careerLevel || null,
      jobSearchStatus: profileData.job_search_status || profileData.jobSearchStatus || null,
      preferredWorkType: profileData.preferred_work_type || profileData.preferredWorkType || null,
    };
  }

  /**
   * Get mock user data for fallback
   */
  getMockUserData() {
    return {
      id: 'mock-user-1',
      email: 'demo@example.com',
      username: 'demouser',
      full_name: 'Demo User',
      first_name: 'Demo',
      last_name: 'User',
      bio: 'Demo user for testing purposes',
      current_job_title: 'Software Developer',
      years_of_experience: 3,
      industry: 'Technology',
      career_level: 'mid',
      job_search_status: 'actively_looking',
      preferred_work_type: 'hybrid',
    };
  }

  /**
   * Get user statistics
   */
  async getUserStats() {
    try {
      // For now, return mock stats
      // In production, this would be a GraphQL query
      return {
        applications: 0,
        savedJobs: 0,
        profileViews: 0,
        skillsAssessed: 0,
        resumesCreated: 0,
      };
    } catch (error) {
      console.error('Error getting user statistics:', error);
      return {
        applications: 0,
        savedJobs: 0,
        profileViews: 0,
        skillsAssessed: 0,
        resumesCreated: 0,
      };
    }
  }
}

export default new GraphQLUserService();