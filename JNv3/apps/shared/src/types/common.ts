/**
 * Common types used throughout JobQuest Navigator v2
 */

// Base types
export type UUID = string;
export type Timestamp = string; // ISO 8601 format
export type Email = string;
export type URL = string;
export type JSONString = string;

// Generic response types
export interface BaseEntity {
  id: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  isActive: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  errors?: string[];
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  totalCount: number;
  pageCount: number;
  currentPage: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

export interface FilterParams {
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

// GraphQL types
export interface GraphQLError {
  message: string;
  locations?: Array<{
    line: number;
    column: number;
  }>;
  path?: string[];
  extensions?: Record<string, any>;
}

export interface GraphQLResponse<T> {
  data?: T;
  errors?: GraphQLError[];
  extensions?: Record<string, any>;
}

// Form validation types
export interface ValidationError {
  field: string;
  message: string;
  code?: string;
}

export interface FormState<T> {
  values: T;
  errors: ValidationError[];
  isValid: boolean;
  isSubmitting: boolean;
  isDirty: boolean;
}

// File upload types
export interface FileUpload {
  id: UUID;
  filename: string;
  originalName: string;
  mimeType: string;
  size: number;
  url: URL;
  uploadedAt: Timestamp;
}

// Location types (simplified)
export interface Location {
  text: string; // e.g., "San Francisco, CA" or "Remote"
  country?: string;
  state?: string;
  city?: string;
  isRemote?: boolean;
}

// Money/Currency types
export interface Money {
  amount: number;
  currency: string; // ISO 4217 currency code
}

export interface SalaryRange {
  min?: Money;
  max?: Money;
  period: 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly';
}

// Search and filtering
export interface SearchFilters {
  query?: string;
  location?: string;
  salaryMin?: number;
  salaryMax?: number;
  workType?: string[];
  experienceLevel?: string[];
  skills?: string[];
  companySize?: string[];
  industry?: string[];
}

// Activity logging
export interface ActivityLog {
  id: UUID;
  userId: UUID;
  action: string;
  description?: string;
  epic: 'core' | 'jobs' | 'resumes' | 'ai_suggestions' | 'skills' | 'certifications' | 'company_research';
  metadata?: JSONString;
  ipAddress?: string;
  userAgent?: string;
  createdAt: Timestamp;
}

// Notification types
export interface Notification {
  id: UUID;
  userId: UUID;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  isRead: boolean;
  actionUrl?: URL;
  createdAt: Timestamp;
  expiresAt?: Timestamp;
}

// Settings and preferences
export interface UserPreferences {
  jobAlertFrequency: 'never' | 'daily' | 'weekly' | 'monthly';
  autoSaveResume: boolean;
  resumePrivacyLevel: 'private' | 'public' | 'recruiters_only';
  enableAiSuggestions: boolean;
  aiSuggestionFrequency: 'real_time' | 'daily' | 'weekly';
  emailNotifications: boolean;
  pushNotifications: boolean;
  smsNotifications: boolean;
  profileVisibility: 'private' | 'public' | 'connections_only';
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
}

// API configuration
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
  headers: Record<string, string>;
}