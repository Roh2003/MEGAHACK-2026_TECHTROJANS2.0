# AI Recruitment Platform Backend

Single-server FastAPI backend for the HireMind platform. The repository now runs from one root entrypoint, `main.py`, while the domain code stays organized under service-specific folders.

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open the API docs at `http://localhost:8000/docs`.

## Project Structure

```text
ai-recruitment-platform/
├── main.py
├── AI_Model/
│   ├── agent.py
│   ├── generatesQuestionFromai.py
│   ├── interview_summary_agent.py
│   ├── resume_parser.py
│   └── screening_pipeline.py
├── shared/
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── email.py
│   ├── jwt_handler.py
│   ├── middleware.py
│   ├── response.py
│   └── status_codes.py
├── services/
│   ├── auth-service/
│   │   ├── database.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── job-service/
│   │   ├── database.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── services/
│   ├── application-service/
│   │   ├── database.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── services/
│   └── distribution-service/
│       ├── adapters/
│       └── services/
├── uploads/
│   └── resumes/
├── requirements.txt
└── README.md
```

`main.py` now loads the service routers directly, so the per-service launcher files are no longer needed.

## API Surface

The monolith exposes the existing domain routes from one server:

- Auth: `/auth/*` and `/organizations/*`
- Jobs: `/jobs/{jobid}` and `/job-posts/{jobid}`
- Applications: `/apply/{jobid}` and `/job-applications/*`
- Distribution: `/distribute-job/{jobid}`
- AI: `/ai-screening/status`, `/ai-screening/run-now`, `/ai-interview/questions`
- Health: `/health`

## Environment

Typical variables used by the backend include:

- `MONGO_URI`
- `DATABASE_NAME`
- `BASE_JOB_URL`
- `OPENAI_API_KEY`
- `AI_CRON_INTERVAL_SECONDS`

Service-specific `.env` files are still supported for the domain modules, but the runtime entrypoint is now centralized in the root `main.py`.
