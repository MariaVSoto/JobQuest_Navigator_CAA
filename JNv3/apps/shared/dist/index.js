"use strict";
/**
 * JobQuest Navigator v2 - Shared Module
 * Main entry point for all shared components
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.NotFoundError = exports.AuthorizationError = exports.AuthenticationError = exports.ValidationError = exports.utils = exports.CONFIG = exports.PACKAGE_NAME = exports.VERSION = exports.formatters = exports.formatLocation = exports.formatName = exports.formatSalaryRange = exports.formatCurrency = exports.formatDate = exports.businessRules = exports.validateURL = exports.validateUUID = exports.validatePassword = exports.validateEmail = exports.PROFICIENCY_LEVEL = exports.SKILL_CATEGORY = exports.CAREER_LEVEL = exports.JOB_SEARCH_STATUS = exports.APPLICATION_STATUS = exports.WORK_TYPE = exports.JOB_TYPE = exports.JOB_STATUS = void 0;
// Types
__exportStar(require("./types/common"), exports);
__exportStar(require("./types/user"), exports);
// Constants and Enums
__exportStar(require("./constants/enums"), exports);
// Utilities
__exportStar(require("./utils/validation"), exports);
__exportStar(require("./utils/formatting"), exports);
// Re-export commonly used items with convenient aliases
var index_1 = require("./index");
// Enum aliases
Object.defineProperty(exports, "JOB_STATUS", { enumerable: true, get: function () { return index_1.JOB_STATUS; } });
Object.defineProperty(exports, "JOB_TYPE", { enumerable: true, get: function () { return index_1.JOB_TYPE; } });
Object.defineProperty(exports, "WORK_TYPE", { enumerable: true, get: function () { return index_1.WORK_TYPE; } });
Object.defineProperty(exports, "APPLICATION_STATUS", { enumerable: true, get: function () { return index_1.APPLICATION_STATUS; } });
Object.defineProperty(exports, "JOB_SEARCH_STATUS", { enumerable: true, get: function () { return index_1.JOB_SEARCH_STATUS; } });
Object.defineProperty(exports, "CAREER_LEVEL", { enumerable: true, get: function () { return index_1.CAREER_LEVEL; } });
Object.defineProperty(exports, "SKILL_CATEGORY", { enumerable: true, get: function () { return index_1.SKILL_CATEGORY; } });
Object.defineProperty(exports, "PROFICIENCY_LEVEL", { enumerable: true, get: function () { return index_1.PROFICIENCY_LEVEL; } });
// Validation aliases
Object.defineProperty(exports, "validateEmail", { enumerable: true, get: function () { return index_1.validateEmail; } });
Object.defineProperty(exports, "validatePassword", { enumerable: true, get: function () { return index_1.validatePassword; } });
Object.defineProperty(exports, "validateUUID", { enumerable: true, get: function () { return index_1.validateUUID; } });
Object.defineProperty(exports, "validateURL", { enumerable: true, get: function () { return index_1.validateURL; } });
Object.defineProperty(exports, "businessRules", { enumerable: true, get: function () { return index_1.businessRules; } });
// Formatting aliases
Object.defineProperty(exports, "formatDate", { enumerable: true, get: function () { return index_1.formatDate; } });
Object.defineProperty(exports, "formatCurrency", { enumerable: true, get: function () { return index_1.formatCurrency; } });
Object.defineProperty(exports, "formatSalaryRange", { enumerable: true, get: function () { return index_1.formatSalaryRange; } });
Object.defineProperty(exports, "formatName", { enumerable: true, get: function () { return index_1.formatName; } });
Object.defineProperty(exports, "formatLocation", { enumerable: true, get: function () { return index_1.formatLocation; } });
Object.defineProperty(exports, "formatters", { enumerable: true, get: function () { return index_1.formatters; } });
// Version info
exports.VERSION = '2.0.0';
exports.PACKAGE_NAME = '@jobquest/shared';
// Configuration constants
exports.CONFIG = {
    API_TIMEOUT: 30000,
    MAX_FILE_SIZE_MB: 10,
    SUPPORTED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif'],
    SUPPORTED_DOCUMENT_TYPES: [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    ],
    DATE_FORMATS: {
        DEFAULT: 'MMM d, yyyy',
        FULL: 'MMMM d, yyyy',
        SHORT: 'MM/dd/yyyy',
        ISO: 'yyyy-MM-dd'
    },
    PAGINATION: {
        DEFAULT_PAGE_SIZE: 20,
        MAX_PAGE_SIZE: 100
    }
};
// Utility functions for common operations
exports.utils = {
    // Type checking utilities
    isValidEmail: (email) => validateEmail(email),
    isValidUUID: (uuid) => validateUUID(uuid),
    // Formatting utilities
    formatUserName: (firstName, lastName) => formatName(firstName, lastName),
    formatJobTitle: (title) => title.trim().replace(/\s+/g, ' '),
    // Common validation patterns
    isStrongPassword: (password) => validatePassword(password).isValid,
    // Data transformation utilities
    parseApiDate: (dateString) => {
        try {
            const date = new Date(dateString);
            return isNaN(date.getTime()) ? null : date;
        }
        catch {
            return null;
        }
    },
    // Safe JSON parsing
    safeJsonParse: (jsonString, fallback) => {
        try {
            return JSON.parse(jsonString);
        }
        catch {
            return fallback;
        }
    },
    // Array utilities
    removeDuplicates: (array) => [...new Set(array)],
    // Object utilities
    removeEmptyFields: (obj) => {
        const result = {};
        for (const [key, value] of Object.entries(obj)) {
            if (value !== null && value !== undefined && value !== '') {
                result[key] = value;
            }
        }
        return result;
    }
};
// Error classes for common scenarios
class ValidationError extends Error {
    constructor(message, field, code) {
        super(message);
        this.field = field;
        this.code = code;
        this.name = 'ValidationError';
    }
}
exports.ValidationError = ValidationError;
class AuthenticationError extends Error {
    constructor(message = 'Authentication failed') {
        super(message);
        this.name = 'AuthenticationError';
    }
}
exports.AuthenticationError = AuthenticationError;
class AuthorizationError extends Error {
    constructor(message = 'Access denied') {
        super(message);
        this.name = 'AuthorizationError';
    }
}
exports.AuthorizationError = AuthorizationError;
class NotFoundError extends Error {
    constructor(resource = 'Resource') {
        super(`${resource} not found`);
        this.name = 'NotFoundError';
    }
}
exports.NotFoundError = NotFoundError;
// Default export with all utilities
exports.default = {
    VERSION: exports.VERSION,
    PACKAGE_NAME: exports.PACKAGE_NAME,
    CONFIG: exports.CONFIG,
    utils: exports.utils,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError
};
//# sourceMappingURL=index.js.map