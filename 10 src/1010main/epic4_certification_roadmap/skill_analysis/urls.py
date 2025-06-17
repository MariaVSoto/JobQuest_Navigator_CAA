from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/skillgap/analyze', views.analyze_skills, name='analyze_skills'),  # Updated URL
    path('api/roadmap/for-job', views.roadmap_for_job, name='roadmap_for_job'),
    path('api/jobs/search', views.search_jobs, name='search_jobs'),
]