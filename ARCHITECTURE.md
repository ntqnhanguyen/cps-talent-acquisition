# Architecture Documentation

## System Overview

The CPS Talent Acquisition System is a modern, AI-powered recruitment platform built with microservices architecture principles. The system automates CV parsing and candidate scoring to streamline the hiring process.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  (Web Browser, Mobile App, API Clients)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTPS/REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    API Gateway Layer                         │
│                     (FastAPI)                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐      │
│  │  Jobs    │  │  Apply   │  │  Integrations        │      │
│  │  API     │  │  API     │  │  API                 │      │
│  └──────────┘  └──────────┘  └──────────────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────┐  ┌────────────┐  ┌────────────────┐
│  Business  │  │  Business  │  │   Business     │
│  Logic     │  │  Logic     │  │   Logic        │
│  Services  │  │  Services  │  │   Services     │
│            │  │            │  │                │
│ • Storage  │  │ • AI       │  │ • Success      │
│ • Parser   │  │   Parser   │  │   Factors      │
│ • Scorer   │  │ • Scorer   │  │                │
└─────┬──────┘  └─────┬──────┘  └────────────────┘
      │               │
      │               │ OpenAI API
      │               │
      ▼               ▼
┌─────────────────────────────────────────────────┐
│              Data Layer                          │
│  ┌──────────────┐         ┌──────────────┐     │
│  │  PostgreSQL  │         │    MinIO     │     │
│  │  (Metadata)  │         │  (CV Files)  │     │
│  └──────────────┘         └──────────────┘     │
└─────────────────────────────────────────────────┘
```

## Component Details

### 1. API Gateway Layer (FastAPI)

**Responsibilities:**
- Handle HTTP requests and responses
- Request validation using Pydantic schemas
- Authentication and authorization (future)
- Rate limiting (future)
- API documentation (OpenAPI/Swagger)

**Key Components:**
- `app/main.py`: Application entry point
- `app/api/`: Route handlers for different domains
- `app/schemas/`: Request/response validation schemas

**Technology:**
- FastAPI 0.109+
- Uvicorn (ASGI server)
- Pydantic (data validation)

### 2. Business Logic Layer

#### 2.1 Storage Service
**Purpose:** Manage file storage operations with MinIO

**Key Functions:**
- Upload CV files to object storage
- Download files for processing
- Delete files when needed
- Generate file URLs

**Implementation:** `app/services/storage.py`

#### 2.2 AI Parser Service
**Purpose:** Extract structured information from CVs

**Key Functions:**
- Extract text from PDF/DOCX files
- Parse CV content using OpenAI API
- Normalize and structure candidate data

**Implementation:** `app/services/ai_parser.py`

**AI Model:** GPT-4.1-mini

**Extracted Fields:**
- Name, Email, Phone, LinkedIn
- Skills (list)
- Experience years (number)
- Education (string)

#### 2.3 AI Scorer Service
**Purpose:** Score candidates against job requirements

**Key Functions:**
- Compare candidate profile with job description
- Calculate sub-scores (skill, experience, education, keyword match)
- Compute weighted overall score

**Implementation:** `app/services/ai_scorer.py`

**Scoring Algorithm:**
```
overall_score = (
    skill_fit * 0.40 +
    experience_fit * 0.30 +
    education_fit * 0.15 +
    keyword_match * 0.15
)
```

#### 2.4 SuccessFactors Service
**Purpose:** Integrate with SAP SuccessFactors (mock)

**Key Functions:**
- Sync candidate applications to SuccessFactors
- Provide integration documentation
- Log sync operations

**Implementation:** `app/services/successfactors.py`

### 3. Data Layer

#### 3.1 PostgreSQL Database

**Purpose:** Store structured metadata

**Tables:**
- **jobs**: Job postings with descriptions and requirements
- **candidates**: Candidate profiles and parsed information
- **applications**: Job applications linking candidates to jobs

**Technology:**
- PostgreSQL 15
- SQLAlchemy 2.0 (async ORM)
- Alembic (migrations)

**Connection:**
- Async connection using asyncpg driver
- Connection pooling managed by SQLAlchemy
- Session management with dependency injection

#### 3.2 MinIO Object Storage

**Purpose:** Store binary files (CVs)

**Features:**
- S3-compatible API
- Bucket-based organization
- Public read access for resume bucket

**Configuration:**
- Bucket: `resumes`
- Endpoint: `minio:9000`
- Console: `minio:9001`

## Data Flow

### Application Workflow

```
1. Candidate uploads CV
   ↓
2. API validates file (type, size)
   ↓
3. Upload CV to MinIO
   ↓
4. Extract text from CV
   ↓
5. Parse CV with AI (OpenAI)
   ↓
6. Create/Update Candidate record
   ↓
7. Create Application record (status: parsed)
   ↓
8. Score candidate against job
   ↓
9. Update Application with scores (status: scored)
   ↓
10. Return application details
```

### Scoring Workflow

```
1. Fetch candidate profile
   ↓
2. Fetch job description and required skills
   ↓
3. Send to OpenAI for scoring
   ↓
4. Receive sub-scores
   ↓
5. Calculate overall score
   ↓
6. Store scores in Application
   ↓
