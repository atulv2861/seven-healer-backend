# Projects API Documentation

## Overview
The Projects API provides comprehensive CRUD operations for managing healthcare projects with proper authentication and authorization.

## Base URL
```
/api/v1/projects
```

## Authentication
All admin operations (CREATE, UPDATE, DELETE) require authentication with admin privileges. Public operations (READ) don't require authentication.

### Authentication Header
```
Authorization: Bearer <access_token>
```

## API Endpoints

### 1. Create Project (Admin Only)
**POST** `/api/v1/projects/`

Creates a new project. Requires admin authentication.

#### Request Body
```json
{
  "title": "All India Institute of Medical Sciences (AIIMS), Delhi",
  "location": "New Delhi, India",
  "beds": "2000 Bedded Hospital",
  "area": "10,00,000 Sq. Mtr. (Approx.)",
  "client": "ARCOP",
  "status": "Completed",
  "description": "A state-of-the-art medical facility featuring advanced healthcare infrastructure with cutting-edge technology and patient-centric design.",
  "features": ["Emergency Services", "ICU Units", "Operation Theaters", "Diagnostic Center", "Research Labs"],
  "images": "/images/projects/AIIMS-Delhi-1.png"
}
```

#### Response (201 Created)
```json
{
  "id": "project-uuid-here",
  "title": "All India Institute of Medical Sciences (AIIMS), Delhi",
  "location": "New Delhi, India",
  "beds": "2000 Bedded Hospital",
  "area": "10,00,000 Sq. Mtr. (Approx.)",
  "client": "ARCOP",
  "status": "Completed",
  "description": "A state-of-the-art medical facility featuring advanced healthcare infrastructure with cutting-edge technology and patient-centric design.",
  "features": ["Emergency Services", "ICU Units", "Operation Theaters", "Diagnostic Center", "Research Labs"],
  "images": "/images/projects/AIIMS-Delhi-1.png",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 2. Get All Projects (Public)
**GET** `/api/v1/projects/`

Retrieves all projects with pagination and filtering options.

#### Query Parameters
- `page` (optional): Page number (default: 1, min: 1)
- `limit` (optional): Items per page (default: 10, min: 1, max: 100)
- `status` (optional): Filter by status ("Completed", "In Progress", "Planning", "On Hold")
- `client` (optional): Filter by client name (partial match)
- `search` (optional): Search in title and description

#### Example Request
```
GET /api/v1/projects/?page=1&limit=10&status=Completed&search=AIIMS
```

#### Response (200 OK)
```json
{
  "projects": [
    {
      "id": "project-uuid-here",
      "title": "All India Institute of Medical Sciences (AIIMS), Delhi",
      "location": "New Delhi, India",
      "beds": "2000 Bedded Hospital",
      "area": "10,00,000 Sq. Mtr. (Approx.)",
      "client": "ARCOP",
      "status": "Completed",
      "description": "A state-of-the-art medical facility featuring advanced healthcare infrastructure with cutting-edge technology and patient-centric design.",
      "features": ["Emergency Services", "ICU Units", "Operation Theaters", "Diagnostic Center", "Research Labs"],
      "images": "/images/projects/AIIMS-Delhi-1.png",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

### 3. Get Project by ID (Public)
**GET** `/api/v1/projects/{project_id}`

Retrieves a specific project by its ID.

#### Response (200 OK)
```json
{
  "id": "project-uuid-here",
  "title": "All India Institute of Medical Sciences (AIIMS), Delhi",
  "location": "New Delhi, India",
  "beds": "2000 Bedded Hospital",
  "area": "10,00,000 Sq. Mtr. (Approx.)",
  "client": "ARCOP",
  "status": "Completed",
  "description": "A state-of-the-art medical facility featuring advanced healthcare infrastructure with cutting-edge technology and patient-centric design.",
  "features": ["Emergency Services", "ICU Units", "Operation Theaters", "Diagnostic Center", "Research Labs"],
  "images": "/images/projects/AIIMS-Delhi-1.png",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 4. Update Project (Admin Only)
**PUT** `/api/v1/projects/{project_id}`

Updates an existing project. Requires admin authentication.

#### Request Body (All fields optional)
```json
{
  "title": "Updated Project Title",
  "status": "In Progress",
  "description": "Updated description"
}
```

#### Response (200 OK)
```json
{
  "id": "project-uuid-here",
  "title": "Updated Project Title",
  "location": "New Delhi, India",
  "beds": "2000 Bedded Hospital",
  "area": "10,00,000 Sq. Mtr. (Approx.)",
  "client": "ARCOP",
  "status": "In Progress",
  "description": "Updated description",
  "features": ["Emergency Services", "ICU Units", "Operation Theaters", "Diagnostic Center", "Research Labs"],
  "images": "/images/projects/AIIMS-Delhi-1.png",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

### 5. Delete Project (Admin Only)
**DELETE** `/api/v1/projects/{project_id}`

Deletes a project. Requires admin authentication.

#### Response (204 No Content)
No response body.

### 6. Get Project Statistics (Admin Only)
**GET** `/api/v1/projects/stats/summary`

Retrieves project statistics. Requires admin authentication.

#### Response (200 OK)
```json
{
  "total_projects": 15,
  "status_breakdown": {
    "Completed": 8,
    "In Progress": 4,
    "Planning": 2,
    "On Hold": 1
  },
  "client_breakdown": {
    "ARCOP": 3,
    "Apollo Group": 2,
    "Fortis Healthcare": 4,
    "Max Healthcare": 6
  },
  "total_clients": 4
}
```

## Data Models

### Project Schema
```json
{
  "id": "string (UUID)",
  "title": "string (max 200 chars)",
  "location": "string (max 100 chars)",
  "beds": "string (max 50 chars)",
  "area": "string (max 100 chars)",
  "client": "string (max 100 chars)",
  "status": "string (enum: Completed, In Progress, Planning, On Hold)",
  "description": "string (max 1000 chars)",
  "features": "array of strings",
  "images": "string (max 500 chars, optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid status. Must be one of: Completed, In Progress, Planning, On Hold"
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
  "detail": "Only administrators can create projects"
}
```

### 404 Not Found
```json
{
  "detail": "Project not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error creating project: <error message>"
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

### Creating a Project (Admin)
```bash
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AIIMS Delhi",
    "location": "New Delhi, India",
    "beds": "2000 Bedded Hospital",
    "area": "10,00,000 Sq. Mtr.",
    "client": "ARCOP",
    "status": "Completed",
    "description": "State-of-the-art medical facility",
    "features": ["Emergency Services", "ICU Units"],
    "images": "/images/projects/aiims-delhi.png"
  }'
```

### Getting All Projects (Public)
```bash
curl -X GET "http://localhost:8000/api/v1/projects/?page=1&limit=10"
```

### Updating a Project (Admin)
```bash
curl -X PUT "http://localhost:8000/api/v1/projects/{project_id}" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "In Progress",
    "description": "Updated description"
  }'
```

## Status Values
- `Completed`: Project is finished
- `In Progress`: Project is currently being worked on
- `Planning`: Project is in planning phase
- `On Hold`: Project is temporarily paused

## Notes
- All timestamps are in UTC format
- Project IDs are UUIDs
- Image paths should be relative to the application's static files directory
- Features are stored as an array of strings
- Pagination starts from page 1
- Search is case-insensitive and searches in both title and description
