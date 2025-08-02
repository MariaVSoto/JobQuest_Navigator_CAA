/**
 * Common types used throughout JobQuest Navigator v2
 */
export type UUID = string;
export type Timestamp = string;
export type Email = string;
export type URL = string;
export type JSONString = string;
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
export interface FileUpload {
    id: UUID;
    filename: string;
    originalName: string;
    mimeType: string;
    size: number;
    url: URL;
    uploadedAt: Timestamp;
}
export interface Location {
    text: string;
    country?: string;
    state?: string;
    city?: string;
    isRemote?: boolean;
}
export interface Money {
    amount: number;
    currency: string;
}
export interface SalaryRange {
    min?: Money;
    max?: Money;
    period: 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly';
}
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
export interface ApiConfig {
    baseUrl: string;
    timeout: number;
    retries: number;
    headers: Record<string, string>;
}
//# sourceMappingURL=common.d.ts.map