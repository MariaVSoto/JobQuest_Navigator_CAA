/**
 * Unified Fallback Manager
 * Centralized fallback logic for all services with consistent error handling and mock data management
 */

import { fallbackService } from './fallbackService';

class FallbackManager {
  constructor() {
    this.isGraphQLEnabled = process.env.REACT_APP_USE_FASTAPI_AUTH === 'true';
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.retryCount = 2;
    this.retryDelay = 1000; // 1 second
    
    // Circuit breaker state for each service
    this.circuitBreakers = {
      graphql: { failures: 0, isOpen: false, lastFailureTime: null },
      rest: { failures: 0, isOpen: false, lastFailureTime: null }
    };
    
    this.maxFailures = 3;
    this.circuitBreakerTimeout = 60000; // 1 minute
    
    console.log(`🔧 FallbackManager initialized - GraphQL: ${this.isGraphQLEnabled}, Dev: ${this.isDevelopment}`);
  }

  /**
   * Execute operation with automatic fallback chain
   * @param {Object} config - Configuration object
   * @param {Function} config.primaryOperation - Primary GraphQL operation
   * @param {Function} config.fallbackOperation - Fallback REST operation  
   * @param {Function} config.mockOperation - Mock operation for final fallback
   * @param {string} config.operationName - Name for logging
   * @param {Object} config.args - Arguments to pass to operations
   */
  async executeWithFallback(config) {
    const { primaryOperation, fallbackOperation, mockOperation, operationName, args = [] } = config;
    
    // If GraphQL is enabled and circuit breaker is closed, try primary service
    if (this.isGraphQLEnabled && !this.isCircuitBreakerOpen('graphql')) {
      try {
        console.log(`🚀 Attempting ${operationName} via GraphQL...`);
        const result = await this.withRetry(primaryOperation, args);
        this.resetCircuitBreaker('graphql');
        console.log(`✅ ${operationName} successful via GraphQL`);
        return result;
      } catch (graphqlError) {
        this.recordFailure('graphql');
        console.warn(`❌ GraphQL ${operationName} failed:`, graphqlError);
        
        // Try fallback if available and circuit breaker is closed
        if (fallbackOperation && !this.isCircuitBreakerOpen('rest')) {
          try {
            console.log(`🔄 Trying ${operationName} via REST fallback...`);
            const result = await this.withRetry(fallbackOperation, args);
            this.resetCircuitBreaker('rest');
            console.log(`✅ ${operationName} successful via REST fallback`);
            return result;
          } catch (restError) {
            this.recordFailure('rest');
            console.error(`❌ REST ${operationName} failed:`, restError);
          }
        }
      }
    } else if (fallbackOperation && !this.isCircuitBreakerOpen('rest')) {
      // GraphQL disabled or circuit breaker open, try REST directly
      try {
        console.log(`🔄 Using REST service directly for ${operationName}...`);
        const result = await this.withRetry(fallbackOperation, args);
        this.resetCircuitBreaker('rest');
        console.log(`✅ ${operationName} successful via REST`);
        return result;
      } catch (restError) {
        this.recordFailure('rest');
        console.error(`❌ REST ${operationName} failed:`, restError);
      }
    }

    // Final fallback to mock data
    if (mockOperation) {
      console.log(`🎭 Using mock ${operationName} as final fallback`);
      return await mockOperation(...args);
    } else {
      console.log(`🎭 Using fallback service for ${operationName}`);
      return this.getGenericMockResponse(operationName);
    }
  }

  /**
   * Execute operation with retry logic
   */
  async withRetry(operation, args, retryCount = this.retryCount) {
    for (let attempt = 1; attempt <= retryCount + 1; attempt++) {
      try {
        return await operation(...args);
      } catch (error) {
        if (attempt <= retryCount && this.isRetryableError(error)) {
          console.log(`🔄 Retry attempt ${attempt}/${retryCount} after ${this.retryDelay}ms...`);
          await this.delay(this.retryDelay);
          continue;
        }
        throw error;
      }
    }
  }

