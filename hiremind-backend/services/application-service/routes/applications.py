from fastapi import APIRouter, File, Form, UploadFile, status

from schemas.application import ApplicationCreateSchema
from services.application_service import apply_for_job, get_applications_for_job

router = APIRouter()


@router.post("/apply/{jobid}", status_code=status.HTTP_201_CREATED)
async def apply(
    jobid: str,
    candidate_name: str = Form(..., description="Full name of the candidate"),
    email: str = Form(..., description="Candidate email address"),
    phone: str = Form(..., description="Candidate phone number"),
    experience: str = Form(..., description="Candidate's work experience summary"),
    resume: UploadFile = File(..., description="Resume file — PDF, DOC, or DOCX"),
):
    """Submit a job application for a given jobid."""
    data = ApplicationCreateSchema(
        candidate_name=candidate_name,
        email=email,
        phone=phone,
        experience=experience,
    )
    return await apply_for_job(jobid, data, resume)


@router.get("/applications/{jobid}")
async def list_applications(jobid: str):
    """Retrieve all applications submitted for a specific job."""
    return await get_applications_for_job(jobid)
