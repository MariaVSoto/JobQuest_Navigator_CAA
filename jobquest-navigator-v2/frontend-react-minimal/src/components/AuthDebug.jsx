import React from 'react';
import { useAuth } from '../context/AuthContext';
import graphqlAuthService from '../services/graphqlAuthService';

const AuthDebug = () => {
  const { user, isAuthenticated, loading } = useAuth();

  const checkToken = () => {
    const token = graphqlAuthService.getToken();
    console.log('Token from localStorage:', token);
    console.log('Token expired?', graphqlAuthService.isTokenExpired());
    console.log('Is authenticated?', graphqlAuthService.isAuthenticated());
    console.log('User from localStorage:', graphqlAuthService.getUser());
  };

  const testCurrentUser = async () => {
    try {
      console.log('Testing getCurrentUser...');
      const user = await graphqlAuthService.getCurrentUser();
      console.log('getCurrentUser result:', user);
    } catch (error) {
      console.error('getCurrentUser error:', error);
    }
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'white', 
      border: '1px solid #ccc', 
      padding: '10px', 
      zIndex: 9999,
      fontSize: '12px',
      maxWidth: '300px'
    }}>
      <h4>Auth Debug</h4>
      <p><strong>Loading:</strong> {loading ? 'Yes' : 'No'}</p>
      <p><strong>Is Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</p>
      <p><strong>User:</strong> {user ? user.email || user.username : 'null'}</p>
      <button onClick={checkToken} style={{ margin: '2px', fontSize: '10px' }}>
        Check Token
      </button>
      <button onClick={testCurrentUser} style={{ margin: '2px', fontSize: '10px' }}>
        Test getCurrentUser
      </button>
    </div>
  );
};

export default AuthDebug;