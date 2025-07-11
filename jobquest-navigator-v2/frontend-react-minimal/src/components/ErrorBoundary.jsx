import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Check if the error is from a browser extension
    const isExtensionError = 
      error?.stack?.includes('chrome-extension://') || 
      error?.stack?.includes('moz-extension://') ||
      errorInfo?.componentStack?.includes('extension');

    if (isExtensionError) {
      console.warn('Browser extension error detected and caught:', error);
      // For extension errors, just log and continue - don't show error UI
      this.setState({ 
        hasError: false,
        error: null,
        errorInfo: null
      });
      return;
    }

    // For actual application errors, show the error boundary
    console.error('Application error caught by ErrorBoundary:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError && this.state.error) {
      // Fallback UI for actual application errors
      return (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          backgroundColor: '#fee',
          border: '1px solid #fcc',
          borderRadius: '8px',
          margin: '20px'
        }}>
          <h2>Something went wrong.</h2>
          <details style={{ whiteSpace: 'pre-wrap', textAlign: 'left', marginTop: '10px' }}>
            <summary>Error details (click to expand)</summary>
            <pre>{this.state.error && this.state.error.toString()}</pre>
            <br />
            {this.state.errorInfo.componentStack}
          </details>
          <button 
            onClick={() => window.location.reload()}
            style={{
              marginTop: '10px',
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Reload Page
          </button>
        </div>
      );
    }

    // Render children normally if no error
    return this.props.children;
  }
}

export default ErrorBoundary;