# API Examples

This document provides practical examples for using the CPS Talent Acquisition System API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication (demo version).

## Content Types

- Request: `application/json` or `multipart/form-data` (for file uploads)
- Response: `application/json`

---

## Jobs API

### 1. Create a Job

**Endpoint:** `POST /api/v1/jobs`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "location": "Ho Chi Minh City, Vietnam",
    "status": "active",
    "jd_text": "We are seeking a Senior Python Developer with 5+ years of experience in building scalable web applications. Must have expertise in FastAPI, PostgreSQL, and Docker. Experience with AI/ML is a plus. Responsibilities include designing APIs, optimizing database queries, and mentoring junior developers.",
    "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API", "Git", "Linux"]
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Senior Python Developer",
  "location": "Ho Chi Minh City, Vietnam",
  "status": "active",
  "jd_text": "We are seeking a Senior Python Developer...",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API", "Git", "Linux"],
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### 2. List All Jobs

**Endpoint:** `GET /api/v1/jobs`

**Request:**
```bash
curl "http://localhost:8000/api/v1/jobs"
```

**With Status Filter:**
```bash
curl "http://localhost:8000/api/v1/jobs?status=active"
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Senior Python Developer",
    "location": "Ho Chi Minh City, Vietnam",
    "status": "active",
    "jd_text": "We are seeking...",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

### 3. Get Job Details with Candidates

**Endpoint:** `GET /api/v1/jobs/{job_id}`

**Request:**
```bash
curl "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000"
```

**With Score Filter:**
```bash
curl "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000?min_score=70"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Senior Python Developer",
  "location": "Ho Chi Minh City, Vietnam",
  "status": "active",
  "jd_text": "We are seeking...",
  "required_skills": ["Python", "FastAPI", "PostgreSQL"],
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "candidates": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
      "experience_years": 6.5,
      "application_status": "scored",
      "overall_score": 87.5
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "name": "Jane Smith",
      "email": "jane.smith@example.com",
      "skills": ["Python", "Django", "MySQL", "Docker"],
      "experience_years": 4.0,
      "application_status": "scored",
      "overall_score": 72.3
    }
  ]
}
```

---

## Applications API

### 4. Apply for a Job (Upload CV)

**Endpoint:** `POST /api/v1/apply`

**Request (with file):**
```bash
curl -X POST "http://localhost:8000/api/v1/apply" \
  -F "job_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "cv_file=@/path/to/resume.pdf" \
  -F "name=John Doe" \
  -F "email=john.doe@example.com" \
  -F "phone=+84123456789" \
  -F "linkedin=https://linkedin.com/in/johndoe"
```

**Note:** 
- `cv_file` is required (PDF or DOCX, max 10MB)
- `name`, `email`, `phone`, `linkedin` are optional (will be extracted from CV if not provided)

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidate_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "scored",
  "scores": {
    "skill_fit": 85.0,
    "experience_fit": 90.0,
    "education_fit": 85.0,
    "keyword_match": 90.0,
    "overall_score": 87.5
  },
  "created_at": "2024-01-15T11:00:00",
  "updated_at": "2024-01-15T11:00:05"
}
```

### 5. List All Applications

**Endpoint:** `GET /api/v1/applications`

**Request:**
```bash
curl "http://localhost:8000/api/v1/applications"
```

**Response:**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440003",
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "candidate_id": "660e8400-e29b-41d4-a716-446655440001",
    "status": "scored",
    "scores": {
      "skill_fit": 85.0,
      "experience_fit": 90.0,
      "education_fit": 85.0,
      "keyword_match": 90.0,
      "overall_score": 87.5
    },
    "created_at": "2024-01-15T11:00:00",
    "updated_at": "2024-01-15T11:00:05"
  }
]
```

### 6. Shortlist an Application

**Endpoint:** `POST /api/v1/applications/{application_id}/shortlist`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/applications/770e8400-e29b-41d4-a716-446655440003/shortlist"
```

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidate_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "shortlisted",
  "scores": {
    "skill_fit": 85.0,
    "experience_fit": 90.0,
    "education_fit": 85.0,
    "keyword_match": 90.0,
    "overall_score": 87.5
  },
  "created_at": "2024-01-15T11:00:00",
  "updated_at": "2024-01-15T11:05:00"
}
```

---

## Integrations API

### 7. Sync to SuccessFactors (Mock)

**Endpoint:** `POST /api/v1/integrations/successfactors/sync`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/integrations/successfactors/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "application_ids": [
      "770e8400-e29b-41d4-a716-446655440003",
      "770e8400-e29b-41d4-a716-446655440004"
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "synced_count": 2,
  "message": "Successfully synced 2 application(s) to SuccessFactors",
  "timestamp": "2024-01-15T11:10:00",
  "mock_payload": {
    "sync_timestamp": "2024-01-15T11:10:00",
    "applications": [
      {
        "candidateId": "660e8400-e29b-41d4-a716-446655440001",
        "jobRequisitionId": "550e8400-e29b-41d4-a716-446655440000",
        "applicationDate": "2024-01-15T11:00:00",
        "status": "SHORTLISTED",
        "source": "CPS_TALENT_ACQUISITION",
        "candidateProfile": {
          "firstName": "John",
          "lastName": "Doe",
          "email": "john.doe@example.com",
          "phoneNumber": "+84123456789"
        },
        "scores": {
          "skill_fit": 85.0,
          "experience_fit": 90.0,
          "education_fit": 85.0,
          "keyword_match": 90.0,
          "overall_score": 87.5
        },
        "resumeUrl": "http://minio:9000/resumes/..."
      }
    ]
  }
}
```

### 8. Get SuccessFactors Integration Documentation

**Endpoint:** `GET /api/v1/integrations/successfactors/documentation`

