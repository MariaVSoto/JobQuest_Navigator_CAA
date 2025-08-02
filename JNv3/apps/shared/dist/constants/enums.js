"use strict";
/**
 * Enumeration constants for JobQuest Navigator v2
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.FILE_TYPE = exports.AI_RESEARCH_STATUS = exports.AI_MODEL = exports.NOTIFICATION_TYPE = exports.ACTIVITY_EPIC = exports.THEME = exports.PRIVACY_LEVEL = exports.NOTIFICATION_FREQUENCY = exports.CURRENCY = exports.SALARY_PERIOD = exports.INDUSTRY = exports.COMPANY_SIZE = exports.PROFICIENCY_LEVEL = exports.SKILL_CATEGORY = exports.CAREER_LEVEL = exports.JOB_SEARCH_STATUS = exports.APPLICATION_STATUS = exports.EXPERIENCE_LEVEL = exports.CONTRACT_TYPE = exports.WORK_TYPE = exports.JOB_TYPE = exports.JOB_STATUS = void 0;
// Job related enums
exports.JOB_STATUS = {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    CLOSED: 'closed',
    EXPIRED: 'expired'
};
exports.JOB_TYPE = {
    FULL_TIME: 'full_time',
    PART_TIME: 'part_time',
    CONTRACT: 'contract',
    FREELANCE: 'freelance',
    INTERNSHIP: 'internship'
};
exports.WORK_TYPE = {
    REMOTE: 'remote',
    HYBRID: 'hybrid',
    ONSITE: 'onsite',
    FLEXIBLE: 'flexible'
};
exports.CONTRACT_TYPE = {
    PERMANENT: 'permanent',
    CONTRACT: 'contract',
    TEMPORARY: 'temporary',
    APPRENTICESHIP: 'apprenticeship',
    VOLUNTEER: 'volunteer'
};
exports.EXPERIENCE_LEVEL = {
    ENTRY: 'entry',
    JUNIOR: 'junior',
    MID: 'mid',
    SENIOR: 'senior',
    LEAD: 'lead',
    MANAGER: 'manager',
    DIRECTOR: 'director',
    EXECUTIVE: 'executive'
};
// Application related enums
exports.APPLICATION_STATUS = {
    APPLIED: 'applied',
    SCREENING: 'screening',
    INTERVIEW: 'interview',
    OFFER: 'offer',
    REJECTED: 'rejected',
    WITHDRAWN: 'withdrawn'
};
// User related enums
exports.JOB_SEARCH_STATUS = {
    NOT_LOOKING: 'not_looking',
    CASUALLY_LOOKING: 'casually_looking',
    ACTIVELY_LOOKING: 'actively_looking',
    OPEN_TO_OFFERS: 'open_to_offers'
};
exports.CAREER_LEVEL = {
    ENTRY: 'entry',
    JUNIOR: 'junior',
    MID: 'mid',
    SENIOR: 'senior',
    LEAD: 'lead',
    MANAGER: 'manager',
    DIRECTOR: 'director',
    EXECUTIVE: 'executive'
};
// Skill related enums
exports.SKILL_CATEGORY = {
    PROGRAMMING: 'programming',
    FRAMEWORK: 'framework',
    DATABASE: 'database',
    CLOUD: 'cloud',
    DEVOPS: 'devops',
    DESIGN: 'design',
    MANAGEMENT: 'management',
    COMMUNICATION: 'communication',
    LANGUAGE: 'language',
    OTHER: 'other'
};
exports.PROFICIENCY_LEVEL = {
    BEGINNER: 'beginner',
    INTERMEDIATE: 'intermediate',
    ADVANCED: 'advanced',
    EXPERT: 'expert'
};
// Company related enums
exports.COMPANY_SIZE = {
    STARTUP: 'startup',
    SMALL: 'small',
    MEDIUM: 'medium',
    LARGE: 'large',
    ENTERPRISE: 'enterprise'
};
exports.INDUSTRY = {
    TECHNOLOGY: 'technology',
    FINANCE: 'finance',
    HEALTHCARE: 'healthcare',
    EDUCATION: 'education',
    RETAIL: 'retail',
    MANUFACTURING: 'manufacturing',
    CONSULTING: 'consulting',
    MEDIA: 'media',
    NON_PROFIT: 'non_profit',
    GOVERNMENT: 'government',
    OTHER: 'other'
};
// Salary related enums
exports.SALARY_PERIOD = {
    HOURLY: 'hourly',
    DAILY: 'daily',
    WEEKLY: 'weekly',
    MONTHLY: 'monthly',
    YEARLY: 'yearly'
};
exports.CURRENCY = {
    USD: 'USD',
    EUR: 'EUR',
    GBP: 'GBP',
    CAD: 'CAD',
    AUD: 'AUD',
    JPY: 'JPY',
    CNY: 'CNY',
    INR: 'INR'
};
// User preferences enums
exports.NOTIFICATION_FREQUENCY = {
    NEVER: 'never',
    REAL_TIME: 'real_time',
    DAILY: 'daily',
    WEEKLY: 'weekly',
    MONTHLY: 'monthly'
};
exports.PRIVACY_LEVEL = {
    PRIVATE: 'private',
    PUBLIC: 'public',
    RECRUITERS_ONLY: 'recruiters_only',
    CONNECTIONS_ONLY: 'connections_only'
};
exports.THEME = {
    LIGHT: 'light',
    DARK: 'dark',
    AUTO: 'auto'
};
// Activity logging enums
exports.ACTIVITY_EPIC = {
    CORE: 'core',
    JOBS: 'jobs',
    RESUMES: 'resumes',
    AI_SUGGESTIONS: 'ai_suggestions',
    SKILLS: 'skills',
    CERTIFICATIONS: 'certifications',
    COMPANY_RESEARCH: 'company_research'
};
// Notification types
exports.NOTIFICATION_TYPE = {
    INFO: 'info',
    SUCCESS: 'success',
    WARNING: 'warning',
    ERROR: 'error'
};
// AI related enums
exports.AI_MODEL = {
    GPT4: 'gpt-4',
    GPT4_TURBO: 'gpt-4-turbo',
    GPT35_TURBO: 'gpt-3.5-turbo',
    CLAUDE_3: 'claude-3-sonnet',
    CLAUDE_3_HAIKU: 'claude-3-haiku'
};
exports.AI_RESEARCH_STATUS = {
    NONE: 'none',
    PENDING: 'pending',
    COMPLETED: 'completed',
    FAILED: 'failed'
};
// File upload enums
exports.FILE_TYPE = {
    PDF: 'application/pdf',
    DOC: 'application/msword',
    DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    TXT: 'text/plain',
    IMAGE_JPEG: 'image/jpeg',
    IMAGE_PNG: 'image/png',
    IMAGE_GIF: 'image/gif'
};
//# sourceMappingURL=enums.js.map