# Authentication API Documentation

## Overview
This document describes the authentication system for the Seven Healer Consultancy API. The system provides user registration, login, and JWT-based authentication.

## Base URL
```
http://localhost:8000/api/v1/auth
```

## Endpoints

### 1. User Signup
**POST** `/signup`

Register a new user account.

#### Request Body
```json
{
  "first_name": "John",
  "last_name": "Doe", 
  "email": "john.doe@example.com",
  "password": "password123",
  "phone": "+1234567890",
  "role": "user"
}
```

#### Response (201 Created)
```json
{
  "id": "uuid-string",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "role": "user",
  "is_active": true
}
```

#### Validation Rules
- **Email**: Must be a valid email format
- **Phone**: Must match pattern `^\+?[\d\s\-\(\)]{10,15}$`
- **Password**: Will be hashed using bcrypt
- **Role**: Must be either "user" or "admin" (defaults to "user")

### 2. User Login
**POST** `/login`

Authenticate user and receive access token.

#### Request Body (Form Data)
```
username: john.doe@example.com
password: password123
```

#### Response (200 OK)
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-string",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "role": "user",
    "is_active": true
  }
}
```

### 3. Get Current User
**GET** `/me`

Get current user information using JWT token.

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response (200 OK)
```json
{
  "id": "uuid-string",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "role": "user",
  "is_active": true
}
```

### 4. Logout
**POST** `/logout`

Logout user (client should remove token).

#### Response (200 OK)
```json
{
  "message": "Successfully logged out"
}
```

## Superuser Access

The system includes a built-in superuser account:

- **Email**: `admin@sevenhealerconsultants.in`
- **Password**: `admin123`
- **Role**: `admin`

## Security Features

### Password Hashing
- Passwords are hashed using bcrypt with salt
- Never stored in plain text

### JWT Tokens
- Access tokens expire after 30 minutes (configurable)
- Tokens contain user email as subject
- Signed with HS256 algorithm

### Input Validation
- Email format validation
- Phone number format validation
- Required field validation
- Duplicate email prevention

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid email format"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid email or password"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error creating user: <error_message>"
}
```

## Usage Examples

### JavaScript/Fetch
```javascript
// Signup
const signupResponse = await fetch('/api/v1/auth/signup', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    first_name: 'John',
    last_name: 'Doe',
    email: 'john.doe@example.com',
    password: 'password123',
    phone: '+1234567890',
    role: 'user'
  })
});

// Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: 'username=john.doe@example.com&password=password123'
});

const { access_token } = await loginResponse.json();

// Get current user
const meResponse = await fetch('/api/v1/auth/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

### Python/Requests
```python
import requests

# Signup
signup_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "password123",
    "phone": "+1234567890",
    "role": "user"
}
response = requests.post('/api/v1/auth/signup', json=signup_data)

# Login
login_data = {
    "username": "john.doe@example.com",
    "password": "password123"
}
response = requests.post('/api/v1/auth/login', data=login_data)
token = response.json()["access_token"]

# Get current user
headers = {"Authorization": f"Bearer {token}"}
response = requests.get('/api/v1/auth/me', headers=headers)
```

## Database Schema

### Users Collection
```javascript
{
  "_id": "uuid-string",
  "first_name": "string",
  "last_name": "string", 
  "email": "string (unique)",
  "password": "string (hashed)",
  "phone": "string",
  "role": "enum (user|admin)",
  "is_active": "boolean"
}
```

## Configuration

The following environment variables can be configured:

- `JWT_SECRET_KEY`: Secret key for JWT signing
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `SUPERUSER_EMAIL`: Superuser email
- `SUPERUSER_PASSWORD`: Superuser password
- `DB_URI`: MongoDB connection string
- `DB_NAME`: Database name

