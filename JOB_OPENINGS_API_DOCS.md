# Job Openings API Documentation

## Overview
The Job Openings API provides comprehensive CRUD operations for managing job postings with proper authentication and authorization. It supports complex job structures with categorized responsibilities and detailed job information.

## Base URL
```
/api/v1/jobs
```

## Authentication
All admin operations (CREATE, UPDATE, DELETE) require authentication with admin privileges. Public operations (READ) don't require authentication.

### Authentication Header
```
Authorization: Bearer <access_token>
```

## API Endpoints

### 1. Create Job Opening (Admin Only)
**POST** `/api/v1/jobs/`

Creates a new job opening. Requires admin authentication.

#### Request Body
```json
{
  "job_id": "JD-0028",
  "title": "Assistant Manager – Marketing",
  "company": "SHCP",
  "location": "Seven Healer Counsultancy Pvt.Ltd",
  "type": "Full Time",
  "posted_date": "Posted 3 weeks ago",
  "description": "We are looking for a dynamic and strategic Marketing Manager to lead the development and execution of integrated marketing initiatives for our upcoming state-of-the-art hospital.",
  "overview": "We are looking for a dynamic and strategic Marketing Manager to lead the development and execution of integrated marketing initiatives for our upcoming state-of-the-art hospital. The ideal candidate will play a pivotal role in building the hospital's brand presence, driving patient engagement, and ensuring alignment between marketing goals and overall business objectives.",
  "key_responsibilities": [
    {
      "category": "Marketing Strategy & Execution",
      "items": [
        "Assist in developing and implementing marketing plans to promote hospital services and enhance brand visibility.",
        "Support execution of campaigns across digital, print, outdoor, and other platforms.",
        "Coordinate marketing activities in line with hospital milestones, service launches, and special initiatives."
      ]
    },
    {
      "category": "Digital & Social Media Marketing",
      "items": [
        "Manage day-to-day content updates and engagement across social media channels.",
        "Coordinate website updates, SEO/SEM activities, and email marketing campaigns."
      ]
    }
  ],
  "qualifications": [
    "MBA/PGDM in Marketing, Communications, or related field.",
    "6-8 years of experience in healthcare or service industry marketing.",
    "Knowledge of digital marketing, brand promotion, and public relations."
  ],
  "remuneration": "As per industry standards",
  "why_join_us": "At Sant Nirankari Health City, we offer a collaborative and supportive work environment where your contributions are valued and recognized.",
  "requirements": [],
  "responsibilities": [],
  "is_active": "Active"
}
```

