# AI Recruitment Platform — Backend (Monolith Mode)

A production-ready AI-powered recruitment backend built with **FastAPI** and **MongoDB**.

The project now supports a **single-server monolith runtime** that loads all existing service domains in one process.

---

## Runtime Modes

### Monolith (Recommended)

Run all domains on a single server and single port:

```bash
uvicorn monolith_main:app --host 0.0.0.0 --port 8000 --reload
```

Monolith URLs:

- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Auth APIs: `http://localhost:8000/auth/*`
- Job APIs: `http://localhost:8000/jobs/*`
- Distribution APIs: `http://localhost:8000/distribute-job/*`
- Application APIs: `http://localhost:8000/apply/*`, `http://localhost:8000/job-applications/*`

### AI Screening Cron (Monolith)

The monolith now includes an automated AI screening worker that:

1. Checks expired job posts (`end_time <= now`).
2. Fetches related job applications with missing `ai_score`.
3. Parses resume text from `resume_url` (pdf/txt/docx).
4. Evaluates candidate fit using resume text + job description + job skills.
5. Writes `ai_score`, `strengths`, `weaknesses` back to `job_applications`.

Required environment variable:

- `OPENAI_API_KEY`: enables AI screening worker.

Optional environment variables:

- `AI_CRON_INTERVAL_SECONDS` (default `300`)
- `AI_CUTOFF_SCORE` (default `75`)

Control endpoints:

- `GET /ai-screening/status`
- `POST /ai-screening/run-now`

### Legacy Microservices

If needed, you can still run services independently:

| Service              | Port | Responsibility                                     |
|----------------------|------|----------------------------------------------------|
| Auth Service         | 8001 | User registration, login, JWT authentication       |
| Job Service          | 8002 | Job creation, listing, deletion (HR-only writes)   |
| Distribution Service | 8003 | Social media share links for job postings          |
| Application Service  | 8004 | Candidate applications and resume file uploads     |

---

## Project Structure

```
ai-recruitment-platform/
├── services/
│   ├── auth-service/           # Port 8001
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── .env
│   │   ├── models/user.py
│   │   ├── schemas/user.py
│   │   ├── routes/auth.py
│   │   ├── services/auth_service.py
│   │   └── utils/password.py
│   │
│   ├── job-service/            # Port 8002
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── .env
│   │   ├── models/job.py
│   │   ├── schemas/job.py
│   │   ├── routes/jobs.py
│   │   └── services/job_service.py
│   │
│   ├── distribution-service/   # Port 8003
│   │   ├── main.py
│   │   ├── .env
│   │   ├── adapters/
│   │   │   ├── linkedin_adapter.py
│   │   │   ├── twitter_adapter.py
│   │   │   └── whatsapp_adapter.py
│   │   └── services/distribution_service.py
│   │
│   └── application-service/    # Port 8004
│       ├── main.py
│       ├── database.py
│       ├── .env
│       ├── models/application.py
│       ├── schemas/application.py
│       ├── routes/applications.py
│       └── services/application_service.py
│
├── shared/                     # Shared reference utilities
│   ├── config.py
│   ├── jwt_handler.py
│   └── database.py
│
├── requirements.txt
└── README.md
```

---

## Prerequisites

- **Python 3.10+**
- **MongoDB** running on `localhost:27017`
- pip or a virtual environment manager

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Each service has its own `.env` file. Update them with your values — especially `JWT_SECRET` (use the **same secret across services** that need to verify tokens).

### 3. Start Monolith Server (Single Port)

```bash
uvicorn monolith_main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. (Optional) Start All Services Separately

Open **4 separate terminals**, one per service:

**Terminal 1 — Auth Service (Port 8001):**
```bash
cd services/auth-service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 — Job Service (Port 8002):**
```bash
cd services/job-service
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 3 — Distribution Service (Port 8003):**
```bash
cd services/distribution-service
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Terminal 4 — Application Service (Port 8004):**
```bash
cd services/application-service
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

---

## Interactive API Docs (Swagger UI)

| Service              | URL                             |
|----------------------|---------------------------------|
| Auth Service         | http://localhost:8001/docs      |
| Job Service          | http://localhost:8002/docs      |
| Distribution Service | http://localhost:8003/docs      |
| Application Service  | http://localhost:8004/docs      |

---

## API Reference

### Auth Service — `localhost:8001`

#### POST `/auth/register` — Register a new user
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securePassword123",
    "role": "hr"
}
```
> `role` accepts: `"hr"` or `"candidate"`

