/**
 * Enumeration constants for JobQuest Navigator v2
 */

// Job related enums
export const JOB_STATUS = {
  DRAFT: 'draft',
  PUBLISHED: 'published', 
  CLOSED: 'closed',
  EXPIRED: 'expired'
} as const;

export const JOB_TYPE = {
  FULL_TIME: 'full_time',
  PART_TIME: 'part_time',
  CONTRACT: 'contract',
  FREELANCE: 'freelance',
  INTERNSHIP: 'internship'
} as const;

export const WORK_TYPE = {
  REMOTE: 'remote',
  HYBRID: 'hybrid',
  ONSITE: 'onsite',
  FLEXIBLE: 'flexible'
} as const;

export const CONTRACT_TYPE = {
  PERMANENT: 'permanent',
  CONTRACT: 'contract',
  TEMPORARY: 'temporary',
  APPRENTICESHIP: 'apprenticeship',
  VOLUNTEER: 'volunteer'
} as const;

export const EXPERIENCE_LEVEL = {
  ENTRY: 'entry',
  JUNIOR: 'junior',
  MID: 'mid',
  SENIOR: 'senior',
  LEAD: 'lead',
  MANAGER: 'manager',
  DIRECTOR: 'director',
  EXECUTIVE: 'executive'
} as const;

// Application related enums
export const APPLICATION_STATUS = {
  APPLIED: 'applied',
  SCREENING: 'screening',
  INTERVIEW: 'interview',
  OFFER: 'offer',
  REJECTED: 'rejected',
  WITHDRAWN: 'withdrawn'
} as const;

// User related enums
export const JOB_SEARCH_STATUS = {
  NOT_LOOKING: 'not_looking',
  CASUALLY_LOOKING: 'casually_looking',
  ACTIVELY_LOOKING: 'actively_looking',
  OPEN_TO_OFFERS: 'open_to_offers'
} as const;

export const CAREER_LEVEL = {
  ENTRY: 'entry',
  JUNIOR: 'junior',
  MID: 'mid',
  SENIOR: 'senior',
  LEAD: 'lead',
  MANAGER: 'manager',
  DIRECTOR: 'director',
  EXECUTIVE: 'executive'
} as const;

// Skill related enums
export const SKILL_CATEGORY = {
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
} as const;

export const PROFICIENCY_LEVEL = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced',
  EXPERT: 'expert'
} as const;

// Company related enums
export const COMPANY_SIZE = {
  STARTUP: 'startup',
  SMALL: 'small',
  MEDIUM: 'medium',
  LARGE: 'large',
  ENTERPRISE: 'enterprise'
} as const;

export const INDUSTRY = {
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
} as const;

// Salary related enums
export const SALARY_PERIOD = {
  HOURLY: 'hourly',
  DAILY: 'daily',
  WEEKLY: 'weekly',
  MONTHLY: 'monthly',
  YEARLY: 'yearly'
} as const;

export const CURRENCY = {
  USD: 'USD',
  EUR: 'EUR',
  GBP: 'GBP',
  CAD: 'CAD',
  AUD: 'AUD',
  JPY: 'JPY',
  CNY: 'CNY',
  INR: 'INR'
} as const;

// User preferences enums
export const NOTIFICATION_FREQUENCY = {
  NEVER: 'never',
  REAL_TIME: 'real_time',
  DAILY: 'daily',
  WEEKLY: 'weekly',
  MONTHLY: 'monthly'
} as const;

export const PRIVACY_LEVEL = {
  PRIVATE: 'private',
  PUBLIC: 'public',
  RECRUITERS_ONLY: 'recruiters_only',
  CONNECTIONS_ONLY: 'connections_only'
} as const;

export const THEME = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto'
} as const;

// Activity logging enums
export const ACTIVITY_EPIC = {
  CORE: 'core',
  JOBS: 'jobs',
  RESUMES: 'resumes',
  AI_SUGGESTIONS: 'ai_suggestions',
  SKILLS: 'skills',
  CERTIFICATIONS: 'certifications',
  COMPANY_RESEARCH: 'company_research'
} as const;

// Notification types
export const NOTIFICATION_TYPE = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error'
} as const;

// AI related enums
export const AI_MODEL = {
  GPT4: 'gpt-4',
  GPT4_TURBO: 'gpt-4-turbo',
  GPT35_TURBO: 'gpt-3.5-turbo',
  CLAUDE_3: 'claude-3-sonnet',
  CLAUDE_3_HAIKU: 'claude-3-haiku'
} as const;

export const AI_RESEARCH_STATUS = {
  NONE: 'none',
  PENDING: 'pending',
  COMPLETED: 'completed',
  FAILED: 'failed'
} as const;

// File upload enums
export const FILE_TYPE = {
  PDF: 'application/pdf',
  DOC: 'application/msword',
  DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  TXT: 'text/plain',
  IMAGE_JPEG: 'image/jpeg',
  IMAGE_PNG: 'image/png',
  IMAGE_GIF: 'image/gif'
} as const;

// Type guards for runtime type checking
export type JobStatus = typeof JOB_STATUS[keyof typeof JOB_STATUS];
export type JobType = typeof JOB_TYPE[keyof typeof JOB_TYPE];
export type WorkType = typeof WORK_TYPE[keyof typeof WORK_TYPE];
export type ContractType = typeof CONTRACT_TYPE[keyof typeof CONTRACT_TYPE];
export type ExperienceLevel = typeof EXPERIENCE_LEVEL[keyof typeof EXPERIENCE_LEVEL];
export type ApplicationStatus = typeof APPLICATION_STATUS[keyof typeof APPLICATION_STATUS];
export type JobSearchStatus = typeof JOB_SEARCH_STATUS[keyof typeof JOB_SEARCH_STATUS];
export type CareerLevel = typeof CAREER_LEVEL[keyof typeof CAREER_LEVEL];
export type SkillCategory = typeof SKILL_CATEGORY[keyof typeof SKILL_CATEGORY];
export type ProficiencyLevel = typeof PROFICIENCY_LEVEL[keyof typeof PROFICIENCY_LEVEL];
export type CompanySize = typeof COMPANY_SIZE[keyof typeof COMPANY_SIZE];
export type Industry = typeof INDUSTRY[keyof typeof INDUSTRY];
export type SalaryPeriod = typeof SALARY_PERIOD[keyof typeof SALARY_PERIOD];
export type Currency = typeof CURRENCY[keyof typeof CURRENCY];
export type NotificationFrequency = typeof NOTIFICATION_FREQUENCY[keyof typeof NOTIFICATION_FREQUENCY];
export type PrivacyLevel = typeof PRIVACY_LEVEL[keyof typeof PRIVACY_LEVEL];
export type Theme = typeof THEME[keyof typeof THEME];
export type ActivityEpic = typeof ACTIVITY_EPIC[keyof typeof ACTIVITY_EPIC];
export type NotificationType = typeof NOTIFICATION_TYPE[keyof typeof NOTIFICATION_TYPE];
export type AiModel = typeof AI_MODEL[keyof typeof AI_MODEL];
export type AiResearchStatus = typeof AI_RESEARCH_STATUS[keyof typeof AI_RESEARCH_STATUS];
export type FileType = typeof FILE_TYPE[keyof typeof FILE_TYPE];