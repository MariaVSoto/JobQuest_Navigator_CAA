/**
 * Enumeration constants for JobQuest Navigator v2
 */
export declare const JOB_STATUS: {
    readonly DRAFT: "draft";
    readonly PUBLISHED: "published";
    readonly CLOSED: "closed";
    readonly EXPIRED: "expired";
};
export declare const JOB_TYPE: {
    readonly FULL_TIME: "full_time";
    readonly PART_TIME: "part_time";
    readonly CONTRACT: "contract";
    readonly FREELANCE: "freelance";
    readonly INTERNSHIP: "internship";
};
export declare const WORK_TYPE: {
    readonly REMOTE: "remote";
    readonly HYBRID: "hybrid";
    readonly ONSITE: "onsite";
    readonly FLEXIBLE: "flexible";
};
export declare const CONTRACT_TYPE: {
    readonly PERMANENT: "permanent";
    readonly CONTRACT: "contract";
    readonly TEMPORARY: "temporary";
    readonly APPRENTICESHIP: "apprenticeship";
    readonly VOLUNTEER: "volunteer";
};
export declare const EXPERIENCE_LEVEL: {
    readonly ENTRY: "entry";
    readonly JUNIOR: "junior";
    readonly MID: "mid";
    readonly SENIOR: "senior";
    readonly LEAD: "lead";
    readonly MANAGER: "manager";
    readonly DIRECTOR: "director";
    readonly EXECUTIVE: "executive";
};
export declare const APPLICATION_STATUS: {
    readonly APPLIED: "applied";
    readonly SCREENING: "screening";
    readonly INTERVIEW: "interview";
    readonly OFFER: "offer";
    readonly REJECTED: "rejected";
    readonly WITHDRAWN: "withdrawn";
};
export declare const JOB_SEARCH_STATUS: {
    readonly NOT_LOOKING: "not_looking";
    readonly CASUALLY_LOOKING: "casually_looking";
    readonly ACTIVELY_LOOKING: "actively_looking";
    readonly OPEN_TO_OFFERS: "open_to_offers";
};
export declare const CAREER_LEVEL: {
    readonly ENTRY: "entry";
    readonly JUNIOR: "junior";
    readonly MID: "mid";
    readonly SENIOR: "senior";
    readonly LEAD: "lead";
    readonly MANAGER: "manager";
    readonly DIRECTOR: "director";
    readonly EXECUTIVE: "executive";
};
export declare const SKILL_CATEGORY: {
    readonly PROGRAMMING: "programming";
    readonly FRAMEWORK: "framework";
    readonly DATABASE: "database";
    readonly CLOUD: "cloud";
    readonly DEVOPS: "devops";
    readonly DESIGN: "design";
    readonly MANAGEMENT: "management";
    readonly COMMUNICATION: "communication";
    readonly LANGUAGE: "language";
    readonly OTHER: "other";
};
export declare const PROFICIENCY_LEVEL: {
    readonly BEGINNER: "beginner";
    readonly INTERMEDIATE: "intermediate";
    readonly ADVANCED: "advanced";
    readonly EXPERT: "expert";
};
export declare const COMPANY_SIZE: {
    readonly STARTUP: "startup";
    readonly SMALL: "small";
    readonly MEDIUM: "medium";
    readonly LARGE: "large";
    readonly ENTERPRISE: "enterprise";
};
export declare const INDUSTRY: {
    readonly TECHNOLOGY: "technology";
    readonly FINANCE: "finance";
    readonly HEALTHCARE: "healthcare";
    readonly EDUCATION: "education";
    readonly RETAIL: "retail";
    readonly MANUFACTURING: "manufacturing";
    readonly CONSULTING: "consulting";
    readonly MEDIA: "media";
    readonly NON_PROFIT: "non_profit";
    readonly GOVERNMENT: "government";
    readonly OTHER: "other";
};
export declare const SALARY_PERIOD: {
    readonly HOURLY: "hourly";
    readonly DAILY: "daily";
    readonly WEEKLY: "weekly";
    readonly MONTHLY: "monthly";
    readonly YEARLY: "yearly";
};
export declare const CURRENCY: {
    readonly USD: "USD";
    readonly EUR: "EUR";
    readonly GBP: "GBP";
    readonly CAD: "CAD";
    readonly AUD: "AUD";
    readonly JPY: "JPY";
    readonly CNY: "CNY";
    readonly INR: "INR";
};
export declare const NOTIFICATION_FREQUENCY: {
    readonly NEVER: "never";
    readonly REAL_TIME: "real_time";
    readonly DAILY: "daily";
    readonly WEEKLY: "weekly";
    readonly MONTHLY: "monthly";
};
export declare const PRIVACY_LEVEL: {
    readonly PRIVATE: "private";
    readonly PUBLIC: "public";
    readonly RECRUITERS_ONLY: "recruiters_only";
    readonly CONNECTIONS_ONLY: "connections_only";
};
export declare const THEME: {
    readonly LIGHT: "light";
    readonly DARK: "dark";
    readonly AUTO: "auto";
};
export declare const ACTIVITY_EPIC: {
    readonly CORE: "core";
    readonly JOBS: "jobs";
    readonly RESUMES: "resumes";
    readonly AI_SUGGESTIONS: "ai_suggestions";
    readonly SKILLS: "skills";
    readonly CERTIFICATIONS: "certifications";
    readonly COMPANY_RESEARCH: "company_research";
};
export declare const NOTIFICATION_TYPE: {
    readonly INFO: "info";
    readonly SUCCESS: "success";
    readonly WARNING: "warning";
    readonly ERROR: "error";
};
export declare const AI_MODEL: {
    readonly GPT4: "gpt-4";
    readonly GPT4_TURBO: "gpt-4-turbo";
    readonly GPT35_TURBO: "gpt-3.5-turbo";
    readonly CLAUDE_3: "claude-3-sonnet";
    readonly CLAUDE_3_HAIKU: "claude-3-haiku";
};
export declare const AI_RESEARCH_STATUS: {
    readonly NONE: "none";
    readonly PENDING: "pending";
    readonly COMPLETED: "completed";
    readonly FAILED: "failed";
};
export declare const FILE_TYPE: {
    readonly PDF: "application/pdf";
    readonly DOC: "application/msword";
    readonly DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
    readonly TXT: "text/plain";
    readonly IMAGE_JPEG: "image/jpeg";
    readonly IMAGE_PNG: "image/png";
    readonly IMAGE_GIF: "image/gif";
};
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
//# sourceMappingURL=enums.d.ts.map