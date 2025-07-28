"use strict";
/**
 * Validation utilities for JobQuest Navigator v2
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.VALIDATION_LIMITS = exports.businessRules = exports.sanitizeString = exports.sanitizeHTML = exports.validateForm = exports.validateFileType = exports.validateFileSize = exports.validateJobDescription = exports.validateCompanyName = exports.validateJobTitle = exports.validateExperienceYears = exports.validateSalaryRange = exports.isValidBirthDate = exports.validateDate = exports.validatePhoneNumber = exports.validateURL = exports.isValidUUID = exports.validateUUID = exports.validatePassword = exports.isValidEmailDomain = exports.validateEmail = void 0;
const validator_1 = __importDefault(require("validator"));
// Email validation
const validateEmail = (email) => {
    return validator_1.default.isEmail(email);
};
exports.validateEmail = validateEmail;
const isValidEmailDomain = (email) => {
    if (!(0, exports.validateEmail)(email))
        return false;
    const domain = email.split('@')[1];
    // Add custom business logic for allowed/blocked domains
    const blockedDomains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com'];
    return !blockedDomains.includes(domain.toLowerCase());
};
exports.isValidEmailDomain = isValidEmailDomain;
const validatePassword = (password) => {
    const errors = [];
    let score = 0;
    // Length check
    if (password.length < 8) {
        errors.push('Password must be at least 8 characters long');
    }
    else if (password.length >= 12) {
        score += 25;
    }
    else {
        score += 15;
    }
    // Character variety checks
    if (!/[a-z]/.test(password)) {
        errors.push('Password must contain at least one lowercase letter');
    }
    else {
        score += 15;
    }
    if (!/[A-Z]/.test(password)) {
        errors.push('Password must contain at least one uppercase letter');
    }
    else {
        score += 15;
    }
    if (!/\d/.test(password)) {
        errors.push('Password must contain at least one number');
    }
    else {
        score += 15;
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
        errors.push('Password must contain at least one special character');
    }
    else {
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
exports.validatePassword = validatePassword;
// UUID validation
const validateUUID = (uuid) => {
    return validator_1.default.isUUID(uuid);
};
exports.validateUUID = validateUUID;
const isValidUUID = (value) => {
    return typeof value === 'string' && (0, exports.validateUUID)(value);
};
exports.isValidUUID = isValidUUID;
// URL validation
const validateURL = (url) => {
    return validator_1.default.isURL(url, {
        protocols: ['http', 'https'],
        require_protocol: true
    });
};
exports.validateURL = validateURL;
// Phone number validation
const validatePhoneNumber = (phone, countryCode = 'US') => {
    return validator_1.default.isMobilePhone(phone, countryCode);
};
exports.validatePhoneNumber = validatePhoneNumber;
// Date validation
const validateDate = (dateString) => {
    return validator_1.default.isISO8601(dateString);
};
exports.validateDate = validateDate;
const isValidBirthDate = (dateString) => {
    if (!(0, exports.validateDate)(dateString))
        return false;
    const date = new Date(dateString);
    const now = new Date();
    const age = now.getFullYear() - date.getFullYear();
    // Must be between 16 and 120 years old
    return age >= 16 && age <= 120;
};
exports.isValidBirthDate = isValidBirthDate;
// Job-related validation
const validateSalaryRange = (min, max) => {
    if (min !== undefined && min < 0)
        return false;
    if (max !== undefined && max < 0)
        return false;
    if (min !== undefined && max !== undefined && min > max)
        return false;
    return true;
};
exports.validateSalaryRange = validateSalaryRange;
const validateExperienceYears = (years) => {
    return years >= 0 && years <= 50;
};
exports.validateExperienceYears = validateExperienceYears;
// Text validation
const validateJobTitle = (title) => {
    return title.length >= 2 && title.length <= 200;
};
exports.validateJobTitle = validateJobTitle;
const validateCompanyName = (name) => {
    return name.length >= 1 && name.length <= 200;
};
exports.validateCompanyName = validateCompanyName;
const validateJobDescription = (description) => {
    return description.length >= 10 && description.length <= 10000;
};
exports.validateJobDescription = validateJobDescription;
// File validation
const validateFileSize = (size, maxSizeMB = 10) => {
    return size <= maxSizeMB * 1024 * 1024;
};
exports.validateFileSize = validateFileSize;
const validateFileType = (mimeType, allowedTypes) => {
    return allowedTypes.includes(mimeType);
};
exports.validateFileType = validateFileType;
const validateForm = (data, rules) => {
    const errors = {};
    for (const rule of rules) {
        const value = data[rule.field];
        const fieldErrors = [];
        // Check required fields
        if (rule.required && (value === undefined || value === null || value === '')) {
            fieldErrors.push(rule.message || `${String(rule.field)} is required`);
        }
        else if (value !== undefined && value !== null && value !== '') {
            // Run validator
            const result = rule.validator(value);
            if (result === false) {
                fieldErrors.push(rule.message || `${String(rule.field)} is invalid`);
            }
            else if (typeof result === 'string') {
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
exports.validateForm = validateForm;
// Sanitization utilities
const sanitizeHTML = (html) => {
    return validator_1.default.escape(html);
};
exports.sanitizeHTML = sanitizeHTML;
const sanitizeString = (str) => {
    return validator_1.default.trim(validator_1.default.escape(str));
};
exports.sanitizeString = sanitizeString;
// Business validation rules
exports.businessRules = {
    email: {
        validator: exports.validateEmail,
        message: 'Please enter a valid email address'
    },
    password: {
        validator: (password) => (0, exports.validatePassword)(password).isValid,
        message: 'Password must be at least 8 characters with uppercase, lowercase, number, and special character'
    },
    jobTitle: {
        validator: exports.validateJobTitle,
        message: 'Job title must be between 2 and 200 characters'
    },
    companyName: {
        validator: exports.validateCompanyName,
        message: 'Company name must be between 1 and 200 characters'
    },
    salaryMin: {
        validator: (value) => value >= 0,
        message: 'Minimum salary must be non-negative'
    },
    experienceYears: {
        validator: exports.validateExperienceYears,
        message: 'Experience years must be between 0 and 50'
    }
};
// Export validation constants
exports.VALIDATION_LIMITS = {
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
};
//# sourceMappingURL=validation.js.map