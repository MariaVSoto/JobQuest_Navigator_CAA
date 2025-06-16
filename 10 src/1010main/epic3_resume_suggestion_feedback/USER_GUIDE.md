# User Guide: AI Suggestion Service (Epic 3)

This guide explains how to set up, run, and use the AI Suggestion Service for JobQuest Navigator.

---

## 1. Overview

The AI Suggestion Service provides:
- AI-powered resume improvement suggestions
- Job match recommendations
- Feedback collection on suggestions

---

## 2. Prerequisites

- Python 3.9+
- Django 4.x
- MySQL database
- AWS S3 bucket (for resume storage, via Resume Management Service)
- OpenAI API key
- Valid JWT token (authentication via Auth Service)

---

## 3. Setup & Run

1. **Clone the repository and navigate to the service folder:**
   ```bash
   cd src/1010main/epic3_resume_suggestion_feedback/ai_suggestion_service
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - `OPENAI_API_KEY`
   - `DATABASE_URL` (MySQL)
   - `S3_BUCKET` (if needed)
   - `DJANGO_SECRET_KEY`
   - `ALLOWED_HOSTS`
   - `AUTH_SERVICE_URL`

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

---

## 4. API Usage Examples

All endpoints require a valid JWT token in the `Authorization` header.

### a) Generate Resume Suggestions

```bash
curl -X POST http://localhost:8000/api/v1/suggestions/resume \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"resume_id": "abc123"}'
```

### b) Get Suggestions for a Resume

```bash
curl -X GET http://localhost:8000/api/v1/users/<user_id>/resumes/<resume_id>/suggestions \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### c) Submit Feedback on a Suggestion

```bash
curl -X POST http://localhost:8000/api/v1/suggestions/<suggestion_id>/feedback \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"feedback": "Very helpful!"}'
```

---

## 5. Testing

1. **Run unit tests:**
   ```bash
   python -m unittest discover ../tests
   ```

2. **Check API with Postman or curl using the above examples.**

---

## 6. References

- See `ARCHITECTURE.md` for service design.
- See `README.md` for folder structure and deliverables.
- See `00 Documents/0099 Final Documents/Architecture Decision/Detailed Microservices Architecture design.md` for overall system architecture.

---