**Request:**
```bash
curl "http://localhost:8000/api/v1/integrations/successfactors/documentation"
```

**Response:**
```json
{
  "title": "SAP SuccessFactors Integration Guide",
  "description": "Guide for integrating with SAP SuccessFactors Recruiting API",
  "authentication": {
    "method": "OAuth2 Client Credentials",
    "token_endpoint": "https://{datacenter}.successfactors.com/oauth/token",
    "required_params": {
      "grant_type": "client_credentials",
      "client_id": "your_client_id",
      "client_secret": "your_client_secret",
      "company_id": "your_company_id"
    }
  },
  "endpoints": {
    "candidate": {
      "url": "https://{datacenter}.successfactors.com/odata/v2/Candidate",
      "method": "POST",
      "description": "Create or update candidate profile",
      "required_fields": ["firstName", "lastName", "email"]
    },
    "job_application": {
      "url": "https://{datacenter}.successfactors.com/odata/v2/JobApplication",
      "method": "POST",
      "description": "Create job application",
      "required_fields": ["candidateId", "jobRequisitionId", "applicationDate"]
    },
    "attachment": {
      "url": "https://{datacenter}.successfactors.com/odata/v2/Attachment",
      "method": "POST",
      "description": "Upload resume/CV attachment",
      "required_fields": ["documentName", "fileContent", "mimeType"]
    }
  },
  "example_workflow": [
    "1. Obtain OAuth2 token using client credentials",
    "2. Create Candidate record (POST /Candidate)",
    "3. Upload resume as Attachment (POST /Attachment)",
    "4. Create JobApplication linking candidate to job (POST /JobApplication)",
    "5. Update application status as needed"
  ],
  "references": [
    "https://help.sap.com/docs/SAP_SUCCESSFACTORS_RECRUITING",
    "https://api.sap.com/api/RCMCandidate/overview"
  ]
}
```

---

## Health Check

### 9. Health Check

**Endpoint:** `GET /health`

**Request:**
```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Only PDF and DOCX files are supported"
}
```

### 404 Not Found
```json
{
  "detail": "Job not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: <error message>"
}
```

---

## Python Examples

### Using `requests` library

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a job
job_data = {
    "title": "Senior Python Developer",
    "location": "Ho Chi Minh City, Vietnam",
    "status": "active",
    "jd_text": "We are seeking a Senior Python Developer...",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"]
}

response = requests.post(f"{BASE_URL}/api/v1/jobs", json=job_data)
job = response.json()
job_id = job["id"]
print(f"Created job: {job_id}")

# Apply for the job
files = {"cv_file": open("resume.pdf", "rb")}
data = {
    "job_id": job_id,
    "name": "John Doe",
    "email": "john.doe@example.com"
}

response = requests.post(f"{BASE_URL}/api/v1/apply", files=files, data=data)
application = response.json()
print(f"Application created: {application['id']}")
print(f"Overall score: {application['scores']['overall_score']}")

# Get job details with candidates
response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}")
job_detail = response.json()
print(f"Job has {len(job_detail['candidates'])} candidates")

# Shortlist the application
response = requests.post(f"{BASE_URL}/api/v1/applications/{application['id']}/shortlist")
print(f"Application status: {response.json()['status']}")

# Sync to SuccessFactors
sync_data = {"application_ids": [application["id"]]}
response = requests.post(f"{BASE_URL}/api/v1/integrations/successfactors/sync", json=sync_data)
print(f"Sync result: {response.json()['message']}")
```

---

## JavaScript Examples

### Using `fetch` API

```javascript
const BASE_URL = "http://localhost:8000";

// Create a job
async function createJob() {
  const jobData = {
    title: "Senior Python Developer",
    location: "Ho Chi Minh City, Vietnam",
    status: "active",
    jd_text: "We are seeking a Senior Python Developer...",
    required_skills: ["Python", "FastAPI", "PostgreSQL"]
  };

  const response = await fetch(`${BASE_URL}/api/v1/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(jobData)
  });

  const job = await response.json();
  console.log("Created job:", job.id);
  return job.id;
}

// Apply for a job
async function applyForJob(jobId, cvFile) {
  const formData = new FormData();
  formData.append("job_id", jobId);
  formData.append("cv_file", cvFile);
  formData.append("name", "John Doe");
  formData.append("email", "john.doe@example.com");

  const response = await fetch(`${BASE_URL}/api/v1/apply`, {
    method: "POST",
    body: formData
  });

  const application = await response.json();
  console.log("Application created:", application.id);
  console.log("Overall score:", application.scores.overall_score);
  return application.id;
}

// Get job details
async function getJobDetails(jobId) {
  const response = await fetch(`${BASE_URL}/api/v1/jobs/${jobId}`);
  const jobDetail = await response.json();
  console.log("Candidates:", jobDetail.candidates);
}

// Usage
const jobId = await createJob();
const applicationId = await applyForJob(jobId, fileInput.files[0]);
await getJobDetails(jobId);
```

---

## Postman Collection

You can import these examples into Postman by creating a new collection and adding requests with the endpoints and payloads shown above.

### Environment Variables for Postman

```json
{
  "base_url": "http://localhost:8000",
  "job_id": "",
  "application_id": "",
  "candidate_id": ""
}
```

---

## Tips

1. **Save IDs**: Always save the IDs returned from create operations for use in subsequent requests
2. **File Upload**: Ensure CV files are PDF or DOCX format and under 10MB
3. **OpenAI Key**: Make sure your OpenAI API key is set in `.env` for parsing and scoring to work
4. **Async Processing**: CV parsing and scoring may take 3-8 seconds depending on file size
5. **Score Filtering**: Use `min_score` parameter to filter candidates by minimum score threshold

---

For more information, see the [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md).

