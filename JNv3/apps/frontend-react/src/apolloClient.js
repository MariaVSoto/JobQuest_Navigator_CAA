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
// Support for both Django (migration) and FastAPI (new) endpoints
const getGraphQLEndpoint = () => {
  // Check if we should use FastAPI endpoint
  const useFastAPI = process.env.REACT_APP_USE_FASTAPI_JOBS === 'true';
  
  if (useFastAPI) {
    return process.env.REACT_APP_GRAPHQL_URL || 'http://localhost:8001/graphql';
  } else {
    // Use Django endpoint during migration phase
    return '/graphql/';
  }
};

const httpLink = createHttpLink({
  uri: getGraphQLEndpoint(),
});

// 2. Create authentication Link to inject JWT token
const authLink = setContext((_, { headers }) => {
  // Get authentication token from localStorage 
  // Support both Django JWT and AWS Cognito tokens
  const token = localStorage.getItem('jobquest_access_token') || 
                localStorage.getItem('cognito_access_token');
  
  // Return headers with Authorization header
  return {
    headers: {
      ...headers,
      Authorization: token ? `Bearer ${token}` : "",
      // Add content type for FastAPI compatibility
      'Content-Type': 'application/json',
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