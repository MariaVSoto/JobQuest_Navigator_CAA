"use strict";
/**
 * Data formatting utilities for JobQuest Navigator v2
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.formatters = exports.formatSkillsList = exports.extractDomain = exports.formatWebsiteUrl = exports.formatStatus = exports.formatPhoneNumber = exports.formatPercentage = exports.formatFileSize = exports.formatExperience = exports.formatLocation = exports.slugify = exports.capitalizeWords = exports.truncateText = exports.formatInitials = exports.formatName = exports.formatCompactNumber = exports.formatSalaryRange = exports.formatMoney = exports.formatCurrency = exports.formatRelativeTime = exports.formatDateTime = exports.formatDate = void 0;
const date_fns_1 = require("date-fns");
// Date formatting utilities
const formatDate = (date, formatString = 'MMM d, yyyy') => {
    try {
        const dateObj = typeof date === 'string' ? (0, date_fns_1.parseISO)(date) : date;
        if (!(0, date_fns_1.isValid)(dateObj))
            return 'Invalid date';
        return (0, date_fns_1.format)(dateObj, formatString);
    }
    catch {
        return 'Invalid date';
    }
};
exports.formatDate = formatDate;
const formatDateTime = (date) => {
    return (0, exports.formatDate)(date, 'MMM d, yyyy h:mm a');
};
exports.formatDateTime = formatDateTime;
const formatRelativeTime = (date) => {
    try {
        const dateObj = typeof date === 'string' ? (0, date_fns_1.parseISO)(date) : date;
        if (!(0, date_fns_1.isValid)(dateObj))
            return 'Unknown';
        return (0, date_fns_1.formatDistance)(dateObj, new Date(), { addSuffix: true });
    }
    catch {
        return 'Unknown';
    }
};
exports.formatRelativeTime = formatRelativeTime;
// Currency and salary formatting
const formatCurrency = (amount, currency = 'USD', locale = 'en-US') => {
    try {
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(amount);
    }
    catch {
        return `${currency} ${amount.toLocaleString()}`;
    }
};
exports.formatCurrency = formatCurrency;
const formatMoney = (money, locale = 'en-US') => {
    return (0, exports.formatCurrency)(money.amount, money.currency, locale);
};
exports.formatMoney = formatMoney;
const formatSalaryRange = (range, locale = 'en-US') => {
    const { min, max, period } = range;
    let result = '';
    if (min && max) {
        result = `${(0, exports.formatMoney)(min, locale)} - ${(0, exports.formatMoney)(max, locale)}`;
    }
    else if (min) {
        result = `${(0, exports.formatMoney)(min, locale)}+`;
    }
    else if (max) {
        result = `Up to ${(0, exports.formatMoney)(max, locale)}`;
    }
    else {
        result = 'Salary not specified';
    }
    // Add period suffix
    const periodSuffix = {
        hourly: '/hour',
        daily: '/day',
        weekly: '/week',
        monthly: '/month',
        yearly: '/year'
    };
    return result + (periodSuffix[period] || '');
};
exports.formatSalaryRange = formatSalaryRange;
// Compact number formatting (e.g., 1.2K, 5.6M)
const formatCompactNumber = (num, locale = 'en-US') => {
    try {
        return new Intl.NumberFormat(locale, {
            notation: 'compact',
            compactDisplay: 'short',
        }).format(num);
    }
    catch {
        // Fallback for older browsers
        if (num >= 1e9) {
            return (num / 1e9).toFixed(1) + 'B';
        }
        else if (num >= 1e6) {
            return (num / 1e6).toFixed(1) + 'M';
        }
        else if (num >= 1e3) {
            return (num / 1e3).toFixed(1) + 'K';
        }
        else {
            return num.toString();
        }
    }
};
exports.formatCompactNumber = formatCompactNumber;
// String formatting utilities
const formatName = (firstName, lastName) => {
    if (firstName && lastName) {
        return `${firstName} ${lastName}`;
    }
    else if (firstName) {
        return firstName;
    }
    else if (lastName) {
        return lastName;
    }
    else {
        return 'Unknown User';
    }
};
exports.formatName = formatName;
const formatInitials = (firstName, lastName) => {
    const firstInitial = firstName ? firstName.charAt(0).toUpperCase() : '';
    const lastInitial = lastName ? lastName.charAt(0).toUpperCase() : '';
    return firstInitial + lastInitial || '?';
};
exports.formatInitials = formatInitials;
const truncateText = (text, maxLength, suffix = '...') => {
    if (text.length <= maxLength)
        return text;
    return text.slice(0, maxLength - suffix.length) + suffix;
};
exports.truncateText = truncateText;
const capitalizeWords = (str) => {
    return str
        .toLowerCase()
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
};
exports.capitalizeWords = capitalizeWords;
const slugify = (str) => {
    return str
        .toLowerCase()
        .trim()
        .replace(/[^\w\s-]/g, '') // Remove special characters
        .replace(/[\s_-]+/g, '-') // Replace spaces, underscores, and multiple hyphens with single hyphen
        .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens
};
exports.slugify = slugify;
// Location formatting
const formatLocation = (location) => {
    if (!location)
        return 'Location not specified';
    // Handle remote work
    if (location.toLowerCase().includes('remote')) {
        return 'Remote';
    }
    // Format city, state format
    const parts = location.split(',').map(part => part.trim());
    if (parts.length >= 2) {
        return parts.slice(0, 2).join(', ');
    }
    return location;
};
exports.formatLocation = formatLocation;
// Experience formatting
const formatExperience = (years) => {
    if (!years || years === 0)
        return 'No experience';
    if (years === 1)
        return '1 year';
    if (years < 1)
        return 'Less than 1 year';
    return `${years} years`;
};
exports.formatExperience = formatExperience;
// File size formatting
const formatFileSize = (bytes) => {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }
    return `${size.toFixed(unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`;
};
exports.formatFileSize = formatFileSize;
// Percentage formatting
const formatPercentage = (value, decimals = 1) => {
    return `${value.toFixed(decimals)}%`;
};
exports.formatPercentage = formatPercentage;
// Phone number formatting
const formatPhoneNumber = (phone) => {
    // Remove all non-digits
    const digits = phone.replace(/\D/g, '');
    // Format US phone numbers
    if (digits.length === 10) {
        return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
    }
    else if (digits.length === 11 && digits[0] === '1') {
        return `+1 (${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7)}`;
    }
    // Return original for international or invalid numbers
    return phone;
};
exports.formatPhoneNumber = formatPhoneNumber;
// Status formatting with colors/badges
const formatStatus = (status) => {
    const statusMap = {
        // Job statuses
        published: { text: 'Published', variant: 'success' },
        draft: { text: 'Draft', variant: 'secondary' },
        closed: { text: 'Closed', variant: 'danger' },
        expired: { text: 'Expired', variant: 'warning' },
        // Application statuses
        applied: { text: 'Applied', variant: 'primary' },
        screening: { text: 'Screening', variant: 'info' },
        interview: { text: 'Interview', variant: 'warning' },
        offer: { text: 'Offer', variant: 'success' },
        rejected: { text: 'Rejected', variant: 'danger' },
        withdrawn: { text: 'Withdrawn', variant: 'secondary' },
        // Job search statuses
        not_looking: { text: 'Not Looking', variant: 'secondary' },
        casually_looking: { text: 'Casually Looking', variant: 'info' },
        actively_looking: { text: 'Actively Looking', variant: 'warning' },
        open_to_offers: { text: 'Open to Offers', variant: 'success' },
    };
    return statusMap[status] || { text: (0, exports.capitalizeWords)(status.replace(/_/g, ' ')), variant: 'secondary' };
};
exports.formatStatus = formatStatus;
// URL formatting
const formatWebsiteUrl = (url) => {
    if (!url)
        return '';
    // Add protocol if missing
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        return `https://${url}`;
    }
    return url;
};
exports.formatWebsiteUrl = formatWebsiteUrl;
const extractDomain = (url) => {
    try {
        const formatted = (0, exports.formatWebsiteUrl)(url);
        const domain = new URL(formatted).hostname;
        return domain.replace(/^www\./, '');
    }
    catch {
        return url;
    }
};
exports.extractDomain = extractDomain;
// Skills formatting
const formatSkillsList = (skills, maxDisplay = 5) => {
    if (!skills || skills.length === 0)
        return 'No skills listed';
    if (skills.length <= maxDisplay) {
        return skills.join(', ');
    }
    const displayed = skills.slice(0, maxDisplay);
    const remaining = skills.length - maxDisplay;
    return `${displayed.join(', ')} +${remaining} more`;
};
exports.formatSkillsList = formatSkillsList;
// Export commonly used formatters
exports.formatters = {
    date: exports.formatDate,
    dateTime: exports.formatDateTime,
    relativeTime: exports.formatRelativeTime,
    currency: exports.formatCurrency,
    salary: exports.formatSalaryRange,
    name: exports.formatName,
    location: exports.formatLocation,
    experience: exports.formatExperience,
    fileSize: exports.formatFileSize,
    percentage: exports.formatPercentage,
    phone: exports.formatPhoneNumber,
    status: exports.formatStatus,
    truncate: exports.truncateText,
    capitalize: exports.capitalizeWords,
    slugify: exports.slugify,
    initials: exports.formatInitials,
    compactNumber: exports.formatCompactNumber
};
//# sourceMappingURL=formatting.js.map