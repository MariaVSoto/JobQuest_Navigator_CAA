from django.urls import path
from .views import (
    ResumeUploadView, ResumeListView, ResumeDetailView,
    ResumeVersionListView, FileDownloadView, FileDeleteView
)

urlpatterns = [
    path('v1/resumes/', ResumeUploadView.as_view(), name='resume-upload'),
    path('v1/resumes/', ResumeListView.as_view(), name='resume-list'),
    path('v1/resumes/<uuid:resume_id>/', ResumeDetailView.as_view(), name='resume-detail'),
    path('v1/resumes/<uuid:resume_id>/versions/', ResumeVersionListView.as_view(), name='resume-version-list'),
    path('v1/files/<uuid:file_id>/', FileDownloadView.as_view(), name='file-download'),
    path('v1/files/<uuid:file_id>/delete/', FileDeleteView.as_view(), name='file-delete'),
]
