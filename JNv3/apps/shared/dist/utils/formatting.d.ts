/**
 * Data formatting utilities for JobQuest Navigator v2
 */
import { Money, SalaryRange } from '../types/common';
export declare const formatDate: (date: string | Date, formatString?: string) => string;
export declare const formatDateTime: (date: string | Date) => string;
export declare const formatRelativeTime: (date: string | Date) => string;
export declare const formatCurrency: (amount: number, currency?: string, locale?: string) => string;
export declare const formatMoney: (money: Money, locale?: string) => string;
export declare const formatSalaryRange: (range: SalaryRange, locale?: string) => string;
export declare const formatCompactNumber: (num: number, locale?: string) => string;
export declare const formatName: (firstName?: string, lastName?: string) => string;
export declare const formatInitials: (firstName?: string, lastName?: string) => string;
export declare const truncateText: (text: string, maxLength: number, suffix?: string) => string;
export declare const capitalizeWords: (str: string) => string;
export declare const slugify: (str: string) => string;
export declare const formatLocation: (location: string) => string;
export declare const formatExperience: (years?: number) => string;
export declare const formatFileSize: (bytes: number) => string;
export declare const formatPercentage: (value: number, decimals?: number) => string;
export declare const formatPhoneNumber: (phone: string) => string;
export declare const formatStatus: (status: string) => {
    text: string;
    variant: string;
};
export declare const formatWebsiteUrl: (url: string) => string;
export declare const extractDomain: (url: string) => string;
export declare const formatSkillsList: (skills: string[], maxDisplay?: number) => string;
export declare const formatters: {
    readonly date: (date: string | Date, formatString?: string) => string;
    readonly dateTime: (date: string | Date) => string;
    readonly relativeTime: (date: string | Date) => string;
    readonly currency: (amount: number, currency?: string, locale?: string) => string;
    readonly salary: (range: SalaryRange, locale?: string) => string;
    readonly name: (firstName?: string, lastName?: string) => string;
    readonly location: (location: string) => string;
    readonly experience: (years?: number) => string;
    readonly fileSize: (bytes: number) => string;
    readonly percentage: (value: number, decimals?: number) => string;
    readonly phone: (phone: string) => string;
    readonly status: (status: string) => {
        text: string;
        variant: string;
    };
    readonly truncate: (text: string, maxLength: number, suffix?: string) => string;
    readonly capitalize: (str: string) => string;
    readonly slugify: (str: string) => string;
    readonly initials: (firstName?: string, lastName?: string) => string;
    readonly compactNumber: (num: number, locale?: string) => string;
};
//# sourceMappingURL=formatting.d.ts.map