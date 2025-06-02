openapi: 3.0.3
info:
  title: JobQuest Navigator API
  description: API documentation for JobQuest Navigator, an all-in-one job search platform to discover jobs, manage resumes, and prepare for interviews.
  version: 1.0.0-alpha
  contact:
    name: Team 9 - The Zombies of CAA
    email: team9@seneca.ca
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: http://localhost:8000
    description: Local Development Server
  - url: https://api.jobquestnavigator.com
    description: Production Server (TBD)

tags:
  - name: Job Search
    description: APIs related to discovering and filtering job opportunities.

paths:
  /api/jobs:
    get:
      summary: Retrieve Job Listings
      description: Fetch job listings based on user location and filters. Supports geolocation-based job mapping as per Epic 1.
      tags:
        - Job Search
      parameters:
        - in: query
          name: latitude
          schema:
            type: number
            format: float
          required: false
          description: User's latitude for geolocation-based filtering.
        - in: query
          name: longitude
          schema:
            type: number
            format: float
          required: false
          description: User's longitude for geolocation-based filtering.
        - in: query
          name: radius
          schema:
            type: integer
            default: 50
          required: false
          description: Search radius in miles (default is 50 miles).
        - in: query
          name: keyword
          schema:
            type: string
          required: false
          description: Keyword to filter jobs by title or description.
      responses:
        '200':
          description: Successful response with a list of job listings.
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: success
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Job'
                  count:
                    type: integer
                    example: 25
        '400':
          description: Invalid request parameters (e.g., invalid latitude/longitude).
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: error
                  message:
                    type: string
                    example: Invalid latitude or longitude values.
        '500':
          description: Server error (e.g., failed to fetch data from Canada Job Bank API).
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: error
                  message:
                    type: string
                    example: Internal server error.
      security:
        - bearerAuth: []

components:
  schemas:
    Job:
      type: object
      properties:
        id:
          type: string
          example: job_12345
          description: Unique identifier for the job listing.
        title:
          type: string
          example: Software Engineer
          description: Job title.
        company:
          type: string
          example: TechCorp
          description: Company name.
        location:
          type: string
          example: Toronto, ON
          description: Job location.
        latitude:
          type: number
          format: float
          example: 43.6532
          description: Latitude of job location.
        longitude:
          type: number
          format: float
          example: -79.3832
          description: Longitude of job location.
        postingDate:
          type: string
          format: date
          example: 2023-10-15
          description: Date the job was posted.
        source:
          type: string
          example: Canada Job Bank
          description: Source of the job listing.
      required:
        - id
        - title
        - company
        - location
        - postingDate

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT token required for authenticated requests.
