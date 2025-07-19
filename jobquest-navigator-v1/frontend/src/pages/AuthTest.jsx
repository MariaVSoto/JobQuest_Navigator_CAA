import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import graphqlAuthService from '../services/graphqlAuthService';

const AuthTest = () => {
  const { user, isAuthenticated, loading } = useAuth();
  const [testResults, setTestResults] = useState({});

  const runTokenTest = async () => {
    const token = graphqlAuthService.getToken();
    const isExpired = graphqlAuthService.isTokenExpired();
    const isAuth = graphqlAuthService.isAuthenticated();
    
    setTestResults(prev => ({
      ...prev,
      token: {
        exists: !!token,
        value: token ? `${token.substring(0, 20)}...` : null,
        expired: isExpired,
        authenticated: isAuth
      }
    }));
  };

  const runUserDataTest = async () => {
    try {
      const userFromStorage = graphqlAuthService.getUser();
      const userFromServer = await graphqlAuthService.getCurrentUser();
      
      setTestResults(prev => ({
        ...prev,
        userData: {
          fromStorage: userFromStorage,
          fromServer: userFromServer,
          contextUser: user
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        userData: {
          error: error.message
        }
      }));
    }
  };

  const testGraphQLQuery = async () => {
    try {
      const query = `
        query GetMe {
          me {
            id
            email
            username
            fullName
          }
        }
      `;

      const response = await fetch('http://localhost:8000/graphql/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${graphqlAuthService.getToken()}`
        },
        body: JSON.stringify({ query })
      });

      const result = await response.json();
      
      setTestResults(prev => ({
        ...prev,
        graphqlTest: {
          success: !result.errors,
          data: result.data,
          errors: result.errors
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        graphqlTest: {
          error: error.message
        }
      }));
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px' }}>
      <h1>Authentication Test Page</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h3>Auth Context State:</h3>
        <p><strong>Loading:</strong> {loading ? 'Yes' : 'No'}</p>
        <p><strong>Is Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</p>
        <p><strong>User:</strong> {user ? JSON.stringify(user, null, 2) : 'null'}</p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button onClick={runTokenTest} style={{ margin: '5px', padding: '10px' }}>
          Test Token
        </button>
        <button onClick={runUserDataTest} style={{ margin: '5px', padding: '10px' }}>
          Test User Data
        </button>
        <button onClick={testGraphQLQuery} style={{ margin: '5px', padding: '10px' }}>
          Test GraphQL Query
        </button>
      </div>

      <div>
        <h3>Test Results:</h3>
        <pre style={{ background: '#f5f5f5', padding: '10px', overflow: 'auto' }}>
          {JSON.stringify(testResults, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default AuthTest;