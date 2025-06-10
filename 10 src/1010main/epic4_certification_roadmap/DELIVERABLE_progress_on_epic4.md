# 🚀 Progress on Epic 4: Certification Roadmap & Skill Gap Analysis

**Sprint:** Epic 4: Certification Roadmap
**Team Member:** Ishan

---

## 1. Automation Tools Used & How They Were Applied

- **spaCy (Python NLP):**
  - Used for AI-powered skill extraction from resume text. The Python script (`extract_skills.py`) processes user input and returns a filtered, accurate list of skills.
- **Node.js/TypeScript Backend:**
  - Orchestrates the workflow, calls the Python script, and maps extracted skills to certifications using a local JSON map.
- **Git & GitHub:**
  - For version control, code review, and collaboration. All changes are committed and pushed to the `dev` branch.
- **Jira:**
  - For sprint/task management and tracking progress.
- **PowerShell/Terminal Automation:**
  - Used for running, testing, and deploying the backend and Python services.

---

## 2. Updated Project Timeline

| Date Range      | Task/Deliverable                                      | Status      |
|-----------------|-------------------------------------------------------|-------------|
| 06/01–06/07     | Initial setup, requirements, and planning             | ✅ Complete |
| 06/05–06/08     | Implemented spaCy-based skill extraction (Python)     | ✅ Complete |
| 06/08–06/12     | Hybrid integration with JSearch (real-time API)       | ⏳ In Progress |

---

## 3. Spirit Plan (5-Day Blocks)

| Spirit | Dates         | Plan/Focus Area                                      |
|--------|--------------|------------------------------------------------------|
| 1      | 06/01–06/07  | Finalize spaCy integration, remove legacy code       |
| 2      | 06/08–06/12  | Hybrid skill extraction (spaCy + JSearch API), testing, bug fixes, and final polish |

---

## 4. Relevant GitHub Branches & Pull Requests

- **Branch:** [`dev`](https://github.com/MariaVSoto/JobQuest_Navigator_CAA/tree/dev)
- **Pull Requests:**
  - [PR: Refactor Epic 4 for spaCy-based skill extraction](#) *(link to your PR if available)*
- **Deliverable Files:**
  - `README.md`, `USER_GUIDE.md`, `MICROSERVICES_USED.md`, `swagger_epic4_skillgap.yaml` (all updated)
- **Removed Legacy Files:**
  - Old APIs, services, and React components (see commit history for details)

---

## 5. Task Distribution & Coordination

- **Ishan:**
  - Led the refactor to spaCy-based extraction
  - Updated all documentation and microservice references
  - Cleaned up the codebase and removed unused files
  - Coordinated with team for hybrid integration

---

## 6. Progress Summary

- **Current:**
  - spaCy-based skill extraction and certification mapping is complete.
  - All documentation and microservice overviews are up to date.
  - Codebase is clean and ready for final enhancements (hybrid API integration in progress).

- **Next Steps:**
  - Complete hybrid approach (spaCy + JSearch real-time API) by 6/12.
  - Continue weekly progress updates and documentation.

---

*If you need to update this file, just edit and commit as needed!* 