from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    ResumeTemplate, Resume, ResumeVersion, ResumeSkillMatch,
    ResumeShare, ResumeComment, ResumeExport
)


class ResumeTemplateSerializer(serializers.ModelSerializer):
    """Serializer for resume templates"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = ResumeTemplate
        fields = [
            'id', 'name', 'category', 'category_display', 'description',
            'template_data', 'preview_image', 'is_premium', 'is_active',
            'usage_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']


class ResumeSkillMatchSerializer(serializers.ModelSerializer):
    """Serializer for resume skill matches"""
    proficiency_display = serializers.CharField(source='get_proficiency_level_display', read_only=True)
    
    class Meta:
        model = ResumeSkillMatch
        fields = [
            'id', 'skill_name', 'skill_category', 'relevance_score',
            'is_primary_skill', 'years_of_experience', 'proficiency_level',
            'proficiency_display', 'found_in_section', 'context_snippet',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ResumeVersionSerializer(serializers.ModelSerializer):
    """Serializer for resume versions"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ResumeVersion
        fields = [
            'id', 'version_number', 'title', 'resume_data',
            'change_summary', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'version_number', 'created_at']


class ResumeCommentSerializer(serializers.ModelSerializer):
    """Serializer for resume comments"""
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = ResumeComment
        fields = [
            'id', 'author_email', 'author_name', 'section', 'content',
            'is_resolved', 'parent_comment', 'replies', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.parent_comment is None:
            replies = obj.resumecomment_set.all()
            return ResumeCommentSerializer(replies, many=True, context=self.context).data
        return []


class ResumeShareSerializer(serializers.ModelSerializer):
    """Serializer for resume sharing"""
    shared_by_name = serializers.CharField(source='shared_by.get_full_name', read_only=True)
    permission_display = serializers.CharField(source='get_permission_level_display', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = ResumeShare
        fields = [
            'id', 'shared_by', 'shared_by_name', 'shared_with_email',
            'permission_level', 'permission_display', 'is_active',
            'expires_at', 'is_expired', 'share_token', 'access_count',
            'last_accessed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'shared_by', 'share_token', 'access_count',
            'last_accessed_at', 'created_at'
        ]
    
    def get_is_expired(self, obj):
        if obj.expires_at:
            from django.utils import timezone
            return timezone.now() > obj.expires_at
        return False


class ResumeExportSerializer(serializers.ModelSerializer):
    """Serializer for resume exports"""
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ResumeExport
        fields = [
            'id', 'format', 'format_display', 'file_path', 'file_size',
            'file_size_mb', 'download_count', 'include_photo',
            'include_references', 'custom_styling', 'created_at',
            'last_downloaded_at'
        ]
        read_only_fields = [
            'id', 'file_path', 'file_size', 'download_count',
            'created_at', 'last_downloaded_at'
        ]
    
    def get_file_size_mb(self, obj):
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None


class ResumeSerializer(serializers.ModelSerializer):
    """Main resume serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    skill_matches = ResumeSkillMatchSerializer(many=True, read_only=True)
    versions_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    shares_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Resume
        fields = [
            'id', 'user', 'user_name', 'title', 'template', 'template_name',
            'status', 'status_display', 'is_default', 'full_name', 'email',
            'phone', 'location', 'website', 'linkedin_url', 'github_url',
            'professional_summary', 'resume_data', 'target_role',
            'target_industry', 'keywords', 'view_count', 'download_count',
            'last_modified_section', 'skill_matches', 'versions_count',
            'comments_count', 'shares_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'view_count', 'download_count', 'created_at', 'updated_at'
        ]
    
    def get_versions_count(self, obj):
        return obj.versions.count()
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_shares_count(self, obj):
        return obj.shares.filter(is_active=True).count()
    
    def validate(self, data):
        # Ensure required personal information is provided
        required_fields = ['full_name', 'email']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field} is required")
        return data


class ResumeDetailSerializer(ResumeSerializer):
    """Detailed resume serializer with related data"""
    versions = ResumeVersionSerializer(many=True, read_only=True)
    comments = ResumeCommentSerializer(many=True, read_only=True)
    shares = ResumeShareSerializer(many=True, read_only=True)
    exports = ResumeExportSerializer(many=True, read_only=True)
    
    class Meta(ResumeSerializer.Meta):
        fields = ResumeSerializer.Meta.fields + ['versions', 'comments', 'shares', 'exports']


class ResumeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new resumes"""
    
    class Meta:
        model = Resume
        fields = [
            'title', 'template', 'full_name', 'email', 'phone', 'location',
            'website', 'linkedin_url', 'github_url', 'professional_summary',
            'resume_data', 'target_role', 'target_industry', 'keywords'
        ]
    
    def validate(self, data):
        # Ensure required fields are provided
        required_fields = ['title', 'full_name', 'email']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field} is required")
        return data
    
    def create(self, validated_data):
        # Set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ResumeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating resumes"""
    
    class Meta:
        model = Resume
        fields = [
            'title', 'template', 'status', 'is_default', 'full_name', 'email',
            'phone', 'location', 'website', 'linkedin_url', 'github_url',
            'professional_summary', 'resume_data', 'target_role',
            'target_industry', 'keywords', 'last_modified_section'
        ]
    
    def update(self, instance, validated_data):
        # Create a new version if significant changes are made
        significant_fields = ['resume_data', 'professional_summary', 'target_role']
        if any(field in validated_data for field in significant_fields):
            self._create_version(instance, validated_data)
        
        return super().update(instance, validated_data)
    
    def _create_version(self, instance, validated_data):
        """Create a new version when significant changes are made"""
        latest_version = instance.versions.first()
        new_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        ResumeVersion.objects.create(
            resume=instance,
            version_number=new_version_number,
            title=instance.title,
            resume_data=instance.resume_data,
            change_summary=f"Updated {', '.join(validated_data.keys())}",
            created_by=self.context['request'].user
        )


class ResumeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for resume lists"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    versions_count = serializers.SerializerMethodField()
    last_version_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Resume
        fields = [
            'id', 'title', 'template_name', 'status', 'status_display',
            'is_default', 'target_role', 'target_industry', 'view_count',
            'download_count', 'versions_count', 'last_version_date',
            'created_at', 'updated_at'
        ]
    
    def get_versions_count(self, obj):
        return obj.versions.count()
    
    def get_last_version_date(self, obj):
        latest_version = obj.versions.first()
        return latest_version.created_at if latest_version else obj.updated_at


class ResumeCloneSerializer(serializers.Serializer):
    """Serializer for cloning resumes"""
    title = serializers.CharField(max_length=200)
    copy_versions = serializers.BooleanField(default=False)
    copy_comments = serializers.BooleanField(default=False)
    
    def validate_title(self, value):
        user = self.context['request'].user
        if Resume.objects.filter(user=user, title=value).exists():
            raise serializers.ValidationError("A resume with this title already exists")
        return value 