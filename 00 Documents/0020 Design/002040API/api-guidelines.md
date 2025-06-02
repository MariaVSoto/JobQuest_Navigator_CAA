# API Design Guidelines

## 1. General Principles
- Follow RESTful design principles.
- Use clear, consistent, and meaningful resource names.
- Use HTTP methods appropriately: GET (read), POST (create), PUT/PATCH (update), DELETE (remove).

## 2. Naming Conventions
- Use plural nouns for resource names: `/users`, `/jobs`, `/applications`.
- Use lowercase letters and hyphens to separate words: `/job-applications`.
- Nest resources to show relationships: `/users/{userId}/resumes`.

## 3. Request Format
- Accept and return JSON by default: `Content-Type: application/json`.
- Use query parameters for filtering, sorting, and pagination: `/jobs?location=Toronto&sort=date&page=2`.

## 4. Response Format
- Always return a consistent JSON structure.
- Include a top-level object (not an array).
- Example:
```json
{
  "data": [ ... ],
  "meta": { "total": 100, "page": 1 },
  "errors": []
}
```

## 5. Error Handling
- Use standard HTTP status codes (200, 201, 400, 401, 403, 404, 409, 422, 500, etc.).
- Return error details in a consistent format:
```json
{
  "errors": [
    {
      "code": "RESOURCE_NOT_FOUND",
      "message": "Job not found.",
      "field": "jobId"
    }
  ]
}
```

## 6. Versioning
- Use URI versioning: `/api/v1/jobs`.
- Avoid breaking changes in the same version.

## 7. Authentication & Security
- Use HTTPS for all endpoints.
- Use token-based authentication (e.g., JWT in `Authorization: Bearer <token>` header).
- Validate all input data and sanitize outputs.

## 8. Documentation
- Document all endpoints, parameters, request/response examples, and error codes.
- Use OpenAPI/Swagger for interactive API documentation when possible.

## 9. Pagination
- Use `page` and `pageSize` (or `limit`/`offset`) for paginated endpoints.
- Include pagination metadata in responses.

## 10. Rate Limiting
- Implement rate limiting and return appropriate headers (e.g., `X-RateLimit-Remaining`).

---

> This guideline ensures all APIs are consistent, secure, and easy to use and maintain. 