"""
Serializers for Epic 6: Company Research & Interview Preparation.
Handles API serialization for all company research related models.
"""

from rest_framework import serializers
from core.serializers import CompanySerializer
from .models import (
    CompanyResearch, InterviewPreparation, InterviewQuestion,
    PracticeSession, CompanyInsight, SavedResearch, CompanyNews
)


class CompanyResearchSerializer(serializers.ModelSerializer):
    """Serializer for CompanyResearch model."""
    company = CompanySerializer(read_only=True)
    company_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = CompanyResearch
        fields = [
            'id', 'company', 'company_id', 'user', 'title',
            'overview', 'culture_analysis', 'recent_news',
            'financial_highlights', 'growth_prospects',
            'research_date', 'is_saved', 'confidence_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'research_date', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class InterviewPreparationSerializer(serializers.ModelSerializer):
    """Serializer for InterviewPreparation model."""
    company_name = serializers.CharField(source='company_research.company.name', read_only=True)
    
    class Meta:
        model = InterviewPreparation
        fields = [
            'id', 'company_research', 'company_name', 'position_title',
            'key_talking_points', 'company_specific_prep',
            'technical_focus_areas', 'behavioral_scenarios',
            'preparation_status', 'last_reviewed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InterviewQuestionSerializer(serializers.ModelSerializer):
    """Serializer for InterviewQuestion model."""
    company = CompanySerializer(read_only=True)
    company_id = serializers.UUIDField(write_only=True, required=False)
    question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    
    class Meta:
        model = InterviewQuestion
        fields = [
            'id', 'question_text', 'question_type', 'question_type_display',
            'difficulty', 'difficulty_display', 'company', 'company_id',
            'position_type', 'sample_answer', 'answer_framework',
            'times_used', 'average_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'times_used', 'average_rating', 'created_at', 'updated_at']


class PracticeSessionSerializer(serializers.ModelSerializer):
    """Serializer for PracticeSession model."""
    company = CompanySerializer(read_only=True)
    company_id = serializers.UUIDField(write_only=True, required=False)
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    completion_status_display = serializers.CharField(source='get_completion_status_display', read_only=True)
    
    class Meta:
        model = PracticeSession
        fields = [
            'id', 'user', 'session_type', 'session_type_display',
            'company', 'company_id', 'duration_minutes', 'questions_attempted',
            'completion_status', 'completion_status_display', 'self_rating',
            'notes', 'areas_for_improvement', 'session_data',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CompanyInsightSerializer(serializers.ModelSerializer):
    """Serializer for CompanyInsight model."""
    company = CompanySerializer(read_only=True)
    company_id = serializers.UUIDField(write_only=True)
    insight_type_display = serializers.CharField(source='get_insight_type_display', read_only=True)
    net_votes = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanyInsight
        fields = [
            'id', 'company', 'company_id', 'insight_type', 'insight_type_display',
            'title', 'content', 'source', 'credibility_score',
            'upvotes', 'downvotes', 'net_votes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'upvotes', 'downvotes', 'created_at', 'updated_at']

    def get_net_votes(self, obj):
        return obj.upvotes - obj.downvotes


class SavedResearchSerializer(serializers.ModelSerializer):
    """Serializer for SavedResearch model."""
    company_research = CompanyResearchSerializer(read_only=True)
    company_research_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = SavedResearch
        fields = [
            'id', 'user', 'company_research', 'company_research_id',
            'notes', 'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CompanyNewsSerializer(serializers.ModelSerializer):
    """Serializer for CompanyNews model."""
    company = CompanySerializer(read_only=True)
    company_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = CompanyNews
        fields = [
            'id', 'company', 'company_id', 'title', 'summary', 'url',
            'published_date', 'source', 'relevance_score', 'categories',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanyResearchSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing company research."""
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.URLField(source='company.logo_url', read_only=True)
    
    class Meta:
        model = CompanyResearch
        fields = [
            'id', 'company_name', 'company_logo', 'title',
            'research_date', 'is_saved', 'confidence_score'
        ]


class InterviewQuestionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing interview questions."""
    question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = InterviewQuestion
        fields = [
            'id', 'question_text', 'question_type', 'question_type_display',
            'difficulty', 'difficulty_display', 'company_name',
            'position_type', 'times_used', 'average_rating'
        ]