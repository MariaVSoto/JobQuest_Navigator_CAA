/**
 * JobQuest Navigator v2 - Shared Module
 * Main entry point for all shared components
 */
export * from './types/common';
export * from './types/user';
export * from './constants/enums';
export * from './utils/validation';
export * from './utils/formatting';
export { type UUID, type Email, type Timestamp, type ApiResponse, type PaginatedResponse, type User, type UserProfile, type CreateUserInput, type UpdateUserInput, type LoginInput, type LoginResponse, JOB_STATUS, JOB_TYPE, WORK_TYPE, APPLICATION_STATUS, JOB_SEARCH_STATUS, CAREER_LEVEL, SKILL_CATEGORY, PROFICIENCY_LEVEL, validateEmail, validatePassword, validateUUID, validateURL, businessRules, formatDate, formatCurrency, formatSalaryRange, formatName, formatLocation, formatters } from './index';
export declare const VERSION = "2.0.0";
export declare const PACKAGE_NAME = "@jobquest/shared";
export declare const CONFIG: {
    readonly API_TIMEOUT: 30000;
    readonly MAX_FILE_SIZE_MB: 10;
    readonly SUPPORTED_IMAGE_TYPES: readonly ["image/jpeg", "image/png", "image/gif"];
    readonly SUPPORTED_DOCUMENT_TYPES: readonly ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"];
    readonly DATE_FORMATS: {
        readonly DEFAULT: "MMM d, yyyy";
        readonly FULL: "MMMM d, yyyy";
        readonly SHORT: "MM/dd/yyyy";
        readonly ISO: "yyyy-MM-dd";
    };
    readonly PAGINATION: {
        readonly DEFAULT_PAGE_SIZE: 20;
        readonly MAX_PAGE_SIZE: 100;
    };
};
export declare const utils: {
    readonly isValidEmail: (email: string) => boolean;
    readonly isValidUUID: (uuid: string) => boolean;
    readonly formatUserName: (firstName?: string, lastName?: string) => string;
    readonly formatJobTitle: (title: string) => string;
    readonly isStrongPassword: (password: string) => boolean;
    readonly parseApiDate: (dateString: string) => Date | null;
    readonly safeJsonParse: <T>(jsonString: string, fallback: T) => T;
    readonly removeDuplicates: <T>(array: T[]) => T[];
    readonly removeEmptyFields: <T extends Record<string, any>>(obj: T) => Partial<T>;
};
export declare class ValidationError extends Error {
    field?: string | undefined;
    code?: string | undefined;
    constructor(message: string, field?: string | undefined, code?: string | undefined);
}
export declare class AuthenticationError extends Error {
    constructor(message?: string);
}
export declare class AuthorizationError extends Error {
    constructor(message?: string);
}
export declare class NotFoundError extends Error {
    constructor(resource?: string);
}
declare const _default: {
    VERSION: string;
    PACKAGE_NAME: string;
    CONFIG: {
        readonly API_TIMEOUT: 30000;
        readonly MAX_FILE_SIZE_MB: 10;
        readonly SUPPORTED_IMAGE_TYPES: readonly ["image/jpeg", "image/png", "image/gif"];
        readonly SUPPORTED_DOCUMENT_TYPES: readonly ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"];
        readonly DATE_FORMATS: {
            readonly DEFAULT: "MMM d, yyyy";
            readonly FULL: "MMMM d, yyyy";
            readonly SHORT: "MM/dd/yyyy";
            readonly ISO: "yyyy-MM-dd";
        };
        readonly PAGINATION: {
            readonly DEFAULT_PAGE_SIZE: 20;
            readonly MAX_PAGE_SIZE: 100;
        };
    };
    utils: {
        readonly isValidEmail: (email: string) => boolean;
        readonly isValidUUID: (uuid: string) => boolean;
        readonly formatUserName: (firstName?: string, lastName?: string) => string;
        readonly formatJobTitle: (title: string) => string;
        readonly isStrongPassword: (password: string) => boolean;
        readonly parseApiDate: (dateString: string) => Date | null;
        readonly safeJsonParse: <T>(jsonString: string, fallback: T) => T;
        readonly removeDuplicates: <T>(array: T[]) => T[];
        readonly removeEmptyFields: <T extends Record<string, any>>(obj: T) => Partial<T>;
    };
    ValidationError: typeof ValidationError;
    AuthenticationError: typeof AuthenticationError;
    AuthorizationError: typeof AuthorizationError;
    NotFoundError: typeof NotFoundError;
};
export default _default;
//# sourceMappingURL=index.d.ts.map