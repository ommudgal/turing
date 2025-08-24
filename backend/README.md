# Backend API for The Turing Test 25

This is the FastAPI backend for The Turing Test 25 student registration system.

## Features

- Student registration with validation
- Email OTP verification
- reCAPTCHA validation
- CORS enabled for frontend integration

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and configure your email settings:
   ```bash
   cp .env.example .env
   ```

3. Run the server:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 5054 --reload
   ```

## API Endpoints

- `POST /api/v1/student/register` - Register a new student
- `POST /api/v1/student/verify` - Verify OTP
- `GET /api/v1/student/resend-otp` - Resend OTP
- `POST /api/v1/student/validate` - Validate reCAPTCHA

## Docker

Build and run with Docker:
```bash
docker build -t backend .
docker run -p 5054:5054 backend
```

Or use docker-compose from the project root:
```bash
docker-compose up
```
