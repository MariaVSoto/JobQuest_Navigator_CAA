/**
 * JobQuest Navigator v2 - Shared Module
 * Main entry point for all shared components
 */

// Types
export * from './types/common';
export * from './types/user';

// Constants and Enums
export * from './constants/enums';

// Utilities
export * from './utils/validation';
export * from './utils/formatting';

// Re-export commonly used items with convenient aliases
export {
  // Type aliases
  type UUID,
  type Email,
  type Timestamp,
  type ApiResponse,
  type PaginatedResponse,
  type User,
  type UserProfile,
  type CreateUserInput,
  type UpdateUserInput,
  type LoginInput,
  type LoginResponse,
  
  // Enum aliases
  JOB_STATUS,
  JOB_TYPE,
  WORK_TYPE,
  APPLICATION_STATUS,
  JOB_SEARCH_STATUS,
  CAREER_LEVEL,
  SKILL_CATEGORY,
  PROFICIENCY_LEVEL,
  
  // Validation aliases
  validateEmail,
  validatePassword,
  validateUUID,
  validateURL,
  businessRules,
  
  // Formatting aliases
  formatDate,
  formatCurrency,
  formatSalaryRange,
  formatName,
  formatLocation,
  formatters
} from './index';

// Version info
export const VERSION = '2.0.0';
export const PACKAGE_NAME = '@jobquest/shared';

// Configuration constants
export const CONFIG = {
  API_TIMEOUT: 30000,
  MAX_FILE_SIZE_MB: 10,
  SUPPORTED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif'],
  SUPPORTED_DOCUMENT_TYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ],
  DATE_FORMATS: {
    DEFAULT: 'MMM d, yyyy',
    FULL: 'MMMM d, yyyy',
    SHORT: 'MM/dd/yyyy',
    ISO: 'yyyy-MM-dd'
  },
  PAGINATION: {
    DEFAULT_PAGE_SIZE: 20,
    MAX_PAGE_SIZE: 100
  }
} as const;

// Utility functions for common operations
export const utils = {
  // Type checking utilities
  isValidEmail: (email: string): boolean => validateEmail(email),
  isValidUUID: (uuid: string): boolean => validateUUID(uuid),
  
  // Formatting utilities
  formatUserName: (firstName?: string, lastName?: string): string => 
    formatName(firstName, lastName),
  
  formatJobTitle: (title: string): string => 
    title.trim().replace(/\s+/g, ' '),
  
  // Common validation patterns
  isStrongPassword: (password: string): boolean => 
    validatePassword(password).isValid,
  
  // Data transformation utilities
  parseApiDate: (dateString: string): Date | null => {
    try {
      const date = new Date(dateString);
      return isNaN(date.getTime()) ? null : date;
    } catch {
      return null;
    }
  },
  
  // Safe JSON parsing
  safeJsonParse: <T>(jsonString: string, fallback: T): T => {
    try {
      return JSON.parse(jsonString);
    } catch {
      return fallback;
    }
  },
  
  // Array utilities
  removeDuplicates: <T>(array: T[]): T[] => [...new Set(array)],
  
  // Object utilities
  removeEmptyFields: <T extends Record<string, any>>(obj: T): Partial<T> => {
    const result: Partial<T> = {};
    for (const [key, value] of Object.entries(obj)) {
      if (value !== null && value !== undefined && value !== '') {
        result[key as keyof T] = value;
      }
    }
    return result;
  }
} as const;

// Error classes for common scenarios
export class ValidationError extends Error {
  constructor(
    message: string,
    public field?: string,
    public code?: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends Error {
  constructor(message = 'Authentication failed') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class AuthorizationError extends Error {
  constructor(message = 'Access denied') {
    super(message);
    this.name = 'AuthorizationError';
  }
}

export class NotFoundError extends Error {
  constructor(resource = 'Resource') {
    super(`${resource} not found`);
    this.name = 'NotFoundError';
  }
}

// Default export with all utilities
export default {
  VERSION,
  PACKAGE_NAME,
  CONFIG,
  utils,
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  NotFoundError
};