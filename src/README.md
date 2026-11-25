# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Teacher-authenticated activity signup and unregister

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Add a teacher account (passwords are stored as salted hashes in an ignored local file):

   ```
   python src/manage_teachers.py teacher-username
   ```

   Enter and confirm an ASCII password of at least 12 characters when prompted.

3. Run the application from the repository root:

   ```
   uvicorn src.app:app --reload
   ```

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

Students can view activities and participants without signing in. Teachers must log in in the web interface to register or unregister students. The `/auth/login`, signup, and unregister API endpoints require HTTP Basic credentials. The app reads `src/teachers.json`; this file is git-ignored, created with restrictive permissions, and should be provisioned separately on each deployment.

Use HTTPS when exposing the application beyond local development so teacher credentials are encrypted in transit.

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/auth/login`                                                      | Validate teacher credentials                                        |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity (teacher authentication required)           |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister a student (teacher authentication required)            |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
