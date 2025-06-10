# Microservices and Modules Used in Epic 4

## 1. Skill Gap Analysis API
- **Path:** `api/skillCertApi.ts`
- **Description:** Handles skill extraction using AI/NLP (spaCy) and maps extracted skills to recommended certifications. Calls the Python microservice for skill extraction.

## 2. Python Skill Extraction Microservice
- **Path:** `extract_skills.py`
- **Description:** Uses spaCy and a curated skill list to extract relevant skills from resume text, filtering out generic/common words for accuracy.

## 3. Skill Gap Service
- **Path:** `services/skillGapService.ts`
- **Description:** (Legacy/optional) Business logic for analyzing user skills, generating recommendations, and integrating with the API.

## 4. Test/Frontend Component
- **Path:** `test.html` (and optionally `components/RealTimeSkillTest.tsx`)
- **Description:** User interface for testing and interacting with the skill gap analysis tool.

## 5. Express Server
- **Path:** `server.ts`
- **Description:** Serves the test page and API endpoints for local development.

---
**Note:**
- All Epic 4 microservices are currently self-contained and run locally.
- No external microservices are deployed; all logic is in the above modules. 