import React from 'react';
import { useNavigate } from 'react-router-dom';
import './NotFound.css';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="not-found-container">
      <div className="not-found-content">
        <div className="not-found-image">
          <img 
            src="/404-illustration.svg" 
            alt="404 Illustration" 
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIwIiBoZWlnaHQ9IjI0MCIgdmlld0JveD0iMCAwIDMyMCAyNDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMTYwIiBjeT0iMTIwIiByPSIxMDAiIGZpbGw9IiNGM0Y0RjYiLz48dGV4dCB4PSIxNjAiIHk9IjE0MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjQ4IiBmb250LXdlaWdodD0iYm9sZCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iIzFBMUExQSI+NDA0PC90ZXh0Pjwvc3ZnPg==';
            }}
          />
        </div>
        <div className="not-found-text">
          <h1>404</h1>
          <h2>Page Not Found</h2>
          <p>Sorry, the page you are looking for doesn't exist or has been moved.</p>
          <button onClick={() => navigate('/')} className="home-button">
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotFound; 