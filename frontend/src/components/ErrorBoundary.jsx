/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI
 */
import { Component } from 'react';
import styles from './ErrorBoundary.module.css';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to console
    console.error('❌ React Error Boundary caught an error:', error, errorInfo);
    
    // Save error details to state
    this.state = {
      hasError: true,
      error,
      errorInfo
    };

    // TODO: Send error to monitoring service
    // if (window.Sentry) {
    //   window.Sentry.captureException(error, { extra: errorInfo });
    // }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/';  // Navigate to home
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className={styles.errorContainer}>
          <div className={styles.errorCard}>
            <div className={styles.errorIcon}>🥴</div>
            <h1 className={styles.errorTitle}>Oops! Something went wrong</h1>
            <p className={styles.errorMessage}>
              We're sorry for the inconvenience. The application encountered an unexpected error.
            </p>
            
            {import.meta.env.DEV && this.state.error && (
              <details className={styles.errorDetails}>
                <summary>Error Details (Development Only)</summary>
                <pre className={styles.errorStack}>
                  {this.state.error.toString()}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <div className={styles.errorActions}>
              <button 
                onClick={() => window.location.reload()} 
                className={styles.primaryButton}
              >
                Refresh Page
              </button>
              <button 
                onClick={this.handleReset}
                className={styles.secondaryButton}
              >
                Go to Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

