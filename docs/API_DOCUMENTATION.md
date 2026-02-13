# Face Attendance System API Documentation

## Base URL
```
http://localhost:8000
```

## Overview
The Face Attendance System provides RESTful APIs for managing student attendance with face recognition capabilities.

## Authentication
Currently, the API does not require authentication. This may be added in future versions.

## API Endpoints

### 1. Face Detection & Ingestion

#### POST /api/v1/ingest
Receive face detection data from the face detection system.

**Request Body:**
```json
{
  "timestamp": "2026-01-26T12:00:00.000Z",
  "camera_id": "cam01",
  "total_faces": 3,
  "known_faces": [
    {"name": "Alice", "confidence": 0.92},
    {"name": "Bob", "confidence": 0.88}
  ],
  "unknown_faces": 1,
  "stream_image": "base64-encoded-jpeg-or-null"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### 2. Attendance Management

#### POST /api/v1/attendance/check
Check in all currently detected faces.

**Response:**
```json
{
  "status": "success",
  "saved_count": 2,
  "already_checked": [],
  "names": ["Alice", "Bob"]
}
```

#### GET /api/v1/attendance/report
Generate attendance report with filters.

**Query Parameters:**
- `session_id` (optional): Filter by session ID
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `student_id` (optional): Filter by student ID

**Response:**
```json
{
  "report": [
    {
      "id": 1,
      "session_id": 1,
      "student_id": 1,
      "timestamp": "2026-01-26T12:00:00.000Z",
      "check_in_type": "face",
      "confidence_score": 0.92,
      "camera_id": "cam01",
      "student_name": "Alice",
      "student_number": "STU2026001",
      "email": "alice@example.com",
      "session_name": "Math Class",
      "course_id": "MATH101"
    }
  ]
}
```

#### GET /api/v1/attendance/export
Export attendance data as CSV file.

**Query Parameters:**
- `session_id` (optional): Filter by session ID
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)

**Response:** CSV file download

#### GET /api/v1/attendance/history
Legacy endpoint for attendance history (use /report instead).

**Response:**
```json
{
  "stats": [
    {"date": "2026-01-26", "count": 10}
  ],
  "logs": [
    {
      "id": 1,
      "timestamp": "2026-01-26T12:00:00.000Z",
      "name": "Alice",
      "camera_id": "cam01",
      "image_base64": "base64-encoded-image"
    }
  ]
}
```

### 3. Student Management

#### POST /api/v1/students
Create or update a student record.

**Request Body:**
```json
{
  "student_id": "STU2026001",
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "+1234567890",
  "department": "Computer Science"
}
```

**Response:**
```json
{
  "status": "success",
  "student_id": 1
}
```

#### GET /api/v1/students
Get list of students with optional search.

**Query Parameters:**
- `limit` (optional): Maximum number of results (default: 100, max: 1000)
- `search` (optional): Search term for name, ID, or email

**Response:**
```json
{
  "students": [
    {
      "id": 1,
      "student_id": "STU2026001",
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "phone": "+1234567890",
      "department": "Computer Science",
      "created_at": "2026-01-26T10:00:00.000Z",
      "updated_at": "2026-01-26T10:00:00.000Z"
    }
  ]
}
```

#### GET /api/v1/students/{student_id}
Get a specific student by ID.

**Response:**
```json
{
  "student": {
    "id": 1,
    "student_id": "STU2026001",
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "+1234567890",
    "department": "Computer Science",
    "created_at": "2026-01-26T10:00:00.000Z",
    "updated_at": "2026-01-26T10:00:00.000Z"
  }
}
```

### 4. Session Management

#### POST /api/v1/sessions
Create a new attendance session.

**Request Body:**
```json
{
  "session_name": "Math Class - Chapter 5",
  "course_id": "MATH101"
}
```

**Response:**
```json
{
  "status": "success",
  "session_id": 1
}
```

#### POST /api/v1/sessions/{session_id}/end
End an attendance session.

**Response:**
```json
{
  "status": "success"
}
```

#### GET /api/v1/sessions/active
Get the currently active session.

**Response:**
```json
{
  "session": {
    "id": 1,
    "session_name": "Math Class - Chapter 5",
    "course_id": "MATH101",
    "started_at": "2026-01-26T10:00:00.000Z",
    "ended_at": null,
    "status": "active",
    "total_checked_in": 5
  }
}
```

### 5. Dashboard & Statistics

#### GET /api/v1/dashboard/stats
Get comprehensive dashboard statistics.

**Response:**
```json
{
  "total_students": 100,
  "today_attendance": 25,
  "today_checkins": 30,
  "week_attendance": 80,
  "week_checkins": 95,
  "active_sessions": 1,
  "daily_stats": [
    {"date": "2026-01-26", "unique": 25, "total": 30},
    {"date": "2026-01-25", "unique": 20, "total": 22}
  ]
}
```

#### GET /api/v1/state
Get current system state.

**Response:**
```json
{
  "last_update": "2026-01-26T12:00:00.000Z",
  "last_event": {
    "timestamp": "2026-01-26T12:00:00.000Z",
    "camera_id": "cam01",
    "total_faces": 3,
    "known_faces": [
      {"name": "Alice", "confidence": 0.92}
    ],
    "unknown_faces": 1
  },
  "recent_logs": []
}
```

### 6. WebSocket Connection

#### WebSocket /ws
Real-time updates for face detection events.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

**Message Format:**
```json
{
  "type": "event",
  "payload": {
    "timestamp": "2026-01-26T12:00:00.000Z",
    "camera_id": "cam01",
    "total_faces": 3,
    "known_faces": [
      {"name": "Alice", "confidence": 0.92}
    ],
    "unknown_faces": 1
  }
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Database Schema

### Students Table
- `id`: Primary key
- `student_id`: Unique student identifier
- `name`: Student full name
- `email`: Email address
- `phone`: Phone number
- `department`: Department/ faculty
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Attendance Sessions Table
- `id`: Primary key
- `session_name`: Session description
- `course_id`: Course identifier
- `started_at`: Session start time
- `ended_at`: Session end time
- `status`: Session status (active/completed)
- `total_checked_in`: Number of check-ins

### Attendance Table
- `id`: Primary key
- `session_id`: Foreign key to sessions
- `student_id`: Foreign key to students
- `timestamp`: Check-in time
- `check_in_type`: Type of check-in (face/manual)
- `confidence_score`: Face recognition confidence
- `camera_id`: Camera identifier
- `image_base64`: Base64-encoded image
- `latitude`: GPS latitude
- `longitude`: GPS longitude
- `ip_address`: Client IP address

## Usage Examples

### Python Example
```python
import requests

# Create a student
response = requests.post('http://localhost:8000/api/v1/students', json={
    'student_id': 'STU2026001',
    'name': 'Alice Johnson',
    'email': 'alice@example.com'
})

# Create a session
response = requests.post('http://localhost:8000/api/v1/sessions', json={
    'session_name': 'Math Class',
    'course_id': 'MATH101'
})
session_id = response.json()['session_id']

# Get attendance report
response = requests.get(f'http://localhost:8000/api/v1/attendance/report?session_id={session_id}')
report = response.json()['report']
```

### JavaScript Example
```javascript
// Get dashboard stats
fetch('http://localhost:8000/api/v1/dashboard/stats')
  .then(response => response.json())
  .then(data => console.log(data));

// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'event') {
    console.log('Face detected:', data.payload);
  }
};
```

## Migration

To migrate from the old database schema:

```bash
python scripts/migrate_db.py
```

This will:
1. Backup the existing database
2. Update the schema
3. Migrate all existing data
4. Remove the old tables
