# Quick Start Guide

This guide will help you get the CPS Talent Acquisition System up and running in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

## Step-by-Step Setup

### 1. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# You can use any text editor (nano, vim, or VS Code)
nano .env
```

Set your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. Start the System

```bash
# Start all services (PostgreSQL, MinIO, API)
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
docker-compose ps
```

You should see all services running:
- `cps-postgres` (healthy)
- `cps-minio` (healthy)
- `cps-api` (running)

### 3. Verify Installation

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (login: minioadmin / minioadmin123)

### 4. Create Your First Job

Using the API documentation (http://localhost:8000/docs):

1. Find the `POST /api/v1/jobs` endpoint
2. Click "Try it out"
3. Use this sample data:

```json
{
  "title": "Senior Python Developer",
  "location": "Ho Chi Minh City, Vietnam",
  "status": "active",
  "jd_text": "We are seeking a Senior Python Developer with 5+ years of experience in building scalable web applications. Must have expertise in FastAPI, PostgreSQL, and Docker. Experience with AI/ML is a plus.",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API", "Git"]
}
```

4. Click "Execute"
5. Copy the `id` from the response (you'll need it later)

### 5. Apply for the Job

You can use curl or the API documentation:

#### Using curl:

```bash
# Replace <JOB_ID> with the actual job ID from step 4
# Replace /path/to/resume.pdf with your actual CV file

curl -X POST "http://localhost:8000/api/v1/apply" \
  -F "job_id=<JOB_ID>" \
  -F "cv_file=@/path/to/resume.pdf" \
  -F "name=John Doe" \
  -F "email=john.doe@example.com" \
  -F "phone=+84123456789"
```

#### Using API Documentation:

1. Find the `POST /api/v1/apply` endpoint
2. Click "Try it out"
3. Fill in:
   - `job_id`: The job ID from step 4
   - `cv_file`: Click to upload a PDF or DOCX file
   - `name`: Your name (optional)
   - `email`: Your email (optional)
   - `phone`: Your phone (optional)
4. Click "Execute"

The system will:
- Upload your CV to MinIO
- Extract text from the CV
- Parse it with AI to extract your profile
- Score you against the job requirements
- Return your application details with scores

### 6. View Candidates for the Job

```bash
# Replace <JOB_ID> with the actual job ID
curl "http://localhost:8000/api/v1/jobs/<JOB_ID>"
```

Or use the API documentation:
1. Find `GET /api/v1/jobs/{job_id}`
2. Enter the job ID
3. Click "Execute"

You'll see:
- Job details
- List of candidates ranked by overall score
- Each candidate's skills, experience, and scores

### 7. Filter by Minimum Score

```bash
# Only show candidates with score >= 70
curl "http://localhost:8000/api/v1/jobs/<JOB_ID>?min_score=70"
```

### 8. Shortlist a Candidate

```bash
# Replace <APPLICATION_ID> with the actual application ID
curl -X POST "http://localhost:8000/api/v1/applications/<APPLICATION_ID>/shortlist"
```

### 9. Sync to SuccessFactors (Mock)

```bash
curl -X POST "http://localhost:8000/api/v1/integrations/successfactors/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "application_ids": ["<APPLICATION_ID_1>", "<APPLICATION_ID_2>"]
  }'
```

This will return a mock success response with the payload that would be sent to SuccessFactors.

## Common Commands

### View Logs

```bash
# View API logs
docker-compose logs -f api

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs postgres
docker-compose logs minio
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (delete all data)
docker-compose down -v
```

### Access Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U cps_user -d cps_talent_acquisition

# List tables
\dt

# Query jobs
SELECT * FROM jobs;

# Query candidates
SELECT * FROM candidates;

# Query applications
SELECT * FROM applications;

# Exit
\q
```

## Troubleshooting

### Services not starting

```bash
# Check service status
docker-compose ps

# Check logs for errors
docker-compose logs
```

### Database connection error

```bash
# Restart database
docker-compose restart postgres

# Check database is healthy
docker-compose ps postgres
```

### MinIO connection error

```bash
# Restart MinIO
docker-compose restart minio

# Check bucket was created
docker-compose logs minio-init
```

### OpenAI API error

- Verify your API key in `.env`
- Check your OpenAI account has credits
- Check API quota limits

### File upload fails

- Ensure file is PDF or DOCX
- Check file size is under 10MB
- Verify MinIO is running: `docker-compose ps minio`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
- Explore the API documentation at http://localhost:8000/docs
- Check SuccessFactors integration documentation: http://localhost:8000/api/v1/integrations/successfactors/documentation

## Sample Test Data

### Sample Job Postings

**Backend Developer:**
```json
{
  "title": "Backend Developer",
  "location": "Hanoi, Vietnam",
  "status": "active",
  "jd_text": "Looking for a Backend Developer with experience in Python, FastAPI, and PostgreSQL. Must be able to design and implement RESTful APIs.",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST API"]
}
```

**Full Stack Developer:**
```json
{
  "title": "Full Stack Developer",
  "location": "Remote",
  "status": "active",
  "jd_text": "Seeking a Full Stack Developer proficient in both frontend and backend technologies. React, Node.js, and Python experience required.",
  "required_skills": ["React", "Node.js", "Python", "JavaScript", "TypeScript"]
}
```

**DevOps Engineer:**
```json
{
  "title": "DevOps Engineer",
  "location": "Da Nang, Vietnam",
  "status": "active",
  "jd_text": "DevOps Engineer needed to manage cloud infrastructure and CI/CD pipelines. Experience with Docker, Kubernetes, and AWS required.",
  "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"]
}
```

## Support

For issues and questions:
- Check the logs: `docker-compose logs`
- Review the documentation in README.md
- Open an issue on the repository

Happy recruiting! 🚀

