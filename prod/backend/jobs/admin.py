"""
Jobs app admin configuration for Epic 1: Job Search & Geolocation Mapping.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Job, JobApplication, SavedJob, JobAlert, Skill, UserSkill, JobSkill
)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Skill admin configuration."""
    list_display = ['name', 'category', 'is_technical', 'popularity_score', 'created_at']
    list_filter = ['category', 'is_technical', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class JobSkillInline(admin.TabularInline):
    """Job skill inline admin."""
    model = JobSkill
    extra = 1
    # autocomplete_fields = ['skill']  # Disabled until core admin is configured


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Job admin configuration."""
    list_display = [
        'title', 'company', 'location', 'job_type', 'experience_level',
        'remote_type', 'salary_range', 'posted_date', 'is_active'
    ]
    list_filter = [
        'job_type', 'experience_level', 'remote_type', 'is_active',
        'posted_date', 'source'
    ]
    search_fields = ['title', 'company__name', 'description']
    # autocomplete_fields = ['company', 'location']  # Disabled until core admin is configured
    date_hierarchy = 'posted_date'
    ordering = ['-posted_date']
    inlines = [JobSkillInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'location', 'description')
        }),
        ('Job Details', {
            'fields': (
                'job_type', 'experience_level', 'remote_type',
                'requirements', 'benefits'
            )
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'salary_period')
        }),
        ('External Source', {
            'fields': ('source', 'external_id', 'external_url')
        }),
        ('Status & Dates', {
            'fields': ('is_active', 'posted_date', 'expires_date')
        }),
    )
    
    def salary_range(self, obj):
        """Display salary range."""
        if obj.salary_min and obj.salary_max:
            return f"{obj.salary_currency} {obj.salary_min:,.0f} - {obj.salary_max:,.0f} ({obj.salary_period})"
        elif obj.salary_min:
            return f"{obj.salary_currency} {obj.salary_min:,.0f}+ ({obj.salary_period})"
        elif obj.salary_max:
            return f"Up to {obj.salary_currency} {obj.salary_max:,.0f} ({obj.salary_period})"
        return "Not specified"
    salary_range.short_description = 'Salary Range'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """Job application admin configuration."""
    list_display = [
        'user', 'job_title', 'company', 'status', 'applied_date', 'last_updated'
    ]
    list_filter = ['status', 'applied_date', 'last_updated']
    search_fields = ['user__username', 'user__email', 'job__title', 'job__company__name']
    # autocomplete_fields = ['user', 'job']  # Disabled until core admin is configured
    date_hierarchy = 'applied_date'
    ordering = ['-applied_date']
    
    fieldsets = (
        ('Application Info', {
            'fields': ('user', 'job', 'status')
        }),
        ('Application Details', {
            'fields': ('cover_letter', 'notes')
        }),
        ('Timestamps', {
            'fields': ('applied_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['applied_date', 'last_updated']
    
    def job_title(self, obj):
        """Display job title."""
        return obj.job.title
    job_title.short_description = 'Job Title'
    
    def company(self, obj):
        """Display company name."""
        return obj.job.company.name
    company.short_description = 'Company'


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    """Saved job admin configuration."""
    list_display = ['user', 'job_title', 'company', 'saved_date']
    list_filter = ['saved_date']
    search_fields = ['user__username', 'user__email', 'job__title', 'job__company__name']
    # autocomplete_fields = ['user', 'job']  # Disabled until core admin is configured
    date_hierarchy = 'saved_date'
    ordering = ['-saved_date']
    
    def job_title(self, obj):
        """Display job title."""
        return obj.job.title
    job_title.short_description = 'Job Title'
    
    def company(self, obj):
        """Display company name."""
        return obj.job.company.name
    company.short_description = 'Company'


@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    """Job alert admin configuration."""
    list_display = [
        'user', 'name', 'location', 'job_type', 'is_active',
        'email_notifications', 'frequency', 'created_at', 'last_sent'
    ]
    list_filter = [
        'is_active', 'email_notifications', 'frequency',
        'job_type', 'experience_level', 'remote_type', 'created_at'
    ]
    search_fields = ['user__username', 'user__email', 'name', 'keywords']
    # autocomplete_fields = ['user', 'location']  # Disabled until core admin is configured
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Alert Info', {
            'fields': ('user', 'name', 'is_active')
        }),
        ('Search Criteria', {
            'fields': (
                'keywords', 'location', 'radius', 'job_type',
                'experience_level', 'remote_type', 'salary_min'
            )
        }),
        ('Notification Settings', {
            'fields': ('email_notifications', 'frequency')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_sent'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    """User skill admin configuration."""
    list_display = [
        'user', 'skill', 'proficiency_level', 'years_experience',
        'is_verified', 'created_at'
    ]
    list_filter = [
        'proficiency_level', 'is_verified', 'skill__category',
        'skill__is_technical', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'skill__name'
    ]
    # autocomplete_fields = ['user', 'skill']  # Disabled until core admin is configured
    date_hierarchy = 'created_at'
    ordering = ['user', 'skill__name']
    
    fieldsets = (
        ('Skill Info', {
            'fields': ('user', 'skill', 'proficiency_level')
        }),
        ('Experience', {
            'fields': ('years_experience', 'is_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


# Register JobSkill for direct editing if needed
@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    """Job skill admin configuration."""
    list_display = ['job', 'skill', 'is_required', 'proficiency_level']
    list_filter = ['is_required', 'proficiency_level', 'skill__category']
    search_fields = ['job__title', 'skill__name']
    # autocomplete_fields = ['job', 'skill']  # Disabled until core admin is configured
    ordering = ['job__title', 'skill__name']
