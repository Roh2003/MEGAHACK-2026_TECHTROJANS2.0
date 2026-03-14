from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from models.job_post import JobPost
from schemas.job_post import (
    JobPostCreateSchema,
    JobPostCreateWithMatchesResponseSchema,
    RejectedCandidateMatchResponseSchema,
    JobPostUpdateSchema,
    JobPostResponseSchema,
)
from services.job_service import create_job, get_rejected_candidate_matches
from shared.dependencies import require_hr

router = APIRouter(prefix="/job-posts", tags=["Job Posts"])


# ── helpers ──────────────────────────────────────────────────────────────────

def _serialize(doc: JobPost) -> dict:
    return {
        "id": str(doc.id),
        "title": doc.title,
        "description": doc.description,
        "skills": doc.skills,
        "experience": doc.experience,
        "location": doc.location,
        "ctc": doc.ctc,
        "start_time": doc.start_time.isoformat(),
        "end_time": doc.end_time.isoformat(),
        "created_by": doc.created_by,
        "created_at": doc.created_at.isoformat(),
    }


async def _get_or_404(job_post_id: str) -> JobPost:
    try:
        obj_id = PydanticObjectId(job_post_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job post ID format",
        )
    doc = await JobPost.get(obj_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job post '{job_post_id}' not found",
        )
    return doc


# ── CREATE ────────────────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, response_model=JobPostCreateWithMatchesResponseSchema)
async def create_job_post(
    payload: JobPostCreateSchema,
    current_user: dict = Depends(require_hr),
):
    """Create a new job post and automatically rematch rejected candidates."""
    return await create_job(payload, current_user["sub"])


# ── READ ALL ──────────────────────────────────────────────────────────────────

@router.get("", response_model=list[JobPostResponseSchema])
async def get_all_job_posts():
    """Retrieve all job posts, sorted newest first."""
    docs = await JobPost.find_all().sort(-JobPost.created_at).to_list()
    return [_serialize(d) for d in docs]


# ── READ BY ID ────────────────────────────────────────────────────────────────

@router.get("/{job_post_id}", response_model=JobPostResponseSchema)
async def get_job_post(job_post_id: str):
    """Retrieve a single job post by its MongoDB _id."""
    doc = await _get_or_404(job_post_id)
    return _serialize(doc)


@router.get(
    "/{job_post_id}/rejected-candidate-matches",
    response_model=list[RejectedCandidateMatchResponseSchema],
)
async def get_job_post_rejected_candidate_matches(job_post_id: str):
    return await get_rejected_candidate_matches(job_post_id)


# ── UPDATE ────────────────────────────────────────────────────────────────────

@router.put("/{job_post_id}", response_model=JobPostResponseSchema)
async def update_job_post(job_post_id: str, payload: JobPostUpdateSchema):
    """Partially update a job post. Only the provided fields are changed."""
    doc = await _get_or_404(job_post_id)

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

@router.delete("/{job_post_id}", status_code=status.HTTP_200_OK)
async def delete_job_post(job_post_id: str):
    """Permanently delete a job post from MongoDB."""
    doc = await _get_or_404(job_post_id)
    await doc.delete()
    return {"message": "Job post deleted successfully", "id": job_post_id}
