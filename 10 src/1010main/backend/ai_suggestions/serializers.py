"""
AI Suggestions app serializers for Epic 3: AI-Powered Resume Optimization and Smart Recommendations.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    SuggestionTemplate, AISuggestion, SuggestionFeedback, JobRecommendation,
    ResumeJobMatch, AILearningData, SuggestionBatch
)

User = get_user_model()


class SuggestionTemplateSerializer(serializers.ModelSerializer):
    """Serializer for suggestion templates."""
    
    class Meta:
        model = SuggestionTemplate
        fields = [
            'id', 'name', 'suggestion_type', 'prompt_template', 'context_fields',
            'is_active', 'usage_count', 'success_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'success_rate', 'created_at', 'updated_at']


class AISuggestionSerializer(serializers.ModelSerializer):
    """Serializer for AI suggestions."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = AISuggestion
        fields = [
            'id', 'user', 'user_email', 'suggestion_type', 'title', 'description',
            'suggestion_content', 'ai_model', 'template', 'template_name',
            'confidence_score', 'processing_time', 'context_data', 'target_job_id',
            'target_resume_id', 'status', 'priority', 'expires_at', 'viewed_at',
            'acted_on_at', 'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_email', 'template_name', 'processing_time',
            'viewed_at', 'acted_on_at', 'is_expired', 'created_at', 'updated_at'
        ]
    
    def get_is_expired(self, obj):
        """Check if suggestion has expired."""
        return obj.is_expired()


class AISuggestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating AI suggestions."""
    
    class Meta:
        model = AISuggestion
        fields = [
            'suggestion_type', 'title', 'description', 'suggestion_content',
            'ai_model', 'template', 'confidence_score', 'context_data',
            'target_job_id', 'target_resume_id', 'priority', 'expires_at'
        ]
    
    def validate_confidence_score(self, value):
        """Validate confidence score is between 0 and 1."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Confidence score must be between 0 and 1.")
        return value
    
    def validate_suggestion_content(self, value):
        """Validate suggestion content structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Suggestion content must be a JSON object.")
        
        required_fields = ['suggestion', 'reasoning']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")
        
        return value


class SuggestionFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for suggestion feedback."""
    suggestion_title = serializers.CharField(source='suggestion.title', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = SuggestionFeedback
        fields = [
            'id', 'suggestion', 'suggestion_title', 'user', 'user_email',
            'feedback_type', 'rating', 'comments', 'accuracy_rating',
            'relevance_rating', 'usefulness_rating', 'implemented',
            'implementation_notes', 'created_at'
        ]
        read_only_fields = ['id', 'suggestion_title', 'user', 'user_email', 'created_at']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate_accuracy_rating(self, value):
        """Validate accuracy rating if provided."""
        if value is not None and not 1 <= value <= 5:
            raise serializers.ValidationError("Accuracy rating must be between 1 and 5.")
        return value
    
    def validate_relevance_rating(self, value):
        """Validate relevance rating if provided."""
        if value is not None and not 1 <= value <= 5:
            raise serializers.ValidationError("Relevance rating must be between 1 and 5.")
        return value
    
    def validate_usefulness_rating(self, value):
        """Validate usefulness rating if provided."""
        if value is not None and not 1 <= value <= 5:
            raise serializers.ValidationError("Usefulness rating must be between 1 and 5.")
        return value


class JobRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for job recommendations."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = JobRecommendation
        fields = [
            'id', 'user', 'user_email', 'job_id', 'job_title', 'company_name',
            'match_score', 'recommendation_reason', 'matching_skills',
            'missing_skills', 'ai_model', 'confidence_score', 'viewed',
            'saved', 'applied', 'dismissed', 'created_at', 'viewed_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_email', 'created_at', 'viewed_at'
        ]
    
    def validate_match_score(self, value):
        """Validate match score is between 0 and 1."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Match score must be between 0 and 1.")
        return value
    
    def validate_confidence_score(self, value):
        """Validate confidence score is between 0 and 1."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Confidence score must be between 0 and 1.")
        return value


class ResumeJobMatchSerializer(serializers.ModelSerializer):
    """Serializer for resume-job matches."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = ResumeJobMatch
        fields = [
            'id', 'user', 'user_email', 'resume_id', 'job_id',
            'overall_match_score', 'skills_match_score', 'experience_match_score',
            'keyword_match_score', 'matching_keywords', 'missing_keywords',
            'suggested_improvements', 'strength_areas', 'weakness_areas',
            'ai_model', 'analysis_summary', 'processing_time', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_email', 'processing_time', 'created_at'
        ]
    
    def validate_overall_match_score(self, value):
        """Validate overall match score is between 0 and 1."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Overall match score must be between 0 and 1.")
        return value
    
    def validate_skills_match_score(self, value):
        """Validate skills match score is between 0 and 1."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Skills match score must be between 0 and 1.")
        return value
    
    def validate_experience_match_score(self, value):
        """Validate experience match score is between 0 and 1."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Experience match score must be between 0 and 1.")
        return value
    
    def validate_keyword_match_score(self, value):
        """Validate keyword match score is between 0 and 1."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Keyword match score must be between 0 and 1.")
        return value


class SuggestionBatchSerializer(serializers.ModelSerializer):
    """Serializer for suggestion batches."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = SuggestionBatch
        fields = [
            'id', 'user', 'user_email', 'batch_type', 'status',
            'total_suggestions', 'successful_suggestions', 'failed_suggestions',
            'success_rate', 'processing_time', 'error_message', 'created_at',
            'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_email', 'total_suggestions', 'successful_suggestions',
            'failed_suggestions', 'success_rate', 'processing_time', 'error_message',
            'created_at', 'started_at', 'completed_at'
        ]
    
    def get_success_rate(self, obj):
        """Calculate success rate for the batch."""
        if obj.total_suggestions == 0:
            return 0.0
        return obj.successful_suggestions / obj.total_suggestions


