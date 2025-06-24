from django.urls import path
from .views import ResumeSuggestionView, JobMatchSuggestionView, SuggestionFeedbackView

urlpatterns = [
    path('suggestions/resume', ResumeSuggestionView.as_view(), name='resume-suggestions'),
    path('suggestions/job-match', JobMatchSuggestionView.as_view(), name='job-match-suggestions'),
    path('suggestions/<str:suggestion_id>/feedback', SuggestionFeedbackView.as_view(), name='suggestion-feedback'),
]
