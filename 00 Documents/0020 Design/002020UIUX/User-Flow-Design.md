# User Flow Design

This document illustrates the main user flows for JobQuest Navigator, based on the user stories and personas (Emily and Michael) described in the PRD.

## 1. Emily: Recent Graduate – Job Discovery and Application Flow

### Description
Emily wants to find her first job in a new city, discover nearby opportunities, tailor her resume, and apply efficiently.

```mermaid
flowchart TD
    A[Login / Sign Up] --> B[View Dashboard]
    B --> C[Access Job Map]
    C --> D[Allow Geolocation Access]
    D --> E[View Jobs on Map]
    E --> F[Click Job Pin for Details]
    F --> G[View Job Details]
    G --> H[Get AI Resume Suggestions]
    H --> I[Select/Modify Resume Version]
    I --> J[Apply for Job]
    J --> K[Track Application Status]
    K --> L[Receive Notifications]
    L --> M[Access Interview Prep Module]
    M --> N[Practice Interview Questions]
```

### Key Steps
- User logs in or signs up.
- Navigates to the dashboard and accesses the job map.
- Grants geolocation permission to see nearby jobs.
- Clicks on job pins to view details.
- Uses AI to get resume suggestions and selects the best version.
- Applies for the job and tracks application status.
- Receives notifications and prepares for interviews.

---

## 2. Michael: Mid-career Professional – Certification and Application Management Flow

### Description
Michael wants to upskill, manage multiple job applications, and track certifications.

```mermaid
flowchart TD
    A1[Login / Sign Up] --> B1[View Dashboard]
    B1 --> C1[Access Certification Roadmap]
    C1 --> D1[View Skill Gap Analysis]
    D1 --> E1[Get Certification Recommendations]
    E1 --> F1[Add Certifications to Roadmap]
    F1 --> G1[Mark Certifications as Completed]
    B1 --> H1[Manage Resume Versions]
    H1 --> I1[Edit/Select Resume for Application]
    B1 --> J1[View Job Map or List]
    J1 --> K1[Apply for Job]
    K1 --> L1[Track All Applications]
    L1 --> M1[Receive Application Updates]
```

### Key Steps
- User logs in or signs up.
- Views dashboard and accesses the certification roadmap.
- Reviews skill gap analysis and receives certification recommendations.
- Adds certifications to the roadmap and marks them as completed.
- Manages multiple resume versions for different applications.
- Applies for jobs and tracks all applications.
- Receives updates and notifications.

---

## Notes
- All flows assume the user can navigate back to the dashboard at any time.
- Error handling, onboarding, and help/support flows are not shown but should be considered in UI design.
