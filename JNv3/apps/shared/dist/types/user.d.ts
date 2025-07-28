/**
 * User-related types for JobQuest Navigator v2
 */
import { BaseEntity, Email, UUID, Timestamp, UserPreferences } from './common';
export type JobSearchStatus = 'not_looking' | 'casually_looking' | 'actively_looking' | 'open_to_offers';
export type CareerLevel = 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'manager' | 'director' | 'executive';
export type WorkType = 'remote' | 'hybrid' | 'onsite' | 'flexible';
export interface User extends BaseEntity {
    email: Email;
    username: string;
    fullName?: string;
    dateOfBirth?: string;
    bio?: string;
    currentJobTitle?: string;
    yearsOfExperience?: number;
    industry?: string;
    careerLevel?: CareerLevel;
    jobSearchStatus: JobSearchStatus;
    salaryExpectationMin?: number;
    salaryExpectationMax?: number;
    preferredWorkType?: WorkType;
    isVerified: boolean;
    cognitoSub?: string;
    dateJoined: Timestamp;
    lastLogin?: Timestamp;
    lastLoginIp?: string;
}
export interface CreateUserInput {
    email: Email;
    username: string;
    fullName?: string;
    password: string;
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
export interface UserProfile extends User {
    preferences: UserPreferences;
    skillsCount: number;
    certificationsCount: number;
    applicationsCount: number;
    savedJobsCount: number;
    resumesCount: number;
}
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
export interface UserStats {
    totalUsers: number;
    activeUsers: number;
    newUsersThisWeek: number;
    newUsersThisMonth: number;
    usersByCareerLevel: Record<CareerLevel, number>;
    usersByJobSearchStatus: Record<JobSearchStatus, number>;
    averageExperience: number;
}
export interface UserExportData {
    user: User;
    preferences: UserPreferences;
    skills: any[];
    applications: any[];
    savedJobs: any[];
    resumes: any[];
}
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
//# sourceMappingURL=user.d.ts.map