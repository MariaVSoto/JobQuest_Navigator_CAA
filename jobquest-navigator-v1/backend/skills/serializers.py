"""
Skills app serializers for Epic 4: Skills Analysis and Certification Roadmaps.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    SkillCategory, Skill, UserSkill, Certification, UserCertification,
    LearningPath, UserLearningPath, SkillAssessment, UserSkillAssessment
)

User = get_user_model()


class SkillCategorySerializer(serializers.ModelSerializer):
    """Serializer for skill categories."""
    subcategories = serializers.SerializerMethodField()
    skill_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SkillCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'parent_category', 'is_active', 'subcategories', 'skill_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'subcategories', 'skill_count']
    
    def get_subcategories(self, obj):
        """Get subcategories for this category."""
        subcategories = obj.subcategories.filter(is_active=True)
        return SkillCategorySerializer(subcategories, many=True, context=self.context).data
    
    def get_skill_count(self, obj):
        """Count of skills in this category."""
        return obj.skills.count()


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for skills."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_proficiency = serializers.SerializerMethodField()
    is_user_skill = serializers.SerializerMethodField()
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'slug', 'category', 'category_name', 'description',
            'aliases', 'market_demand', 'average_salary', 'growth_rate',
            'learning_time_hours', 'difficulty_level', 'is_trending',
            'is_technical', 'popularity_score', 'usage_count',
            'user_proficiency', 'is_user_skill', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'usage_count', 'user_proficiency', 'is_user_skill',
            'created_at', 'updated_at'
        ]
    
    def get_user_proficiency(self, obj):
        """Get current user's proficiency level for this skill."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_skill = UserSkill.objects.filter(user=request.user, skill=obj).first()
            if user_skill:
                return user_skill.proficiency_level
        return None
    
    def get_is_user_skill(self, obj):
        """Check if current user has this skill."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserSkill.objects.filter(user=request.user, skill=obj).exists()
        return False


class SkillCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating skills."""
    
    class Meta:
        model = Skill
        fields = [
            'name', 'slug', 'category', 'description', 'aliases',
            'market_demand', 'average_salary', 'growth_rate',
            'learning_time_hours', 'difficulty_level', 'is_trending',
            'is_technical'
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


class UserSkillSerializer(serializers.ModelSerializer):
    """Serializer for user skills."""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.UUIDField(write_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = [
            'id', 'skill', 'skill_id', 'skill_name', 'proficiency_level',
            'years_experience', 'self_assessed_level', 'is_verified',
            'verification_source', 'evidence_url', 'learning_progress',
            'target_proficiency', 'last_used', 'frequency_of_use',
            'source', 'confidence_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'skill', 'skill_name', 'created_at', 'updated_at']
    
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
            if self.instance is None:  # Creating new skill
                if UserSkill.objects.filter(user=request.user, skill_id=skill_id).exists():
                    raise serializers.ValidationError(
                        "You already have this skill in your profile."
                    )
        return data
    
    def create(self, validated_data):
        """Create user skill."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserSkillUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user skills."""
    
    class Meta:
        model = UserSkill
        fields = [
            'proficiency_level', 'years_experience', 'self_assessed_level',
            'verification_source', 'evidence_url', 'learning_progress',
            'target_proficiency', 'last_used', 'frequency_of_use'
        ]


class CertificationSerializer(serializers.ModelSerializer):
    """Serializer for certifications."""
    skill_categories = SkillCategorySerializer(many=True, read_only=True)
    related_skills = SkillSerializer(many=True, read_only=True)
    user_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Certification
        fields = [
            'id', 'name', 'issuing_organization', 'description',
            'skill_categories', 'related_skills', 'difficulty_level',
            'prerequisites', 'exam_format', 'exam_duration_hours',
            'is_lifetime', 'validity_years', 'cost_usd', 'preparation_time_hours',
            'pass_rate', 'salary_boost_percentage', 'market_demand',
            'official_url', 'study_guide_url', 'practice_exam_url',
            'is_active', 'popularity_score', 'user_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'popularity_score', 'user_status', 'created_at', 'updated_at'
        ]
    
    def get_user_status(self, obj):
        """Get current user's status for this certification."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_cert = UserCertification.objects.filter(
                user=request.user, certification=obj
            ).first()
            if user_cert:
                return {
                    'status': user_cert.status,
                    'earned_date': user_cert.earned_date,
                    'expiry_date': user_cert.expiry_date,
                    'study_progress': user_cert.study_progress
                }
        return None


class UserCertificationSerializer(serializers.ModelSerializer):
    """Serializer for user certifications."""
    certification = CertificationSerializer(read_only=True)
    certification_id = serializers.UUIDField(write_only=True)
    certification_name = serializers.CharField(source='certification.name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = UserCertification
        fields = [
            'id', 'certification', 'certification_id', 'certification_name',
            'status', 'earned_date', 'expiry_date', 'credential_id',
            'credential_url', 'verification_url', 'is_verified',
            'study_progress', 'target_completion_date', 'exam_score',
            'attempt_number', 'cost_paid', 'study_hours', 'notes',
            'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'certification', 'certification_name', 'is_expired',
            'created_at', 'updated_at'
        ]
    
    def get_is_expired(self, obj):
        """Check if certification is expired."""
        return obj.is_expired()
    
    def validate_certification_id(self, value):
        """Validate certification exists."""
        try:
            certification = Certification.objects.get(id=value, is_active=True)
            return value
        except Certification.DoesNotExist:
            raise serializers.ValidationError("Certification not found or inactive.")
    
    def validate(self, data):
        """Validate user doesn't already have this certification."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            certification_id = data.get('certification_id')
            if self.instance is None:  # Creating new certification
                if UserCertification.objects.filter(
                    user=request.user, certification_id=certification_id
                ).exists():
                    raise serializers.ValidationError(
                        "You already have this certification in your profile."
                    )
        return data
    
    def create(self, validated_data):
        """Create user certification."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LearningPathSerializer(serializers.ModelSerializer):
    """Serializer for learning paths."""
    target_skills = SkillSerializer(many=True, read_only=True)
    recommended_certifications = CertificationSerializer(many=True, read_only=True)
    prerequisite_skills = SkillSerializer(many=True, read_only=True)
    user_progress = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'name', 'description', 'target_role', 'target_skills',
            'recommended_certifications', 'difficulty_level',
            'estimated_duration_weeks', 'hours_per_week', 'prerequisite_skills',
            'career_outcomes', 'salary_range_min', 'salary_range_max',
            'learning_resources', 'milestones', 'is_active', 'is_featured',
            'popularity_score', 'success_rate', 'user_progress', 'is_enrolled',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'popularity_score', 'success_rate', 'user_progress',
            'is_enrolled', 'created_at', 'updated_at'
        ]
    
    def get_user_progress(self, obj):
        """Get current user's progress in this learning path."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_path = UserLearningPath.objects.filter(
                user=request.user, learning_path=obj
            ).first()
            if user_path:
                return {
                    'status': user_path.status,
                    'progress_percentage': user_path.progress_percentage,
                    'current_milestone': user_path.current_milestone,
                    'total_study_hours': user_path.total_study_hours
                }
        return None
    
    def get_is_enrolled(self, obj):
        """Check if current user is enrolled in this learning path."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserLearningPath.objects.filter(
                user=request.user, learning_path=obj
            ).exists()
        return False


class UserLearningPathSerializer(serializers.ModelSerializer):
    """Serializer for user learning paths."""
    learning_path = LearningPathSerializer(read_only=True)
    learning_path_id = serializers.UUIDField(write_only=True)
    learning_path_name = serializers.CharField(source='learning_path.name', read_only=True)
    skills_acquired = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserLearningPath
        fields = [
            'id', 'learning_path', 'learning_path_id', 'learning_path_name',
            'status', 'progress_percentage', 'current_milestone',
            'started_date', 'target_completion_date', 'completed_date',
            'estimated_hours_remaining', 'total_study_hours',
            'last_activity_date', 'weekly_hours_goal', 'skills_acquired',
            'difficulty_rating', 'satisfaction_rating', 'feedback_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'learning_path', 'learning_path_name', 'progress_percentage',
            'estimated_hours_remaining', 'last_activity_date', 'skills_acquired',
            'created_at', 'updated_at'
        ]
    
    def validate_learning_path_id(self, value):
        """Validate learning path exists."""
        try:
            learning_path = LearningPath.objects.get(id=value, is_active=True)
            return value
        except LearningPath.DoesNotExist:
            raise serializers.ValidationError("Learning path not found or inactive.")
    
    def validate(self, data):
        """Validate user isn't already enrolled in this learning path."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            learning_path_id = data.get('learning_path_id')
            if self.instance is None:  # Creating new enrollment
                if UserLearningPath.objects.filter(
                    user=request.user, learning_path_id=learning_path_id
                ).exists():
                    raise serializers.ValidationError(
                        "You are already enrolled in this learning path."
                    )
        return data
    
    def create(self, validated_data):
        """Create user learning path enrollment."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SkillAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for skill assessments."""
    skill = SkillSerializer(read_only=True)
    user_attempts = serializers.SerializerMethodField()
    best_score = serializers.SerializerMethodField()
    
    class Meta:
        model = SkillAssessment
        fields = [
            'id', 'skill', 'name', 'description', 'assessment_type',
            'difficulty_level', 'time_limit_minutes', 'max_score',
            'passing_score', 'is_active', 'is_certified',
            'user_attempts', 'best_score', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_attempts', 'best_score', 'created_at', 'updated_at'
        ]
    
    def get_user_attempts(self, obj):
        """Get current user's attempts for this assessment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserSkillAssessment.objects.filter(
                user=request.user, assessment=obj
            ).count()
        return 0
    
    def get_best_score(self, obj):
        """Get current user's best score for this assessment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            best_attempt = UserSkillAssessment.objects.filter(
                user=request.user, assessment=obj, completed_at__isnull=False
            ).order_by('-score').first()
            if best_attempt:
                return {
                    'score': best_attempt.score,
                    'percentage': best_attempt.percentage,
                    'passed': best_attempt.passed
                }
        return None


class UserSkillAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for user skill assessments."""
    assessment = SkillAssessmentSerializer(read_only=True)
    assessment_id = serializers.UUIDField(write_only=True)
    assessment_name = serializers.CharField(source='assessment.name', read_only=True)
    
    class Meta:
        model = UserSkillAssessment
        fields = [
            'id', 'assessment', 'assessment_id', 'assessment_name',
            'attempt_number', 'started_at', 'completed_at', 'score',
            'percentage', 'passed', 'time_taken_minutes', 'answers',
            'detailed_results', 'recommended_proficiency', 'improvement_areas',
            'created_at'
        ]
        read_only_fields = [
            'id', 'assessment', 'assessment_name', 'attempt_number',
            'started_at', 'percentage', 'passed', 'recommended_proficiency',
            'improvement_areas', 'created_at'
        ]
    
    def validate_assessment_id(self, value):
        """Validate assessment exists."""
        try:
            assessment = SkillAssessment.objects.get(id=value, is_active=True)
            return value
        except SkillAssessment.DoesNotExist:
            raise serializers.ValidationError("Assessment not found or inactive.")
    
    def create(self, validated_data):
        """Create user skill assessment attempt."""
        validated_data['user'] = self.context['request'].user
        
        # Calculate attempt number
        assessment_id = validated_data.get('assessment_id')
        last_attempt = UserSkillAssessment.objects.filter(
            user=validated_data['user'], assessment_id=assessment_id
        ).order_by('-attempt_number').first()
        
        if last_attempt:
            validated_data['attempt_number'] = last_attempt.attempt_number + 1
        else:
            validated_data['attempt_number'] = 1
        
        return super().create(validated_data)


# Specialized serializers for specific use cases
class SkillSearchSerializer(serializers.Serializer):
    """Serializer for skill search parameters."""
    category = serializers.UUIDField(required=False)
    market_demand = serializers.ChoiceField(
        choices=['very_low', 'low', 'moderate', 'high', 'very_high'],
        required=False
    )
    difficulty_level = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced', 'expert'],
        required=False
    )
    is_trending = serializers.BooleanField(required=False)
    is_technical = serializers.BooleanField(required=False)
    search = serializers.CharField(max_length=200, required=False)
    min_salary = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, min_value=0
    )
    max_salary = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, min_value=0
    )
    
    def validate(self, data):
        """Validate search parameters."""
        min_salary = data.get('min_salary')
        max_salary = data.get('max_salary')
        
        if min_salary and max_salary and min_salary > max_salary:
            raise serializers.ValidationError(
                "Minimum salary cannot be greater than maximum salary."
            )
        
        return data


class SkillGapAnalysisSerializer(serializers.Serializer):
    """Serializer for skill gap analysis results."""
    target_role = serializers.CharField(max_length=100)
    user_skills = UserSkillSerializer(many=True, read_only=True)
    required_skills = SkillSerializer(many=True, read_only=True)
    missing_skills = SkillSerializer(many=True, read_only=True)
    skill_gaps = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
    recommended_learning_paths = LearningPathSerializer(many=True, read_only=True)
    recommended_certifications = CertificationSerializer(many=True, read_only=True)
    overall_readiness_score = serializers.FloatField(read_only=True)


class SkillTrendSerializer(serializers.Serializer):
    """Serializer for skill trends data."""
    skill = SkillSerializer(read_only=True)
    trend_direction = serializers.CharField(read_only=True)
    growth_percentage = serializers.FloatField(read_only=True)
    demand_change = serializers.CharField(read_only=True)
    salary_change = serializers.FloatField(read_only=True)
    period = serializers.CharField(read_only=True)


class SkillRecommendationSerializer(serializers.Serializer):
    """Serializer for skill recommendations."""
    skill = SkillSerializer(read_only=True)
    recommendation_reason = serializers.CharField(read_only=True)
    relevance_score = serializers.FloatField(read_only=True)
    priority = serializers.CharField(read_only=True)
    learning_time_estimate = serializers.IntegerField(read_only=True)
    career_impact = serializers.CharField(read_only=True)


class LearningProgressSerializer(serializers.Serializer):
    """Serializer for learning progress updates."""
    hours_studied = serializers.IntegerField(min_value=0, max_value=24)
    milestone_completed = serializers.IntegerField(required=False, min_value=0)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    difficulty_rating = serializers.IntegerField(
        required=False, min_value=1, max_value=5
    )


class SkillExtractionSerializer(serializers.Serializer):
    """Serializer for skill extraction requests."""
    text = serializers.CharField()
    extraction_type = serializers.ChoiceField(
        choices=[
            ('resume', 'Resume'),
            ('job_description', 'Job Description'),
            ('course_description', 'Course Description'),
        ]
    )
    confidence_threshold = serializers.FloatField(
        min_value=0.0, max_value=1.0, default=0.7
    )


class SkillExtractionResultSerializer(serializers.Serializer):
    """Serializer for skill extraction results."""
    extracted_skills = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
    confidence_scores = serializers.DictField(read_only=True)
    processing_time = serializers.FloatField(read_only=True)
    suggestions = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )


class CertificationPlanSerializer(serializers.Serializer):
    """Serializer for certification planning."""
    target_role = serializers.CharField(max_length=100)
    timeline_months = serializers.IntegerField(min_value=1, max_value=60)
    budget_usd = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, min_value=0
    )
    current_skills = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    preferred_difficulty = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced', 'expert'],
        required=False
    )


class CertificationPlanResultSerializer(serializers.Serializer):
    """Serializer for certification plan results."""
    recommended_certifications = CertificationSerializer(many=True, read_only=True)
    learning_timeline = serializers.ListField(
        child=serializers.DictField(),
        read_only=True
    )
    total_cost = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    total_study_hours = serializers.IntegerField(read_only=True)
    expected_outcomes = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )
    prerequisites_analysis = serializers.DictField(read_only=True)