  /**
   * Check if error is retryable (network errors, timeouts, 5xx)
   */
  isRetryableError(error) {
    if (!error) return false;
    
    // Network errors
    if (error.name === 'NetworkError' || error.message?.includes('network')) {
      return true;
    }
    
    // GraphQL errors
    if (error.networkError) {
      return true;
    }
    
    // HTTP status codes
    if (error.status >= 500 || error.status === 429) {
      return true;
    }
    
    return false;
  }

  /**
   * Circuit breaker management
   */
  isCircuitBreakerOpen(service) {
    const breaker = this.circuitBreakers[service];
    if (!breaker.isOpen) return false;
    
    // Check if timeout has passed
    if (Date.now() - breaker.lastFailureTime > this.circuitBreakerTimeout) {
      console.log(`🔓 Circuit breaker for ${service} is now half-open`);
      breaker.isOpen = false;
      breaker.failures = 0;
      return false;
    }
    
    return true;
  }

  recordFailure(service) {
    const breaker = this.circuitBreakers[service];
    breaker.failures++;
    breaker.lastFailureTime = Date.now();
    
    if (breaker.failures >= this.maxFailures) {
      breaker.isOpen = true;
      console.log(`🔒 Circuit breaker opened for ${service} service after ${breaker.failures} failures`);
    }
  }

  resetCircuitBreaker(service) {
    const breaker = this.circuitBreakers[service];
    breaker.failures = 0;
    breaker.isOpen = false;
    breaker.lastFailureTime = null;
  }

  /**
   * Get generic mock response for unknown operations
   */
  getGenericMockResponse(operationName) {
    const operationType = this.inferOperationType(operationName);
    
    switch (operationType) {
      case 'auth':
        return {
          success: true,
          data: {
            user: fallbackService.getMockUser(),
            tokens: { access: 'mock-jwt-token-for-demo' }
          },
          message: `Mock ${operationName} - backend services unavailable`
        };
      
      case 'list':
        return {
          results: [],
          count: 0,
          message: `Mock ${operationName} - no data available`
        };
      
      case 'create':
      case 'update':
        return {
          success: true,
          data: { id: `mock-${Date.now()}` },
          message: `Mock ${operationName} - changes not persisted`
        };
      
      case 'delete':
        return {
          success: true,
          message: `Mock ${operationName} - item not actually deleted`
        };
      
      default:
        return {
          success: false,
          error: `No fallback available for ${operationName}`,
          message: 'Service unavailable'
        };
    }
  }

  /**
   * Infer operation type from operation name
   */
  inferOperationType(operationName) {
    const name = operationName.toLowerCase();
    
    if (name.includes('login') || name.includes('register') || name.includes('auth')) {
      return 'auth';
    }
    if (name.includes('get') && (name.includes('list') || name.includes('all'))) {
      return 'list';
    }
    if (name.includes('create') || name.includes('add')) {
      return 'create';
    }
    if (name.includes('update') || name.includes('edit')) {
      return 'update';
    }
    if (name.includes('delete') || name.includes('remove')) {
      return 'delete';
    }
    
    return 'unknown';
  }

  /**
   * Utility function for delays
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get health status of all services
   */
  getHealthStatus() {
    return {
      graphql: {
        enabled: this.isGraphQLEnabled,
        circuitBreakerOpen: this.isCircuitBreakerOpen('graphql'),
        failures: this.circuitBreakers.graphql.failures
      },
      rest: {
        circuitBreakerOpen: this.isCircuitBreakerOpen('rest'),
        failures: this.circuitBreakers.rest.failures
      },
      environment: {
        isDevelopment: this.isDevelopment,
        retryCount: this.retryCount,
        retryDelay: this.retryDelay
      }
    };
  }
}

// Export singleton instance
export const fallbackManager = new FallbackManager();
export default fallbackManager;