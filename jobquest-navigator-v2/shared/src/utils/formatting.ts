/**
 * Data formatting utilities for JobQuest Navigator v2
 */

import { format, formatDistance, parseISO, isValid } from 'date-fns';
import { Money, SalaryRange } from '../types/common';

// Date formatting utilities
export const formatDate = (date: string | Date, formatString = 'MMM d, yyyy'): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(dateObj)) return 'Invalid date';
    return format(dateObj, formatString);
  } catch {
    return 'Invalid date';
  }
};

export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, 'MMM d, yyyy h:mm a');
};

export const formatRelativeTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(dateObj)) return 'Unknown';
    return formatDistance(dateObj, new Date(), { addSuffix: true });
  } catch {
    return 'Unknown';
  }
};

// Currency and salary formatting
export const formatCurrency = (
  amount: number, 
  currency = 'USD', 
  locale = 'en-US'
): string => {
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  } catch {
    return `${currency} ${amount.toLocaleString()}`;
  }
};

export const formatMoney = (money: Money, locale = 'en-US'): string => {
  return formatCurrency(money.amount, money.currency, locale);
};

export const formatSalaryRange = (range: SalaryRange, locale = 'en-US'): string => {
  const { min, max, period } = range;
  
  let result = '';
  
  if (min && max) {
    result = `${formatMoney(min, locale)} - ${formatMoney(max, locale)}`;
  } else if (min) {
    result = `${formatMoney(min, locale)}+`;
  } else if (max) {
    result = `Up to ${formatMoney(max, locale)}`;
  } else {
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

// Compact number formatting (e.g., 1.2K, 5.6M)
export const formatCompactNumber = (num: number, locale = 'en-US'): string => {
  try {
    return new Intl.NumberFormat(locale, {
      notation: 'compact',
      compactDisplay: 'short',
    }).format(num);
  } catch {
    // Fallback for older browsers
    if (num >= 1e9) {
      return (num / 1e9).toFixed(1) + 'B';
    } else if (num >= 1e6) {
      return (num / 1e6).toFixed(1) + 'M';
    } else if (num >= 1e3) {
      return (num / 1e3).toFixed(1) + 'K';
    } else {
      return num.toString();
    }
  }
};

// String formatting utilities
export const formatName = (firstName?: string, lastName?: string): string => {
  if (firstName && lastName) {
    return `${firstName} ${lastName}`;
  } else if (firstName) {
    return firstName;
  } else if (lastName) {
    return lastName;
  } else {
    return 'Unknown User';
  }
};

export const formatInitials = (firstName?: string, lastName?: string): string => {
  const firstInitial = firstName ? firstName.charAt(0).toUpperCase() : '';
  const lastInitial = lastName ? lastName.charAt(0).toUpperCase() : '';
  return firstInitial + lastInitial || '?';
};

export const truncateText = (text: string, maxLength: number, suffix = '...'): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - suffix.length) + suffix;
};

export const capitalizeWords = (str: string): string => {
  return str
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

export const slugify = (str: string): string => {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/[\s_-]+/g, '-') // Replace spaces, underscores, and multiple hyphens with single hyphen
    .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens
};

// Location formatting
export const formatLocation = (location: string): string => {
  if (!location) return 'Location not specified';
  
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

// Experience formatting
export const formatExperience = (years?: number): string => {
  if (!years || years === 0) return 'No experience';
  if (years === 1) return '1 year';
  if (years < 1) return 'Less than 1 year';
  return `${years} years`;
};

// File size formatting
export const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`;
};

// Percentage formatting
export const formatPercentage = (value: number, decimals = 1): string => {
  return `${value.toFixed(decimals)}%`;
};

// Phone number formatting
export const formatPhoneNumber = (phone: string): string => {
  // Remove all non-digits
  const digits = phone.replace(/\D/g, '');
  
  // Format US phone numbers
  if (digits.length === 10) {
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
  } else if (digits.length === 11 && digits[0] === '1') {
    return `+1 (${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7)}`;
  }
  
  // Return original for international or invalid numbers
  return phone;
};

// Status formatting with colors/badges
export const formatStatus = (status: string): { text: string; variant: string } => {
  const statusMap: Record<string, { text: string; variant: string }> = {
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
  
  return statusMap[status] || { text: capitalizeWords(status.replace(/_/g, ' ')), variant: 'secondary' };
};

// URL formatting
export const formatWebsiteUrl = (url: string): string => {
  if (!url) return '';
  
  // Add protocol if missing
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return `https://${url}`;
  }
  
  return url;
};

export const extractDomain = (url: string): string => {
  try {
    const formatted = formatWebsiteUrl(url);
    const domain = new URL(formatted).hostname;
    return domain.replace(/^www\./, '');
  } catch {
    return url;
  }
};

// Skills formatting
export const formatSkillsList = (skills: string[], maxDisplay = 5): string => {
  if (!skills || skills.length === 0) return 'No skills listed';
  
  if (skills.length <= maxDisplay) {
    return skills.join(', ');
  }
  
  const displayed = skills.slice(0, maxDisplay);
  const remaining = skills.length - maxDisplay;
  return `${displayed.join(', ')} +${remaining} more`;
};

// Export commonly used formatters
export const formatters = {
  date: formatDate,
  dateTime: formatDateTime,
  relativeTime: formatRelativeTime,
  currency: formatCurrency,
  salary: formatSalaryRange,
  name: formatName,
  location: formatLocation,
  experience: formatExperience,
  fileSize: formatFileSize,
  percentage: formatPercentage,
  phone: formatPhoneNumber,
  status: formatStatus,
  truncate: truncateText,
  capitalize: capitalizeWords,
  slugify,
  initials: formatInitials,
  compactNumber: formatCompactNumber
} as const;