#### POST `/auth/login` — Login
```json
{
    "email": "john@example.com",
    "password": "securePassword123"
}
```
**Response:**
```json
{
    "access_token": "<jwt-token>",
    "token_type": "bearer",
    "user": { "id": "...", "name": "...", "email": "...", "role": "hr", "created_at": "..." }
}
```

#### GET `/auth/me` — Get current profile
```
Authorization: Bearer <jwt-token>
```

---

### Job Service — `localhost:8002`

#### POST `/jobs` — Create a job *(HR only)*
```
Authorization: Bearer <hr-jwt-token>
```
```json
{
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer...",
    "skills": ["Python", "FastAPI", "MongoDB", "Docker"],
    "location": "Remote",
    "experience_required": "3-5 years",
    "deadline": "2026-12-31T23:59:59"
}
```

#### GET `/jobs` — List all jobs *(public)*

#### GET `/jobs/{job_id}` — Get single job *(public)*

#### DELETE `/jobs/{job_id}` — Delete a job *(HR owner only)*
```
Authorization: Bearer <hr-jwt-token>
```

---

### Distribution Service — `localhost:8003`

#### POST `/distribute-job/{job_id}` — Generate share links

**Response:**
```json
{
    "job_id": "665abc123...",
    "job_url": "http://localhost:8002/jobs/665abc123...",
    "share_links": {
        "linkedin": "https://www.linkedin.com/sharing/share-offsite/?url=...",
        "twitter": "https://twitter.com/intent/tweet?text=...",
        "whatsapp": "https://wa.me/?text=..."
    },
    "message": "Job distribution links generated successfully"
}
```

---

### Application Service — `localhost:8004`

#### POST `/apply/{job_id}` — Submit a job application *(multipart/form-data)*

| Field            | Type   | Required |
|------------------|--------|----------|
| candidate_name   | string | ✓        |
| email            | string | ✓        |
| phone            | string | ✓        |
| experience       | string | ✓        |
| resume           | file   | ✓ (PDF / DOC / DOCX) |

#### GET `/applications/{job_id}` — View all applications for a job

---

## Database Design

| Collection   | Service  | Fields                                                                  |
|--------------|----------|-------------------------------------------------------------------------|
| `users`      | Auth     | name, email, password (hashed), role, created_at                       |
| `jobs`       | Job      | title, description, skills, location, experience_required, deadline, created_by, created_at |
| `applications` | Application | job_id, candidate_name, email, phone, experience, resume_path, status, created_at |

---

## Security Notes

- Passwords are hashed with **bcrypt** — never stored in plain text.
- JWT tokens are validated on every protected route using the same `JWT_SECRET`.
- Role-based access: only `hr` users can create or delete jobs.
- Resume uploads are restricted to **PDF, DOC, DOCX** file types.
- All inputs are validated with **Pydantic** before reaching the database.

---

## Environment Variables Reference

### Auth Service (`.env`)
| Variable                      | Default                         | Description               |
|-------------------------------|---------------------------------|---------------------------|
| `MONGO_URI`                   | `mongodb://localhost:27017`     | MongoDB connection string |
| `DATABASE_NAME`               | `ai_recruitment`                | Database name             |
| `JWT_SECRET`                  | *(change this)*                 | JWT signing secret        |
| `JWT_ALGORITHM`               | `HS256`                         | JWT algorithm             |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                            | Token lifespan in minutes |

### Job Service (`.env`)
| Variable        | Default                     | Description                              |
|-----------------|-----------------------------|------------------------------------------|
| `MONGO_URI`     | `mongodb://localhost:27017` | MongoDB connection string                |
| `DATABASE_NAME` | `ai_recruitment`            | Database name                            |
| `JWT_SECRET`    | *(must match Auth Service)* | JWT signing secret for token validation  |
| `JWT_ALGORITHM` | `HS256`                     | JWT algorithm                            |

### Distribution Service (`.env`)
| Variable        | Default                     | Description                              |
|-----------------|-----------------------------|------------------------------------------|
| `BASE_JOB_URL`  | `http://localhost:8002`     | Base URL used to construct job share links |

### Application Service (`.env`)
| Variable        | Default                     | Description               |
|-----------------|-----------------------------|---------------------------|
| `MONGO_URI`     | `mongodb://localhost:27017` | MongoDB connection string |
| `DATABASE_NAME` | `ai_recruitment`            | Database name             |
