import os
from contextlib import asynccontextmanager

# Ensure upload directory exists before StaticFiles mounts it
os.makedirs(os.path.join("uploads", "resumes"), exist_ok=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import connect_db, close_db
from routes.applications import router as applications_router
from routes.job_application import router as job_application_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
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
