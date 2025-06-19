from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import (
    ResumeTemplate, Resume, ResumeVersion, ResumeSkillMatch,
    ResumeShare, ResumeComment, ResumeExport
)


@admin.register(ResumeTemplate)
class ResumeTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'is_premium', 'is_active', 
        'usage_count', 'created_at'
    ]
    list_filter = ['category', 'is_premium', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Template Data', {
            'fields': ('template_data', 'preview_image')
        }),
        ('Settings', {
            'fields': ('is_premium', 'is_active')
        }),
        ('Statistics', {
            'fields': ('usage_count',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


class ResumeVersionInline(admin.TabularInline):
    model = ResumeVersion
    extra = 0
    readonly_fields = ['version_number', 'created_by', 'created_at']
    fields = ['version_number', 'title', 'change_summary', 'created_by', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


class ResumeSkillMatchInline(admin.TabularInline):
    model = ResumeSkillMatch
    extra = 0
    readonly_fields = ['created_at']
    fields = [
        'skill_name', 'skill_category', 'relevance_score', 
        'is_primary_skill', 'proficiency_level'
    ]


class ResumeShareInline(admin.TabularInline):
    model = ResumeShare
    extra = 0
    readonly_fields = ['share_token', 'access_count', 'last_accessed_at', 'created_at']
    fields = [
        'shared_with_email', 'permission_level', 'is_active', 
        'expires_at', 'access_count'
    ]


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'status', 'is_default', 'target_role',
        'view_count', 'download_count', 'versions_count', 'updated_at'
    ]
    list_filter = [
        'status', 'is_default', 'target_industry', 'template__category',
        'created_at', 'updated_at'
    ]
    search_fields = [
        'title', 'user__username', 'user__email', 'full_name',
        'professional_summary', 'target_role', 'keywords'
    ]
    readonly_fields = [
        'id', 'view_count', 'download_count', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'template', 'status', 'is_default')
        }),
        ('Personal Details', {
            'fields': (
                'full_name', 'email', 'phone', 'location',
                'website', 'linkedin_url', 'github_url'
            )
        }),
        ('Professional Information', {
            'fields': ('professional_summary', 'target_role', 'target_industry', 'keywords')
        }),
        ('Resume Data', {
            'fields': ('resume_data',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'download_count', 'last_modified_section'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [ResumeVersionInline, ResumeSkillMatchInline, ResumeShareInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'template'
        ).prefetch_related('versions')
    
    def versions_count(self, obj):
        return obj.versions.count()
    versions_count.short_description = 'Versions'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new resume
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = [
        'resume_title', 'version_number', 'title', 
        'created_by', 'created_at'
    ]
    list_filter = ['created_at', 'resume__status']
    search_fields = [
        'resume__title', 'title', 'change_summary',
        'created_by__username'
    ]
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Version Information', {
            'fields': ('resume', 'version_number', 'title', 'change_summary')
        }),
        ('Resume Data', {
            'fields': ('resume_data',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'resume', 'created_by'
        )
    
    def resume_title(self, obj):
        return obj.resume.title
    resume_title.short_description = 'Resume'
    resume_title.admin_order_field = 'resume__title'


@admin.register(ResumeSkillMatch)
class ResumeSkillMatchAdmin(admin.ModelAdmin):
    list_display = [
        'skill_name', 'resume_title', 'skill_category',
        'relevance_score', 'is_primary_skill', 'proficiency_level'
    ]
    list_filter = [
        'skill_category', 'is_primary_skill', 'proficiency_level',
        'resume__status', 'created_at'
    ]
    search_fields = [
        'skill_name', 'resume__title', 'context_snippet'
    ]
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Skill Information', {
            'fields': ('resume', 'skill_name', 'skill_category')
        }),
        ('Match Details', {
            'fields': (
                'relevance_score', 'is_primary_skill', 
                'years_of_experience', 'proficiency_level'
            )
        }),
        ('Context', {
            'fields': ('found_in_section', 'context_snippet'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('resume')
    
    def resume_title(self, obj):
        return obj.resume.title
    resume_title.short_description = 'Resume'
    resume_title.admin_order_field = 'resume__title'


@admin.register(ResumeShare)
class ResumeShareAdmin(admin.ModelAdmin):
    list_display = [
        'resume_title', 'shared_with_email', 'permission_level',
        'is_active', 'access_count', 'expires_at', 'created_at'
    ]
    list_filter = [
        'permission_level', 'is_active', 'expires_at', 'created_at'
    ]
    search_fields = [
        'resume__title', 'shared_with_email', 'shared_by__username'
    ]
    readonly_fields = [
        'id', 'share_token', 'access_count', 
        'last_accessed_at', 'created_at'
    ]
    
    fieldsets = (
        ('Share Information', {
            'fields': (
                'resume', 'shared_by', 'shared_with_email', 
                'permission_level'
            )
        }),
        ('Settings', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Access Tracking', {
            'fields': ('share_token', 'access_count', 'last_accessed_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'resume', 'shared_by'
        )
    
    def resume_title(self, obj):
        return obj.resume.title
    resume_title.short_description = 'Resume'
    resume_title.admin_order_field = 'resume__title'


@admin.register(ResumeComment)
class ResumeCommentAdmin(admin.ModelAdmin):
    list_display = [
        'resume_title', 'author_email', 'section',
        'is_resolved', 'created_at'
    ]
    list_filter = ['is_resolved', 'section', 'created_at']
    search_fields = [
        'resume__title', 'author_email', 'author_name', 'content'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': (
                'resume', 'author_email', 'author_name', 
                'section', 'parent_comment'
            )
        }),
        ('Content', {
            'fields': ('content', 'is_resolved')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('resume')
    
    def resume_title(self, obj):
        return obj.resume.title
    resume_title.short_description = 'Resume'
    resume_title.admin_order_field = 'resume__title'


@admin.register(ResumeExport)
class ResumeExportAdmin(admin.ModelAdmin):
    list_display = [
        'resume_title', 'format', 'file_size_mb',
        'download_count', 'created_at', 'last_downloaded_at'
    ]
    list_filter = ['format', 'created_at', 'last_downloaded_at']
    search_fields = ['resume__title', 'file_path']
    readonly_fields = [
        'id', 'file_path', 'file_size', 'download_count',
        'created_at', 'last_downloaded_at'
    ]
    
    fieldsets = (
        ('Export Information', {
            'fields': ('resume', 'format')
        }),
        ('Export Settings', {
            'fields': (
                'include_photo', 'include_references', 'custom_styling'
            )
        }),
        ('File Details', {
            'fields': ('file_path', 'file_size', 'download_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'last_downloaded_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('resume')
    
    def resume_title(self, obj):
        return obj.resume.title
    resume_title.short_description = 'Resume'
    resume_title.admin_order_field = 'resume__title'
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{obj.file_size / (1024 * 1024):.2f} MB"
        return "N/A"
    file_size_mb.short_description = 'File Size'
