# CPS Talent Acquisition System

AI-powered recruitment platform for talent acquisition with automated CV parsing and candidate scoring.

## Features

- **Job Management**: Create and manage job postings with detailed job descriptions
- **Candidate Application**: Public form for candidates to upload CVs (PDF/DOCX)
- **AI CV Parsing**: Automatic extraction of candidate information using OpenAI
- **AI Scoring**: Intelligent candidate scoring against job requirements
- **Candidate Pipeline**: Track candidates through stages (Applied → Parsed → Scored → Shortlisted → Synced)
- **SuccessFactors Integration**: Mock integration with SAP SuccessFactors (with documentation for real implementation)

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11**: Programming language
- **Uvicorn**: ASGI server

### Database
- **PostgreSQL 15**: Relational database
- **SQLAlchemy 2.0**: ORM (Object-Relational Mapping)
- **Alembic**: Database migrations

### Storage
- **MinIO**: S3-compatible object storage for CV files

### AI/ML
- **OpenAI API**: For CV parsing and candidate scoring

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Project Structure

```
cps-talent-acquisition/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection & session
│   ├── models/                 # SQLAlchemy models
│   │   ├── job.py
│   │   ├── candidate.py
│   │   └── application.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── job.py
│   │   ├── candidate.py
│   │   └── application.py
│   ├── api/                    # API routes
│   │   ├── jobs.py
│   │   ├── applications.py
│   │   └── integrations.py
│   ├── services/               # Business logic
│   │   ├── storage.py          # MinIO operations
│   │   ├── ai_parser.py        # CV parsing logic
│   │   ├── ai_scorer.py        # Scoring logic
│   │   └── successfactors.py  # Mock integration
│   └── utils/                  # Utilities
├── docker/
│   └── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- OpenAI API key (for AI parsing and scoring)

## Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd cps-talent-acquisition
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI API key:

```env
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Start the services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- MinIO object storage on ports 9000 (API) and 9001 (Console)
- FastAPI application on port 8000

### 4. Verify the services

Check if all services are running:

```bash
docker-compose ps
```

Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Access MinIO Console:
- URL: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin123`

## API Endpoints

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/jobs` | List all jobs |
| `POST` | `/api/v1/jobs` | Create a new job |
| `GET` | `/api/v1/jobs/{id}` | Get job details with candidate pipeline |

### Applications

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/apply` | Apply for a job (upload CV) |
| `GET` | `/api/v1/applications` | List all applications |
| `POST` | `/api/v1/applications/{id}/shortlist` | Mark application as shortlisted |

### Integrations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/integrations/successfactors/sync` | Sync applications to SuccessFactors (mock) |
| `GET` | `/api/v1/integrations/successfactors/documentation` | Get SuccessFactors integration documentation |

## Usage Examples

### 1. Create a Job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Software Engineer",
    "location": "Ho Chi Minh City, Vietnam",
    "status": "active",
    "jd_text": "We are looking for a Senior Software Engineer with 5+ years of experience in Python and FastAPI...",
    "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST API"]
  }'
```

### 2. Apply for a Job

```bash
curl -X POST "http://localhost:8000/api/v1/apply" \
  -F "job_id=<job-uuid>" \
  -F "cv_file=@/path/to/resume.pdf" \
  -F "name=John Doe" \
  -F "email=john.doe@example.com"
```

### 3. Get Job Details with Candidates

```bash
curl "http://localhost:8000/api/v1/jobs/<job-uuid>"
```

### 4. Filter Candidates by Score

```bash
curl "http://localhost:8000/api/v1/jobs/<job-uuid>?min_score=70"
```

### 5. Shortlist a Candidate

```bash
curl -X POST "http://localhost:8000/api/v1/applications/<application-uuid>/shortlist"
```

### 6. Sync to SuccessFactors

```bash
curl -X POST "http://localhost:8000/api/v1/integrations/successfactors/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "application_ids": ["<application-uuid-1>", "<application-uuid-2>"]
  }'
```

## Workflow

1. **Create Job**: Admin creates a job posting with job description and required skills
2. **Candidate Applies**: Candidate uploads CV through the application form
3. **AI Parsing**: System automatically extracts structured information from CV
4. **AI Scoring**: System scores candidate against job requirements
5. **TA Dashboard**: Recruiter views ranked candidates on the dashboard
6. **Shortlist**: Recruiter marks top candidates as shortlisted
7. **Sync**: Recruiter syncs shortlisted candidates to SuccessFactors

## Data Model

### Job
- ID, Title, Location, Status
- Job Description Text
- Required Skills
- Timestamps

### Candidate
- ID, Name, Email, Phone, LinkedIn
- Resume URL
- Skills, Experience Years, Education
- Timestamps

### Application
- ID, Job ID, Candidate ID
- Status (applied → parsed → scored → shortlisted → synced)
- Scores (skill_fit, experience_fit, education_fit, keyword_match, overall_score)
- Timestamps

## AI Features

### CV Parsing
The system uses OpenAI's GPT-4.1-mini model to extract:
- Personal information (name, email, phone, LinkedIn)
- Skills (automatically normalized)
- Years of experience
- Education background

### Candidate Scoring
The system scores candidates on multiple dimensions:
- **Skill Fit** (40%): Match between candidate skills and required skills
- **Experience Fit** (30%): Relevance of work experience
- **Education Fit** (15%): Match of educational background
- **Keyword Match** (15%): Alignment with job description keywords

Overall score is calculated as a weighted average of sub-scores.

## SuccessFactors Integration

The current implementation includes a **mock integration** for demonstration purposes. 

For real integration, see the documentation endpoint:
```bash
curl "http://localhost:8000/api/v1/integrations/successfactors/documentation"
```

This provides:
- OAuth2 authentication flow
- API endpoints for Candidate, JobApplication, and Attachment
- Example workflow
- Official documentation links

## Development

### Run without Docker

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL and MinIO locally

3. Configure `.env` file

4. Run the application:
```bash
uvicorn app.main:app --reload
```

### Run tests

```bash
pytest
```

## Logs

View application logs:
```bash
docker-compose logs -f api
```

View all service logs:
```bash
docker-compose logs -f
```

## Stopping the Services

```bash
docker-compose down
```

To remove volumes (database and storage data):
```bash
docker-compose down -v
```

## Troubleshooting

### Database connection issues
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check database logs: `docker-compose logs postgres`

### MinIO connection issues
- Verify MinIO is running: `docker-compose ps`
- Check MinIO logs: `docker-compose logs minio`
- Ensure bucket was created: `docker-compose logs minio-init`

### OpenAI API errors
- Verify your API key is set correctly in `.env`
- Check API quota and billing status

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.

