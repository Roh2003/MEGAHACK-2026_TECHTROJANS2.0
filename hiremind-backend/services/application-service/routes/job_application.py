from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from models.job_application import JobApplication
from schemas.job_application import (
    JobApplicationCreateSchema,
    JobApplicationUpdateSchema,
    JobApplicationResponseSchema,
)

router = APIRouter(prefix="/job-applications", tags=["Job Applications"])


# ── helpers ───────────────────────────────────────────────────────────────────

def _serialize(doc: JobApplication) -> dict:
    return {
        "id": str(doc.id),                           # j_d_id
        "job_id": doc.job_id,
        "applicant_name": doc.applicant_name,
        "address": doc.address,
        "highest_qualification": doc.highest_qualification,
        "experience": doc.experience,
        "resume_url": doc.resume_url,
        "submit_at": doc.submit_at.isoformat(),
        "status": doc.status,
    }


async def _get_or_404(application_id: str) -> JobApplication:
    try:
        obj_id = PydanticObjectId(application_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid application ID format",
        )
    doc = await JobApplication.get(obj_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application '{application_id}' not found",
        )
    return doc


# ── CREATE ────────────────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, response_model=JobApplicationResponseSchema)
async def create_job_application(payload: JobApplicationCreateSchema):
    """Submit a new job application and store it in MongoDB."""
    doc = JobApplication(
        job_id=payload.job_id,
        applicant_name=payload.applicant_name,
        address=payload.address,
        highest_qualification=payload.highest_qualification,
        experience=payload.experience,
        resume_url=payload.resume_url,
    )
    await doc.insert()
    return _serialize(doc)


# ── READ ALL ──────────────────────────────────────────────────────────────────

@router.get("", response_model=list[JobApplicationResponseSchema])
async def get_all_job_applications():
    """Retrieve all job applications, sorted newest first."""
    docs = await JobApplication.find_all().sort(-JobApplication.submit_at).to_list()
    return [_serialize(d) for d in docs]


# ── READ BY ID ────────────────────────────────────────────────────────────────

@router.get("/{application_id}", response_model=JobApplicationResponseSchema)
async def get_job_application(application_id: str):
    """Retrieve a single job application by its MongoDB _id (j_d_id)."""
    doc = await _get_or_404(application_id)
    return _serialize(doc)


# ── READ BY JOB ID ────────────────────────────────────────────────────────────

@router.get("/by-job/{job_id}", response_model=list[JobApplicationResponseSchema])
async def get_applications_by_job(job_id: str):
    """Retrieve all applications submitted for a specific job post."""
    docs = (
        await JobApplication.find(JobApplication.job_id == job_id)
        .sort(-JobApplication.submit_at)
        .to_list()
    )
    return [_serialize(d) for d in docs]


# ── UPDATE ────────────────────────────────────────────────────────────────────

@router.put("/{application_id}", response_model=JobApplicationResponseSchema)
async def update_job_application(application_id: str, payload: JobApplicationUpdateSchema):
    """Partially update a job application. Useful for changing status or correcting details."""
    doc = await _get_or_404(application_id)

    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields provided",
        )

    for field, value in update_data.items():
        setattr(doc, field, value)

    await doc.save()
    return _serialize(doc)


# ── DELETE ────────────────────────────────────────────────────────────────────

@router.delete("/{application_id}", status_code=status.HTTP_200_OK)
async def delete_job_application(application_id: str):
    """Permanently delete a job application from MongoDB."""
    doc = await _get_or_404(application_id)
    await doc.delete()
    return {"message": "Job application deleted successfully", "id": application_id}
