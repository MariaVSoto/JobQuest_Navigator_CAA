/**
 * User-related types for JobQuest Navigator v2
 */

import { BaseEntity, Email, UUID, Timestamp, UserPreferences } from './common';

// User status and level enums
export type JobSearchStatus = 'not_looking' | 'casually_looking' | 'actively_looking' | 'open_to_offers';
export type CareerLevel = 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'manager' | 'director' | 'executive';
export type WorkType = 'remote' | 'hybrid' | 'onsite' | 'flexible';

// Core User type
export interface User extends BaseEntity {
  email: Email;
  username: string;
  fullName?: string;
  dateOfBirth?: string; // ISO date string
  bio?: string;
  
  // Career Information
  currentJobTitle?: string;
  yearsOfExperience?: number;
  industry?: string;
  careerLevel?: CareerLevel;
  
  // Job Search Preferences
  jobSearchStatus: JobSearchStatus;
  salaryExpectationMin?: number;
  salaryExpectationMax?: number;
  preferredWorkType?: WorkType;
  
  // Authentication & Verification
  isVerified: boolean;
  cognitoSub?: string; // AWS Cognito user ID
  
  // Timestamps
  dateJoined: Timestamp;
  lastLogin?: Timestamp;
  lastLoginIp?: string;
}

// User creation/update types
export interface CreateUserInput {
  email: Email;
  username: string;
  fullName?: string;
  password: string; // Only used during creation
}

export interface UpdateUserInput {
  fullName?: string;
  dateOfBirth?: string;
  bio?: string;
  currentJobTitle?: string;
  yearsOfExperience?: number;
  industry?: string;
  careerLevel?: CareerLevel;
  jobSearchStatus?: JobSearchStatus;
  salaryExpectationMin?: number;
  salaryExpectationMax?: number;
  preferredWorkType?: WorkType;
}

// Authentication types
export interface LoginInput {
  email: Email;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface RefreshTokenInput {
  refreshToken: string;
}

export interface ChangePasswordInput {
  currentPassword: string;
  newPassword: string;
}

export interface ResetPasswordInput {
  email: Email;
}

export interface ConfirmResetPasswordInput {
  token: string;
  newPassword: string;
}

// User profile types
export interface UserProfile extends User {
  preferences: UserPreferences;
  skillsCount: number;
  certificationsCount: number;
  applicationsCount: number;
  savedJobsCount: number;
  resumesCount: number;
}

// User search and filtering
export interface UserSearchFilters {
  query?: string;
  industry?: string[];
  careerLevel?: CareerLevel[];
  yearsOfExperience?: {
    min?: number;
    max?: number;
  };
  skills?: string[];
  location?: string;
  jobSearchStatus?: JobSearchStatus[];
}

// User activity and engagement
export interface UserActivity {
  userId: UUID;
  totalLogins: number;
  lastActiveDate: Timestamp;
  jobsViewed: number;
  jobsApplied: number;
  profileViews: number;
  searchesPerformed: number;
  resumesGenerated: number;
}

// User statistics for analytics
export interface UserStats {
  totalUsers: number;
  activeUsers: number;
  newUsersThisWeek: number;
  newUsersThisMonth: number;
  usersByCareerLevel: Record<CareerLevel, number>;
  usersByJobSearchStatus: Record<JobSearchStatus, number>;
  averageExperience: number;
}

// User export/import types
export interface UserExportData {
  user: User;
  preferences: UserPreferences;
  skills: any[]; // Will be defined in skill.ts
  applications: any[]; // Will be defined in application.ts
  savedJobs: any[]; // Will be defined in job.ts
  resumes: any[]; // Will be defined when resume types are created
}

// Verification and security
export interface EmailVerification {
  userId: UUID;
  email: Email;
  token: string;
  expiresAt: Timestamp;
  isUsed: boolean;
}

export interface UserSession {
  id: UUID;
  userId: UUID;
  accessToken: string;
  refreshToken: string;
  ipAddress: string;
  userAgent: string;
  isActive: boolean;
  expiresAt: Timestamp;
  createdAt: Timestamp;
  lastUsedAt: Timestamp;
}