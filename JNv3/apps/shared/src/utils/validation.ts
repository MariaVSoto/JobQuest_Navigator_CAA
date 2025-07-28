/**
 * Validation utilities for JobQuest Navigator v2
 */

import validator from 'validator';
import { UUID } from '../types/common';

// Email validation
export const validateEmail = (email: string): boolean => {
  return validator.isEmail(email);
};

export const isValidEmailDomain = (email: string): boolean => {
  if (!validateEmail(email)) return false;
  
  const domain = email.split('@')[1];
  // Add custom business logic for allowed/blocked domains
  const blockedDomains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com'];
  return !blockedDomains.includes(domain.toLowerCase());
};

// Password validation
export interface PasswordValidationResult {
  isValid: boolean;
  score: number; // 0-100
  errors: string[];
}

export const validatePassword = (password: string): PasswordValidationResult => {
  const errors: string[] = [];
  let score = 0;

  // Length check
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  } else if (password.length >= 12) {
    score += 25;
  } else {
    score += 15;
  }

  // Character variety checks
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  } else {
    score += 15;
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  } else {
    score += 15;
  }

  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  } else {
    score += 15;
  }

  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push('Password must contain at least one special character');
  } else {
    score += 20;
  }

  // Common password check
  const commonPasswords = [
    'password', '123456', 'password123', 'admin', 'qwerty',
    'letmein', 'welcome', 'monkey', '1234567890'
  ];
  if (commonPasswords.includes(password.toLowerCase())) {
    errors.push('Password is too common');
    score = Math.max(0, score - 30);
  }

  // Sequential characters check
  if (/123|abc|qwe/i.test(password)) {
    score = Math.max(0, score - 10);
  }

  return {
    isValid: errors.length === 0 && score >= 60,
    score: Math.min(100, score),
    errors
  };
};

// UUID validation
export const validateUUID = (uuid: string): boolean => {
  return validator.isUUID(uuid);
};

export const isValidUUID = (value: any): value is UUID => {
  return typeof value === 'string' && validateUUID(value);
};

// URL validation
export const validateURL = (url: string): boolean => {
  return validator.isURL(url, {
    protocols: ['http', 'https'],
    require_protocol: true
  });
};

// Phone number validation
export const validatePhoneNumber = (phone: string, countryCode = 'US'): boolean => {
  return validator.isMobilePhone(phone, countryCode as any);
};

// Date validation
export const validateDate = (dateString: string): boolean => {
  return validator.isISO8601(dateString);
};

export const isValidBirthDate = (dateString: string): boolean => {
  if (!validateDate(dateString)) return false;
  
  const date = new Date(dateString);
  const now = new Date();
  const age = now.getFullYear() - date.getFullYear();
  
  // Must be between 16 and 120 years old
  return age >= 16 && age <= 120;
};

// Job-related validation
export const validateSalaryRange = (min?: number, max?: number): boolean => {
  if (min !== undefined && min < 0) return false;
  if (max !== undefined && max < 0) return false;
  if (min !== undefined && max !== undefined && min > max) return false;
  return true;
};

export const validateExperienceYears = (years: number): boolean => {
  return years >= 0 && years <= 50;
};

// Text validation
export const validateJobTitle = (title: string): boolean => {
  return title.length >= 2 && title.length <= 200;
};

export const validateCompanyName = (name: string): boolean => {
  return name.length >= 1 && name.length <= 200;
};

export const validateJobDescription = (description: string): boolean => {
  return description.length >= 10 && description.length <= 10000;
};

// File validation
export const validateFileSize = (size: number, maxSizeMB = 10): boolean => {
  return size <= maxSizeMB * 1024 * 1024;
};

export const validateFileType = (mimeType: string, allowedTypes: string[]): boolean => {
  return allowedTypes.includes(mimeType);
};

// Form validation utilities
export interface ValidationRule<T> {
  field: keyof T;
  validator: (value: any) => boolean | string;
  message?: string;
  required?: boolean;
}

export const validateForm = <T extends Record<string, any>>(
  data: T,
  rules: ValidationRule<T>[]
): { isValid: boolean; errors: Record<keyof T, string[]> } => {
  const errors: Record<keyof T, string[]> = {} as any;

  for (const rule of rules) {
    const value = data[rule.field];
    const fieldErrors: string[] = [];

    // Check required fields
    if (rule.required && (value === undefined || value === null || value === '')) {
      fieldErrors.push(rule.message || `${String(rule.field)} is required`);
    } else if (value !== undefined && value !== null && value !== '') {
      // Run validator
      const result = rule.validator(value);
      if (result === false) {
        fieldErrors.push(rule.message || `${String(rule.field)} is invalid`);
      } else if (typeof result === 'string') {
        fieldErrors.push(result);
      }
    }

    if (fieldErrors.length > 0) {
      errors[rule.field] = fieldErrors;
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Sanitization utilities
export const sanitizeHTML = (html: string): string => {
  return validator.escape(html);
};

export const sanitizeString = (str: string): string => {
  return validator.trim(validator.escape(str));
};

// Business validation rules
export const businessRules = {
  email: {
    validator: validateEmail,
    message: 'Please enter a valid email address'
  },
  password: {
    validator: (password: string) => validatePassword(password).isValid,
    message: 'Password must be at least 8 characters with uppercase, lowercase, number, and special character'
  },
  jobTitle: {
    validator: validateJobTitle,
    message: 'Job title must be between 2 and 200 characters'
  },
  companyName: {
    validator: validateCompanyName,
    message: 'Company name must be between 1 and 200 characters'
  },
  salaryMin: {
    validator: (value: number) => value >= 0,
    message: 'Minimum salary must be non-negative'
  },
  experienceYears: {
    validator: validateExperienceYears,
    message: 'Experience years must be between 0 and 50'
  }
};

// Export validation constants
export const VALIDATION_LIMITS = {
  EMAIL_MAX_LENGTH: 254,
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_MAX_LENGTH: 128,
  JOB_TITLE_MIN_LENGTH: 2,
  JOB_TITLE_MAX_LENGTH: 200,
  COMPANY_NAME_MAX_LENGTH: 200,
  JOB_DESCRIPTION_MIN_LENGTH: 10,
  JOB_DESCRIPTION_MAX_LENGTH: 10000,
  BIO_MAX_LENGTH: 2000,
  MAX_FILE_SIZE_MB: 10,
  MAX_EXPERIENCE_YEARS: 50
} as const;