class AISuggestionAnalyticsSerializer(serializers.Serializer):
    """Serializer for AI suggestions analytics."""
    total_suggestions = serializers.IntegerField()
    suggestions_by_type = serializers.DictField()
    suggestions_by_status = serializers.DictField()
    average_confidence_score = serializers.FloatField()
    average_processing_time = serializers.FloatField()
    user_engagement_rate = serializers.FloatField()
    implementation_rate = serializers.FloatField()
    recent_suggestions = AISuggestionSerializer(many=True)


class JobMatchAnalysisSerializer(serializers.Serializer):
    """Serializer for job matching analysis requests."""
    resume_id = serializers.UUIDField()
    job_id = serializers.UUIDField()
    analysis_type = serializers.ChoiceField(
        choices=[
            ('basic', 'Basic Analysis'),
            ('detailed', 'Detailed Analysis'),
            ('comprehensive', 'Comprehensive Analysis'),
        ],
        default='basic'
    )
    include_suggestions = serializers.BooleanField(default=True)


class ResumeOptimizationRequestSerializer(serializers.Serializer):
    """Serializer for resume optimization requests."""
    resume_id = serializers.UUIDField()
    target_job_id = serializers.UUIDField(required=False, allow_null=True)
    optimization_focus = serializers.MultipleChoiceField(
        choices=[
            ('keywords', 'Keywords'),
            ('formatting', 'Formatting'),
            ('content', 'Content'),
            ('skills', 'Skills'),
            ('experience', 'Experience'),
        ],
        default=['keywords', 'content']
    )
    priority = serializers.ChoiceField(
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )


class SuggestionActionSerializer(serializers.Serializer):
    """Serializer for suggestion actions (accept/reject)."""
    action = serializers.ChoiceField(
        choices=[
            ('accept', 'Accept'),
            ('reject', 'Reject'),
            ('partially_accept', 'Partially Accept'),
        ]
    )
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    implementation_details = serializers.JSONField(required=False, allow_null=True)


class BulkSuggestionActionSerializer(serializers.Serializer):
    """Serializer for bulk suggestion actions."""
    suggestion_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100
    )
    action = serializers.ChoiceField(
        choices=[
            ('accept', 'Accept All'),
            ('reject', 'Reject All'),
            ('mark_viewed', 'Mark All as Viewed'),
        ]
    )
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class SuggestionSearchSerializer(serializers.Serializer):
    """Serializer for suggestion search and filtering."""
    suggestion_type = serializers.ChoiceField(
        choices=[
            ('resume_improvement', 'Resume Improvement'),
            ('job_match', 'Job Match Recommendation'),
            ('keyword_optimization', 'Keyword Optimization'),
            ('format_suggestion', 'Format Suggestion'),
            ('content_enhancement', 'Content Enhancement'),
            ('skill_highlight', 'Skill Highlighting'),
            ('experience_optimization', 'Experience Optimization'),
        ],
        required=False
    )
    status = serializers.ChoiceField(
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('partially_accepted', 'Partially Accepted'),
            ('expired', 'Expired'),
        ],
        required=False
    )
    priority = serializers.ChoiceField(
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        required=False
    )
    confidence_min = serializers.FloatField(min_value=0.0, max_value=1.0, required=False)
    confidence_max = serializers.FloatField(min_value=0.0, max_value=1.0, required=False)
    target_job_id = serializers.UUIDField(required=False, allow_null=True)
    target_resume_id = serializers.UUIDField(required=False, allow_null=True)
    created_after = serializers.DateTimeField(required=False)
    created_before = serializers.DateTimeField(required=False)
    has_feedback = serializers.BooleanField(required=False)
    search = serializers.CharField(max_length=200, required=False)
    
    def validate(self, data):
        """Validate search parameters."""
        confidence_min = data.get('confidence_min')
        confidence_max = data.get('confidence_max')
        
        if confidence_min and confidence_max and confidence_min > confidence_max:
            raise serializers.ValidationError(
                "confidence_min cannot be greater than confidence_max"
            )
        
        created_after = data.get('created_after')
        created_before = data.get('created_before')
        
        if created_after and created_before and created_after > created_before:
            raise serializers.ValidationError(
                "created_after cannot be greater than created_before"
            )
        
        return data