#### Response (201 Created)
```json
{
  "id": "job-uuid-here",
  "job_id": "JD-0028",
  "title": "Assistant Manager – Marketing",
  "company": "SHCP",
  "location": "Seven Healer Counsultancy Pvt.Ltd",
  "type": "Full Time",
  "posted_date": "Posted 3 weeks ago",
  "description": "We are looking for a dynamic and strategic Marketing Manager...",
  "overview": "We are looking for a dynamic and strategic Marketing Manager...",
  "key_responsibilities": [
    {
      "category": "Marketing Strategy & Execution",
      "items": [
        "Assist in developing and implementing marketing plans...",
        "Support execution of campaigns across digital, print, outdoor, and other platforms."
      ]
    }
  ],
  "qualifications": [
    "MBA/PGDM in Marketing, Communications, or related field.",
    "6-8 years of experience in healthcare or service industry marketing."
  ],
  "remuneration": "As per industry standards",
  "why_join_us": "At Sant Nirankari Health City, we offer a collaborative and supportive work environment...",
  "requirements": [],
  "responsibilities": [],
  "is_active": "Active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 2. Get All Job Openings (Public)
**GET** `/api/v1/jobs/`

Retrieves all job openings with pagination and filtering options.

#### Query Parameters
- `page` (optional): Page number (default: 1, min: 1)
- `limit` (optional): Items per page (default: 10, min: 1, max: 100)
- `status` (optional): Filter by status ("Active", "Inactive", "Closed", "Draft")
- `job_type` (optional): Filter by job type ("Full Time", "Part Time", "Contract", "Internship", "Freelance")
- `company` (optional): Filter by company name (partial match)
- `search` (optional): Search in title, description, and overview
- `active_only` (optional): Show only active jobs (default: true)

#### Example Request
```
GET /api/v1/jobs/?page=1&limit=10&job_type=Full Time&search=Marketing
```

#### Response (200 OK)
```json
{
  "job_openings": [
    {
      "id": "job-uuid-here",
      "job_id": "JD-0028",
      "title": "Assistant Manager – Marketing",
      "company": "SHCP",
      "location": "Seven Healer Counsultancy Pvt.Ltd",
      "type": "Full Time",
      "posted_date": "Posted 3 weeks ago",
      "description": "We are looking for a dynamic and strategic Marketing Manager...",
      "overview": "We are looking for a dynamic and strategic Marketing Manager...",
      "key_responsibilities": [...],
      "qualifications": [...],
      "remuneration": "As per industry standards",
      "why_join_us": "At Sant Nirankari Health City, we offer a collaborative...",
      "requirements": [],
      "responsibilities": [],
      "is_active": "Active",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

### 3. Get Job Opening by ID (Public)
**GET** `/api/v1/jobs/{job_id}`

Retrieves a specific job opening by its job_id.

#### Response (200 OK)
```json
{
  "id": "job-uuid-here",
  "job_id": "JD-0028",
  "title": "Assistant Manager – Marketing",
  "company": "SHCP",
  "location": "Seven Healer Counsultancy Pvt.Ltd",
  "type": "Full Time",
  "posted_date": "Posted 3 weeks ago",
  "description": "We are looking for a dynamic and strategic Marketing Manager...",
  "overview": "We are looking for a dynamic and strategic Marketing Manager...",
  "key_responsibilities": [...],
  "qualifications": [...],
  "remuneration": "As per industry standards",
  "why_join_us": "At Sant Nirankari Health City, we offer a collaborative...",
  "requirements": [],
  "responsibilities": [],
  "is_active": "Active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 4. Update Job Opening (Admin Only)
**PUT** `/api/v1/jobs/{job_id}`

Updates an existing job opening. Requires admin authentication.

#### Request Body (All fields optional)
```json
{
  "title": "Updated Job Title",
  "status": "Inactive",
  "description": "Updated description"
}
```

#### Response (200 OK)
```json
{
  "id": "job-uuid-here",
  "job_id": "JD-0028",
  "title": "Updated Job Title",
  "company": "SHCP",
  "location": "Seven Healer Counsultancy Pvt.Ltd",
  "type": "Full Time",
  "posted_date": "Posted 3 weeks ago",
  "description": "Updated description",
  "overview": "We are looking for a dynamic and strategic Marketing Manager...",
  "key_responsibilities": [...],
  "qualifications": [...],
  "remuneration": "As per industry standards",
  "why_join_us": "At Sant Nirankari Health City, we offer a collaborative...",
  "requirements": [],
  "responsibilities": [],
  "is_active": "Inactive",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

### 5. Delete Job Opening (Admin Only)
**DELETE** `/api/v1/jobs/{job_id}`

Deletes a job opening. Requires admin authentication.

#### Response (204 No Content)
No response body.

### 6. Update Job Status (Admin Only)
**PATCH** `/api/v1/jobs/{job_id}/status`

Updates the status of a job opening. Requires admin authentication.

#### Query Parameters
- `new_status`: New status for the job ("Active", "Inactive", "Closed", "Draft")

#### Response (200 OK)
```json
{
  "id": "job-uuid-here",
  "job_id": "JD-0028",
  "title": "Assistant Manager – Marketing",
  "company": "SHCP",
  "location": "Seven Healer Counsultancy Pvt.Ltd",
  "type": "Full Time",
  "posted_date": "Posted 3 weeks ago",
  "description": "We are looking for a dynamic and strategic Marketing Manager...",
  "overview": "We are looking for a dynamic and strategic Marketing Manager...",
  "key_responsibilities": [...],
  "qualifications": [...],
  "remuneration": "As per industry standards",
  "why_join_us": "At Sant Nirankari Health City, we offer a collaborative...",
  "requirements": [],
  "responsibilities": [],
  "is_active": "Closed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

### 7. Get Job Opening Statistics (Admin Only)
**GET** `/api/v1/jobs/stats/summary`

Retrieves job opening statistics. Requires admin authentication.

#### Response (200 OK)
```json
{
  "total_jobs": 25,
  "active_jobs": 15,
  "inactive_jobs": 5,
  "closed_jobs": 3,
  "draft_jobs": 2,
  "type_breakdown": {
    "Full Time": 20,
    "Part Time": 3,
    "Contract": 2,
    "Internship": 0,
    "Freelance": 0
  },
  "company_breakdown": {
    "SHCP": 10,
    "Seven Healer": 8,
    "Health City": 7
  }
}
```

### 8. Advanced Search (Public)
**GET** `/api/v1/jobs/search/advanced`

Advanced search for job openings with multiple filters.

#### Query Parameters
- `title` (optional): Search in job title
- `company` (optional): Search in company name
- `location` (optional): Search in location
- `job_type` (optional): Filter by job type
- `status` (optional): Filter by status (default: "Active")
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)

#### Example Request
```
GET /api/v1/jobs/search/advanced?title=Marketing&company=SHCP&job_type=Full Time&status=Active
```

#### Response (200 OK)
```json
{
  "job_openings": [...],
  "total": 5,
  "page": 1,
  "limit": 10
}
```

## Data Models

### Job Opening Schema
```json
{
  "id": "string (UUID)",
  "job_id": "string (max 20 chars, unique)",
  "title": "string (max 200 chars)",
  "company": "string (max 100 chars)",
  "location": "string (max 200 chars)",
  "type": "string (enum: Full Time, Part Time, Contract, Internship, Freelance)",
  "posted_date": "string (max 100 chars)",
  "description": "string (max 2000 chars)",
  "overview": "string (max 3000 chars)",
  "key_responsibilities": [
    {
      "category": "string (max 200 chars)",
      "items": ["array of strings"]
    }
  ],
  "qualifications": ["array of strings"],
  "remuneration": "string (max 200 chars)",
  "why_join_us": "string (max 2000 chars)",
  "requirements": ["array of strings"],
  "responsibilities": ["array of strings"],
  "is_active": "string (enum: Active, Inactive, Closed, Draft)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid job type. Must be one of: Full Time, Part Time, Contract, Internship, Freelance"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Only administrators can create job openings"
}
```

### 404 Not Found
```json
{
  "detail": "Job opening not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error creating job opening: <error message>"
}
```

## Authentication Flow

1. **Login** to get access token:
   ```
   POST /api/v1/auth/login
   ```

2. **Use token** in Authorization header:
   ```
   Authorization: Bearer <access_token>
   ```

3. **Admin operations** require admin role or superuser privileges.

## Example Usage

### Creating a Job Opening (Admin)
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "JD-0028",
    "title": "Assistant Manager – Marketing",
    "company": "SHCP",
    "location": "Seven Healer Counsultancy Pvt.Ltd",
    "type": "Full Time",
    "posted_date": "Posted 3 weeks ago",
    "description": "We are looking for a dynamic and strategic Marketing Manager...",
    "overview": "We are looking for a dynamic and strategic Marketing Manager...",
    "key_responsibilities": [
      {
        "category": "Marketing Strategy & Execution",
        "items": [
          "Assist in developing and implementing marketing plans...",
          "Support execution of campaigns across digital, print, outdoor, and other platforms."
        ]
      }
    ],
    "qualifications": [
      "MBA/PGDM in Marketing, Communications, or related field.",
      "6-8 years of experience in healthcare or service industry marketing."
    ],
    "remuneration": "As per industry standards",
    "why_join_us": "At Sant Nirankari Health City, we offer a collaborative...",
    "requirements": [],
    "responsibilities": [],
    "is_active": "Active"
  }'
```

### Getting All Job Openings (Public)
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/?page=1&limit=10&active_only=true"
```

### Updating a Job Opening (Admin)
```bash
curl -X PUT "http://localhost:8000/api/v1/jobs/JD-0028" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": "Closed",
    "description": "Updated job description"
  }'
```

### Advanced Search (Public)
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/search/advanced?title=Marketing&company=SHCP&job_type=Full Time"
```

## Job Types
- `Full Time`: Full-time employment
- `Part Time`: Part-time employment
- `Contract`: Contract-based work
- `Internship`: Internship positions
- `Freelance`: Freelance work

## Job Statuses
- `Active`: Job is currently open for applications
- `Inactive`: Job is temporarily not accepting applications
- `Closed`: Job is no longer accepting applications
- `Draft`: Job is being prepared and not yet published

## Notes
- All timestamps are in UTC format
- Job IDs are unique identifiers (e.g., JD-0028)
- Key responsibilities are organized by categories for better structure
- Pagination starts from page 1
- Search is case-insensitive and searches in title, description, and overview
- Advanced search allows multiple filters to be combined
- Job status can be updated independently using the PATCH endpoint
