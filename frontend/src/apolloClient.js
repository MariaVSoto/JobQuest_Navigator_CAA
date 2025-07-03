/**
 * Apollo Client Configuration for JobQuest Navigator
 * 
 * This file configures Apollo Client with:
 * - HTTP link to GraphQL endpoint
 * - Authentication link for JWT token injection
 * - In-memory cache for query optimization
 */

import { ApolloClient, InMemoryCache, createHttpLink, ApolloLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

// 1. Create HTTP Link pointing to GraphQL API endpoint
const httpLink = createHttpLink({
  uri: process.env.REACT_APP_GRAPHQL_ENDPOINT || 'http://localhost:8000/graphql/',
});

// 2. Create authentication Link to inject JWT token
const authLink = setContext((_, { headers }) => {
  // Get authentication token from localStorage (using the same key as REST API)
  const token = localStorage.getItem('jobquest_access_token');
  
  // Return headers with Authorization header (capital A for Django compatibility)
  return {
    headers: {
      ...headers,
      Authorization: token ? `Bearer ${token}` : "",
    }
  }
});

// 3. Error handling link for better debugging
const errorLink = new ApolloLink((operation, forward) => {
  return forward(operation).map(response => {
    // Log GraphQL errors for debugging
    if (response.errors) {
      console.error('GraphQL errors:', response.errors);
    }
    return response;
  });
});

// 4. Instantiate Apollo Client
const client = new ApolloClient({
  // Chain links: error handling -> auth -> HTTP
  // Order matters: authLink ensures every request has token
  link: ApolloLink.from([errorLink, authLink, httpLink]),
  
  // Use InMemoryCache for intelligent caching and automatic UI updates
  cache: new InMemoryCache({
    typePolicies: {
      Job: {
        fields: {
          // Configure how Apollo handles job-related data
          requiredSkills: {
            merge(existing = [], incoming) {
              return incoming;
            }
          }
        }
      }
    }
  }),

  // Enable Apollo DevTools in development
  connectToDevTools: process.env.NODE_ENV === 'development',

  // Default options for queries
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all', // Return partial data even if there are errors
    },
    query: {
      errorPolicy: 'all',
    },
  }
});

export default client;