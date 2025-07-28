/**
 * Validation utilities for JobQuest Navigator v2
 */
import { UUID } from '../types/common';
export declare const validateEmail: (email: string) => boolean;
export declare const isValidEmailDomain: (email: string) => boolean;
export interface PasswordValidationResult {
    isValid: boolean;
    score: number;
    errors: string[];
}
export declare const validatePassword: (password: string) => PasswordValidationResult;
export declare const validateUUID: (uuid: string) => boolean;
export declare const isValidUUID: (value: any) => value is UUID;
export declare const validateURL: (url: string) => boolean;
export declare const validatePhoneNumber: (phone: string, countryCode?: string) => boolean;
export declare const validateDate: (dateString: string) => boolean;
export declare const isValidBirthDate: (dateString: string) => boolean;
export declare const validateSalaryRange: (min?: number, max?: number) => boolean;
export declare const validateExperienceYears: (years: number) => boolean;
export declare const validateJobTitle: (title: string) => boolean;
export declare const validateCompanyName: (name: string) => boolean;
export declare const validateJobDescription: (description: string) => boolean;
export declare const validateFileSize: (size: number, maxSizeMB?: number) => boolean;
export declare const validateFileType: (mimeType: string, allowedTypes: string[]) => boolean;
export interface ValidationRule<T> {
    field: keyof T;
    validator: (value: any) => boolean | string;
    message?: string;
    required?: boolean;
}
export declare const validateForm: <T extends Record<string, any>>(data: T, rules: ValidationRule<T>[]) => {
    isValid: boolean;
    errors: Record<keyof T, string[]>;
};
export declare const sanitizeHTML: (html: string) => string;
export declare const sanitizeString: (str: string) => string;
export declare const businessRules: {
    email: {
        validator: (email: string) => boolean;
        message: string;
    };
    password: {
        validator: (password: string) => boolean;
        message: string;
    };
    jobTitle: {
        validator: (title: string) => boolean;
        message: string;
    };
    companyName: {
        validator: (name: string) => boolean;
        message: string;
    };
    salaryMin: {
        validator: (value: number) => boolean;
        message: string;
    };
    experienceYears: {
        validator: (years: number) => boolean;
        message: string;
    };
};
export declare const VALIDATION_LIMITS: {
    readonly EMAIL_MAX_LENGTH: 254;
    readonly PASSWORD_MIN_LENGTH: 8;
    readonly PASSWORD_MAX_LENGTH: 128;
    readonly JOB_TITLE_MIN_LENGTH: 2;
    readonly JOB_TITLE_MAX_LENGTH: 200;
    readonly COMPANY_NAME_MAX_LENGTH: 200;
    readonly JOB_DESCRIPTION_MIN_LENGTH: 10;
    readonly JOB_DESCRIPTION_MAX_LENGTH: 10000;
    readonly BIO_MAX_LENGTH: 2000;
    readonly MAX_FILE_SIZE_MB: 10;
    readonly MAX_EXPERIENCE_YEARS: 50;
};
//# sourceMappingURL=validation.d.ts.map