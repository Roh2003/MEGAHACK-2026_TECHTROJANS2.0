from fastapi import APIRouter, File, Form, UploadFile, status

from schemas.application import ApplicationCreateSchema
from services.application_service import apply_for_job, get_applications_for_job

router = APIRouter()


@router.post("/apply/{job_id}", status_code=status.HTTP_201_CREATED)
async def apply(
    job_id: str,
    candidate_name: str = Form(..., description="Full name of the candidate"),
    email: str = Form(..., description="Candidate email address"),
    phone: str = Form(..., description="Candidate phone number"),
    experience: str = Form(..., description="Candidate's work experience summary"),
    resume: UploadFile = File(..., description="Resume file — PDF, DOC, or DOCX"),
):
    """Submit a job application for a given job_id."""
    data = ApplicationCreateSchema(
        candidate_name=candidate_name,
        email=email,
        phone=phone,
        experience=experience,
    )
    return await apply_for_job(job_id, data, resume)


@router.get("/applications/{job_id}")
async def list_applications(job_id: str):
    """Retrieve all applications submitted for a specific job."""
    return await get_applications_for_job(job_id)
