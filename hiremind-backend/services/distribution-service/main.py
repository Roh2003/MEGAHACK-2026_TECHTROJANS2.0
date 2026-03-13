from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.distribution_service import distribute_job

app = FastAPI(
    title="Distribution Service",
    description="Social media job distribution microservice — AI Recruitment Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/distribute-job/{job_id}", tags=["Distribution"])
async def distribute_job_to_platforms(job_id: str):
    """
    Generate share links for a job on LinkedIn, Twitter/X, and WhatsApp.
    No authentication required — links are public by design.
    """
    return await distribute_job(job_id)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "distribution-service", "version": "1.0.0"}
