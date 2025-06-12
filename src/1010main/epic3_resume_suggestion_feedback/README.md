# Epic 3: Resume Suggestion Feedback Service

This epic implements the AI Suggestion Service for JobQuest Navigator, providing AI-driven resume suggestions, job matches, and feedback collection. The service is built with Django and integrates with MySQL, S3, and the OpenAI API, following the microservices architecture described in the project’s Architecture Decision document.

## Folder Structure

```
epic3_resume_suggestion_feedback/
├── README.md
├── ARCHITECTURE.md
├── USER_GUIDE.md
├── ai_suggestion_service/      # Django project root
│   ├── manage.py
│   ├── ai_suggestion/         # Django app
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       └── openai_service.py
│   ├── ai_suggestion_service/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── requirements.txt
├── tests/
│   └── test_suggestions.py
```

## Deliverables

- **Documentation**: 
  - `ARCHITECTURE.md` (with diagrams)
  - `README.md` (overview, setup)
  - `USER_GUIDE.md` (how to use the service)
- **Django Code**: 
  - Django project and app for the AI Suggestion Service
  - API endpoints for suggestions and feedback
- **Tests**: 
  - Unit and integration tests in the `tests/` folder

## References

- See `00 Documents/0099 Final Documents/Architecture Decision/Detailed Microservices Architecture design.md` for the overall system design.
