"""
Models for Epic 6: Company Research & Interview Preparation.
Manages company research, interview preparation materials, and user progress.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from core.models import Company, BaseModel

User = get_user_model()


class CompanyResearch(BaseModel):
    """
    Stores comprehensive research data for a specific company.
    Includes company insights, culture analysis, and preparation materials.
    """
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='research_reports'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='company_research'
    )
    title = models.CharField(max_length=255)
    
    # Research content
    overview = models.TextField(help_text="Company overview and key information")
    culture_analysis = models.TextField(help_text="Company culture and work environment analysis")
    recent_news = models.TextField(blank=True, help_text="Recent company news and updates")
    financial_highlights = models.TextField(blank=True, help_text="Financial performance and highlights")
    growth_prospects = models.TextField(blank=True, help_text="Growth opportunities and future outlook")
    
    # Metadata
    research_date = models.DateTimeField(auto_now_add=True)
    is_saved = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence in research accuracy (0-1)")
    
    class Meta:
        unique_together = ['company', 'user']
        ordering = ['-research_date']

    def __str__(self):
        return f"Research: {self.company.name} by {self.user.email}"


class InterviewPreparation(BaseModel):
    """
    Stores interview preparation materials for a specific company/position.
    """
    company_research = models.ForeignKey(
        CompanyResearch, 
        on_delete=models.CASCADE, 
        related_name='interview_prep'
    )
    position_title = models.CharField(max_length=255, blank=True)
    
    # Preparation content
    key_talking_points = models.TextField(help_text="Important points to discuss")
    company_specific_prep = models.TextField(help_text="Company-specific preparation notes")
    technical_focus_areas = models.TextField(blank=True, help_text="Technical areas to focus on")
    behavioral_scenarios = models.TextField(blank=True, help_text="Behavioral interview scenarios")
    
    # Progress tracking
    preparation_status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        default='not_started'
    )
    last_reviewed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Interview Prep: {self.company_research.company.name}"


class InterviewQuestion(BaseModel):
    """
    Stores interview questions categorized by type and difficulty.
    """
    QUESTION_TYPES = [
        ('general', 'General'),
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral'),
        ('company_specific', 'Company-Specific'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')
    
    # Optional context
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='interview_questions'
    )
    position_type = models.CharField(max_length=100, blank=True)
    
    # Answer guidance
    sample_answer = models.TextField(blank=True, help_text="Sample answer or guidance")
    answer_framework = models.TextField(blank=True, help_text="Framework for answering (e.g., STAR method)")
    
    # Usage tracking
    times_used = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['question_type', 'difficulty', 'question_text']

    def __str__(self):
        return f"{self.get_question_type_display()} - {self.question_text[:50]}..."


class PracticeSession(BaseModel):
    """
    Tracks interview practice sessions and performance.
    """
    SESSION_TYPES = [
        ('mock_interview', 'Mock Interview'),
        ('question_practice', 'Question Practice'),
        ('company_prep', 'Company-Specific Prep'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    company = models.ForeignKey(
        Company, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='practice_sessions'
    )
    
    # Session details
    duration_minutes = models.PositiveIntegerField(default=0)
    questions_attempted = models.PositiveIntegerField(default=0)
    completion_status = models.CharField(
        max_length=20,
        choices=[
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('abandoned', 'Abandoned'),
        ],
        default='in_progress'
    )
    
    # Performance tracking
    self_rating = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="User self-rating (1-5)"
    )
    notes = models.TextField(blank=True, help_text="Session notes and reflections")
    areas_for_improvement = models.TextField(blank=True)
    
    # Session data
    session_data = models.JSONField(
        default=dict, 
        help_text="Detailed session data (questions, answers, timings)"
    )
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_session_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"


class CompanyInsight(BaseModel):
    """
    Stores specific insights about companies (culture, interview process, etc.).
    """
    INSIGHT_TYPES = [
        ('culture', 'Company Culture'),
        ('interview_process', 'Interview Process'),
        ('compensation', 'Compensation & Benefits'),
        ('work_life_balance', 'Work-Life Balance'),
        ('growth_opportunities', 'Growth Opportunities'),
        ('team_dynamics', 'Team Dynamics'),
    ]
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='insights'
    )
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    # Source and credibility
    source = models.CharField(max_length=255, blank=True, help_text="Source of the insight")
    credibility_score = models.FloatField(default=0.5, help_text="Credibility score (0-1)")
    
    # User interaction
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company.name} - {self.get_insight_type_display()}"


class SavedResearch(BaseModel):
    """
    Tracks user's saved research items for quick access.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_research')
    company_research = models.ForeignKey(
        CompanyResearch, 
        on_delete=models.CASCADE, 
        related_name='saves'
    )
    
    # Organization
    notes = models.TextField(blank=True, help_text="Personal notes about this research")
    tags = models.JSONField(default=list, help_text="User-defined tags for organization")
    
    class Meta:
        unique_together = ['user', 'company_research']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} saved {self.company_research.company.name}"


class CompanyNews(BaseModel):
    """
    Stores recent news and updates about companies.
    """
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='news_articles'
    )
    title = models.CharField(max_length=255)
    summary = models.TextField()
    url = models.URLField(blank=True)
    
    # Metadata
    published_date = models.DateTimeField()
    source = models.CharField(max_length=255)
    relevance_score = models.FloatField(default=0.0, help_text="Relevance for job seekers (0-1)")
    
    # Categories
    categories = models.JSONField(
        default=list, 
        help_text="News categories (e.g., hiring, funding, product launches)"
    )
    
    class Meta:
        ordering = ['-published_date']
        unique_together = ['company', 'url']

    def __str__(self):
        return f"{self.company.name} - {self.title}"
