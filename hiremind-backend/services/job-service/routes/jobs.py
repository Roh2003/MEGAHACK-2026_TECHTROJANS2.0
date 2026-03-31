from fastapi import APIRouter, Depends, status

from schemas.job_post import JobPostCreateSchema, JobPostCreateWithMatchesResponseSchema, RejectedCandidateMatchResponseSchema
from services.job_service import (
    create_job,
    delete_job,
    get_all_jobs,
    get_job_by_id,
    get_rejected_candidate_matches,
)
from shared.dependencies import get_current_user, require_hr

router = APIRouter()


@router.post("/jobs", status_code=status.HTTP_201_CREATED, response_model=JobPostCreateWithMatchesResponseSchema)
async def create_new_job(
    data: JobPostCreateSchema,
    current_user: dict = Depends(require_hr),
):
    return await create_job(data, current_user["sub"])


@router.get("/jobs")
async def list_all_jobs():
    return await get_all_jobs()


@router.get("/jobs/{jobid}")
async def get_single_job(jobid: str):
    return await get_job_by_id(jobid)


@router.get("/jobs/{jobid}/rejected-candidate-matches", response_model=list[RejectedCandidateMatchResponseSchema])
async def get_job_rejected_candidate_matches(jobid: str):
    return await get_rejected_candidate_matches(jobid)


@router.delete("/jobs/{jobid}", status_code=status.HTTP_200_OK)
async def remove_job(
    jobid: str,
    current_user: dict = Depends(require_hr),
):
    return await delete_job(jobid, current_user["sub"])