7. Update application status
```

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│      Job        │
├─────────────────┤
│ id (PK)         │
│ title           │
│ location        │
│ status          │
│ jd_text         │
│ required_skills │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────────┐
│   Application       │
├─────────────────────┤
│ id (PK)             │
│ job_id (FK)         │
│ candidate_id (FK)   │
│ status              │
│ scores              │
│ created_at          │
│ updated_at          │
└────────┬────────────┘
         │
         │ N:1
         │
┌────────▼────────┐
│   Candidate     │
├─────────────────┤
│ id (PK)         │
│ name            │
│ email (unique)  │
│ phone           │
│ linkedin        │
│ resume_url      │
│ skills          │
│ experience_yrs  │
│ education       │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## API Design

### RESTful Principles

- Resource-based URLs
- HTTP methods for CRUD operations
- JSON request/response format
- Proper status codes
- Consistent error handling

### API Versioning

- Version prefix: `/api/v1/`
- Future versions: `/api/v2/`, etc.

### Response Format

**Success Response:**
```json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  ...
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

## Security Considerations

### Current Implementation (Demo)

- Basic file validation (type, size)
- No authentication/authorization
- CORS enabled for development

### Production Recommendations

1. **Authentication & Authorization**
   - JWT-based authentication
   - Role-based access control (Admin, Recruiter, Candidate)
   - API key for integrations

2. **File Security**
   - Antivirus scanning for uploaded files
   - Content-type verification
   - Size limits enforcement
   - Secure file storage with encryption

3. **Data Privacy**
   - PII masking in logs
   - GDPR compliance
   - Data retention policies
   - Secure deletion

4. **API Security**
   - Rate limiting
   - Input sanitization
   - SQL injection prevention (using ORM)
   - HTTPS only in production

## Scalability

### Current Design

- Stateless API (horizontal scaling ready)
- Async I/O for database operations
- Object storage for files (scalable)

### Future Enhancements

1. **Async Processing**
   - Message queue (RabbitMQ, Redis)
   - Background workers (Celery)
   - Separate parsing/scoring workers

2. **Caching**
   - Redis for frequently accessed data
   - Cache job descriptions
   - Cache candidate profiles

3. **Load Balancing**
   - Multiple API instances
   - Load balancer (Nginx, HAProxy)
   - Session affinity if needed

4. **Database Optimization**
   - Read replicas for queries
   - Connection pooling
   - Query optimization
   - Indexing strategy

## Monitoring & Observability

### Logging

- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation (future)

### Metrics (Future)

- Request rate and latency
- Error rates
- Database connection pool
- Storage usage
- AI API usage and costs

### Health Checks

- `/health` endpoint
- Database connectivity check
- Storage connectivity check

## Deployment

### Docker Compose (Development)

- Single-host deployment
- All services on one machine
- Suitable for development and demo

### Production Deployment (Recommendations)

1. **Container Orchestration**
   - Kubernetes
   - Docker Swarm
   - AWS ECS

2. **Infrastructure**
   - Managed PostgreSQL (AWS RDS, Azure Database)
   - Managed object storage (AWS S3, Azure Blob)
   - Managed Kubernetes (EKS, AKS, GKE)

3. **CI/CD**
   - GitHub Actions / GitLab CI
   - Automated testing
   - Automated deployment
   - Blue-green deployment

## Integration Points

### OpenAI API

**Purpose:** AI parsing and scoring

**Endpoints Used:**
- `/v1/chat/completions`

**Models:**
- `gpt-4.1-mini` (cost-effective, fast)

**Rate Limits:**
- Monitor usage
- Implement retry logic
- Handle rate limit errors

### SuccessFactors API (Future)

**Authentication:** OAuth2 Client Credentials

**Endpoints:**
- `/odata/v2/Candidate` (POST)
- `/odata/v2/JobApplication` (POST)
- `/odata/v2/Attachment` (POST)

**Workflow:**
1. Obtain OAuth2 token
2. Create candidate profile
3. Upload resume attachment
4. Create job application
5. Update application status

## Performance Targets

### Response Times

- Job listing: < 300ms
- Job detail with candidates: < 500ms
- CV upload and parsing: < 5s
- Candidate scoring: < 3s

### Throughput

- 100+ concurrent users
- 1000+ applications per day
- 10+ jobs created per day

## Error Handling

### Strategy

1. **Validation Errors (400)**
   - Invalid input data
   - Missing required fields
   - File format errors

2. **Not Found (404)**
   - Resource doesn't exist

3. **Server Errors (500)**
   - Database errors
   - Storage errors
   - AI API errors

### Retry Logic

- Retry transient failures
- Exponential backoff
- Maximum retry attempts

## Future Enhancements

1. **Chatbot Integration**
   - Candidate Q&A
   - Application status inquiry
   - Interview scheduling

2. **Analytics Dashboard**
   - Hiring metrics
   - Time-to-hire
   - Source effectiveness
   - Candidate funnel

3. **Advanced AI Features**
   - Resume ranking with ML models
   - Bias detection
   - Interview question generation
   - Candidate matching recommendations

4. **Notification System**
   - Email notifications
   - SMS notifications
   - In-app notifications
   - Webhook support

5. **Multi-tenancy**
   - Support multiple companies
   - Tenant isolation
   - Custom branding

## Conclusion

The CPS Talent Acquisition System is designed with modern architecture principles, focusing on scalability, maintainability, and extensibility. The current implementation provides a solid foundation for a production-ready recruitment platform.

