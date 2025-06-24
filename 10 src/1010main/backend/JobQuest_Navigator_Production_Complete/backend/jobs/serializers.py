"""
Jobs app serializers for Epic 1: Job Search & Geolocation Mapping.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
from core.serializers import LocationSerializer, CompanySerializer
from .models import (
    Job, JobApplication, SavedJob, JobAlert, Skill, UserSkill, JobSkill
)

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    """Skill serializer."""
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'slug', 'category', 'description',
            'is_technical', 'popularity_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SkillCreateSerializer(serializers.ModelSerializer):
    """Skill creation serializer."""
    
    class Meta:
        model = Skill
        fields = [
            'name', 'slug', 'category', 'description', 'is_technical'
        ]
    
    def validate_name(self, value):
        """Validate skill name uniqueness."""
        if Skill.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A skill with this name already exists.")
        return value
    
    def validate_slug(self, value):
        """Validate skill slug uniqueness."""
        if Skill.objects.filter(slug=value).exists():
            raise serializers.ValidationError("A skill with this slug already exists.")
        return value


class JobSkillSerializer(serializers.ModelSerializer):
    """Job skill serializer."""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = JobSkill
        fields = [
            'skill', 'skill_id', 'is_required', 'proficiency_level'
        ]


class JobSerializer(serializers.ModelSerializer):
    """Job serializer for listing and detail views."""
    company = CompanySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    required_skills = JobSkillSerializer(many=True, read_only=True)
    is_saved = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'location', 'description',
            'requirements', 'benefits', 'salary_min', 'salary_max',
            'salary_currency', 'salary_period', 'job_type',
            'experience_level', 'remote_type', 'source', 'external_url',
            'is_active', 'posted_date', 'expires_date', 'created_at',
            'updated_at', 'required_skills', 'is_saved', 'is_applied'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'is_saved', 'is_applied'
        ]
    
    def get_is_saved(self, obj):
        """Check if job is saved by current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedJob.objects.filter(user=request.user, job=obj).exists()
        return False
    
    def get_is_applied(self, obj):
        """Check if user has applied to this job."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return JobApplication.objects.filter(user=request.user, job=obj).exists()
        return False


class JobCreateSerializer(serializers.ModelSerializer):
    """Job creation serializer."""
    company_id = serializers.UUIDField(write_only=True)
    location_id = serializers.UUIDField(write_only=True)
    skill_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Job
        fields = [
            'title', 'company_id', 'location_id', 'description',
            'requirements', 'benefits', 'salary_min', 'salary_max',
            'salary_currency', 'salary_period', 'job_type',
            'experience_level', 'remote_type', 'source', 'external_url',
            'posted_date', 'expires_date', 'skill_ids'
        ]
    
    def create(self, validated_data):
        """Create job with skills."""
        skill_ids = validated_data.pop('skill_ids', [])
        job = super().create(validated_data)
        
        # Add skills to job
        for skill_id in skill_ids:
            try:
                skill = Skill.objects.get(id=skill_id)
                JobSkill.objects.create(job=job, skill=skill)
            except Skill.DoesNotExist:
                continue
        
        return job


class JobUpdateSerializer(serializers.ModelSerializer):
    """Job update serializer."""
    skill_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'requirements', 'benefits',
            'salary_min', 'salary_max', 'salary_currency', 'salary_period',
            'job_type', 'experience_level', 'remote_type', 'external_url',
            'expires_date', 'is_active', 'skill_ids'
        ]
    
    def update(self, instance, validated_data):
        """Update job with skills."""
        skill_ids = validated_data.pop('skill_ids', None)
        job = super().update(instance, validated_data)
        
        # Update skills if provided
        if skill_ids is not None:
            # Remove existing skills
            JobSkill.objects.filter(job=job).delete()
            
            # Add new skills
            for skill_id in skill_ids:
                try:
                    skill = Skill.objects.get(id=skill_id)
                    JobSkill.objects.create(job=job, skill=skill)
                except Skill.DoesNotExist:
                    continue
        
        return job


class JobApplicationSerializer(serializers.ModelSerializer):
    """Job application serializer."""
    job = JobSerializer(read_only=True)
    job_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_id', 'status', 'applied_date',
            'last_updated', 'cover_letter', 'notes'
        ]
        read_only_fields = ['id', 'applied_date', 'last_updated']
    
    def validate_job_id(self, value):
        """Validate job exists and is active."""
        try:
            job = Job.objects.get(id=value, is_active=True)
            return value
        except Job.DoesNotExist:
            raise serializers.ValidationError("Job not found or inactive.")
    
    def validate(self, data):
        """Validate user hasn't already applied to this job."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            job_id = data.get('job_id')
            if JobApplication.objects.filter(
                user=request.user, job_id=job_id
            ).exists():
                raise serializers.ValidationError(
                    "You have already applied to this job."
                )
        return data
    
    def create(self, validated_data):
        """Create job application."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SavedJobSerializer(serializers.ModelSerializer):
    """Saved job serializer."""
    job = JobSerializer(read_only=True)
    job_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = SavedJob
        fields = [
            'id', 'job', 'job_id', 'saved_date', 'notes'
        ]
        read_only_fields = ['id', 'saved_date']
    
    def validate_job_id(self, value):
        """Validate job exists and is active."""
        try:
            job = Job.objects.get(id=value, is_active=True)
            return value
        except Job.DoesNotExist:
            raise serializers.ValidationError("Job not found or inactive.")
    
    def validate(self, data):
        """Validate user hasn't already saved this job."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            job_id = data.get('job_id')
            if SavedJob.objects.filter(
                user=request.user, job_id=job_id
            ).exists():
                raise serializers.ValidationError(
                    "You have already saved this job."
                )
        return data
    
    def create(self, validated_data):
        """Create saved job."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class JobAlertSerializer(serializers.ModelSerializer):
    """Job alert serializer."""
    location = LocationSerializer(read_only=True)
    location_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = JobAlert
        fields = [
            'id', 'name', 'keywords', 'location', 'location_id',
            'radius', 'job_type', 'experience_level', 'remote_type',
            'salary_min', 'is_active', 'email_notifications',
            'frequency', 'created_at', 'updated_at', 'last_sent'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sent']
    
    def create(self, validated_data):
        """Create job alert."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserSkillSerializer(serializers.ModelSerializer):
    """User skill serializer."""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = UserSkill
        fields = [
            'id', 'skill', 'skill_id', 'proficiency_level',
            'years_experience', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']
    
    def validate_skill_id(self, value):
        """Validate skill exists."""
        try:
            skill = Skill.objects.get(id=value)
            return value
        except Skill.DoesNotExist:
            raise serializers.ValidationError("Skill not found.")
    
    def validate(self, data):
        """Validate user doesn't already have this skill."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            skill_id = data.get('skill_id')
            if UserSkill.objects.filter(
                user=request.user, skill_id=skill_id
            ).exists():
                raise serializers.ValidationError(
                    "You already have this skill in your profile."
                )
        return data
    
    def create(self, validated_data):
        """Create user skill."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class JobSearchSerializer(serializers.Serializer):
    """Job search parameters serializer."""
    keywords = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    radius = serializers.IntegerField(required=False, min_value=1, max_value=100)
    job_type = serializers.ChoiceField(
        choices=[('', 'Any')] + Job._meta.get_field('job_type').choices,
        required=False,
        allow_blank=True
    )
    experience_level = serializers.ChoiceField(
        choices=[('', 'Any')] + Job._meta.get_field('experience_level').choices,
        required=False,
        allow_blank=True
    )
    remote_type = serializers.ChoiceField(
        choices=[('', 'Any')] + Job._meta.get_field('remote_type').choices,
        required=False,
        allow_blank=True
    )
    salary_min = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, min_value=0
    )
    salary_max = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, min_value=0
    )
    posted_since = serializers.IntegerField(
        required=False, min_value=1, max_value=365,
        help_text="Days since job was posted"
    )
    company = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    
    def validate(self, data):
        """Validate search parameters."""
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError(
                "Minimum salary cannot be greater than maximum salary."
            )
        
        return data 