import os
import asyncio
from contextlib import asynccontextmanager

# Ensure upload directory exists before StaticFiles mounts it
os.makedirs(os.path.join("uploads", "resumes"), exist_ok=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import connect_db, close_db
from routes.applications import router as applications_router
from routes.job_application import router as job_application_router
from services.round_email_scheduler import round_email_cron_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()

    interval_seconds = int(os.getenv("ROUND_EMAIL_CRON_INTERVAL_SECONDS", "3600"))
    app.state.round_email_cron_task = asyncio.create_task(
        round_email_cron_loop(interval_seconds)
    )
    print(
        f"[application-service] round email cron started (interval={interval_seconds}s)"
    )

    yield

    cron_task = getattr(app.state, "round_email_cron_task", None)
    if cron_task is not None:
        cron_task.cancel()
        try:
            await cron_task
        except asyncio.CancelledError:
            pass

    await close_db()


app = FastAPI(
    title="Application Service",
    description="Candidate application and resume upload microservice — AI Recruitment Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded résumés as static files at /uploads/resumes/<filename>
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(applications_router, tags=["Applications"])
app.include_router(job_application_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "application-service", "version": "1.0.0"}
