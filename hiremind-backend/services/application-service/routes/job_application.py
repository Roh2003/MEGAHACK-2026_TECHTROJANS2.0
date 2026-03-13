from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from models.assessment_question_response import AssessmentQuestionResponse
from models.assessment_questions import AssessmentQuestions
from models.job_application import JobApplication
from models.round import Round
from models.round_result import RoundResult, RoundResultStatus
from schemas.job_application import (
    ApplicationStatus,
    JobApplicationCreateSchema,
    JobApplicationUpdateSchema,
    JobApplicationResponseSchema,
)
from schemas.assessment_question_response import (
    AssessmentQuestionResponseCreateSchema,
    AssessmentQuestionResponseSchema,
)
from schemas.assessment_questions import (
    AssessmentQuestionsCreateSchema,
    AssessmentQuestionsResponseSchema,
)
from schemas.round import RoundCreateSchema, RoundResponseSchema
from schemas.round_result import RoundResultCreateSchema, RoundResultResponseSchema

router = APIRouter(prefix="/job-applications", tags=["Job Applications"])


# ── helpers ───────────────────────────────────────────────────────────────────

def _serialize(doc: JobApplication) -> dict:
    return {
        "id": str(doc.id),                           # j_d_id
        "job_id": doc.job_id,
        "candidate_id": doc.candidate_id,
        "applicant_name": doc.applicant_name,
        "address": doc.address,
        "highest_qualification": doc.highest_qualification,
        "experience": doc.experience,
        "resume_url": doc.resume_url,
        "ai_score": doc.ai_score,
        "strengths": doc.strengths,
        "weaknesses": doc.weaknesses,
        "current_round": doc.current_round,
        "submit_at": doc.submit_at.isoformat(),
        "status": doc.status,
    }


def _serialize_round(doc: Round) -> dict:
    return {
        "id": str(doc.id),
        "job_id": doc.job_id,
        "round_name": doc.round_name,
        "round_order": doc.round_order,
        "type": doc.type,
        "max_score": doc.max_score,
        "created_at": doc.created_at.isoformat(),
    }


def _serialize_round_result(doc: RoundResult) -> dict:
    return {
        "id": str(doc.id),
        "job_id": doc.job_id,
        "application_id": doc.application_id,
        "candidate_id": doc.candidate_id,
        "round_id": doc.round_id,
        "score": doc.score,
        "status": doc.status,
        "feedback": doc.feedback,
        "evaluated_by": doc.evaluated_by,
        "evaluated_at": doc.evaluated_at.isoformat(),
    }


def _serialize_assessment_questions(doc: AssessmentQuestions) -> dict:
    return {
        "id": str(doc.id),
        "job_id": doc.job_id,
        "round_id": doc.round_id,
        "questionans": [
            {
                "question": item.question,
                "ans": item.ans,
                "correctans": item.correctans,
                "marks": item.marks,
            }
            for item in doc.questionans
        ],
        "created_at": doc.created_at.isoformat(),
        "updated_at": doc.updated_at.isoformat(),
    }


def _serialize_assessment_question_response(doc: AssessmentQuestionResponse) -> dict:
    return {
        "id": str(doc.id),
        "job_id": doc.job_id,
        "round_id": doc.round_id,
        "candidate_id": doc.candidate_id,
        "totalmarks": doc.totalmarks,
        "questionanswer": [
            {
                "question": item.question,
                "answer": item.answer,
                "marks_obtained": item.marks_obtained,
                "is_correct": item.is_correct,
            }
            for item in doc.questionanswer
        ],
        "submitted_at": doc.submitted_at.isoformat(),
        "updated_at": doc.updated_at.isoformat(),
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
        candidate_id=payload.candidate_id,
        applicant_name=payload.applicant_name,
        address=payload.address,
        highest_qualification=payload.highest_qualification,
        experience=payload.experience,
        resume_url=payload.resume_url,
        ai_score=payload.ai_score,
        strengths=payload.strengths or [],
        weaknesses=payload.weaknesses or [],
        current_round=payload.current_round,
        status=payload.status,
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


@router.post("/rounds", status_code=status.HTTP_201_CREATED, response_model=RoundResponseSchema)
async def create_round(payload: RoundCreateSchema):
    """Create a round definition for a specific job pipeline."""
    existing = await Round.find_one(
        Round.job_id == payload.job_id,
        Round.round_order == payload.round_order,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Round order '{payload.round_order}' already exists for job '{payload.job_id}'"
            ),
        )

    doc = Round(
        job_id=payload.job_id,
        round_name=payload.round_name,
        round_order=payload.round_order,
        type=payload.type,
        max_score=payload.max_score,
    )
    await doc.insert()
    return _serialize_round(doc)


@router.get("/rounds/by-job/{job_id}", response_model=list[RoundResponseSchema])
async def get_rounds_by_job(job_id: str):
    """List configured rounds for a job in pipeline order."""
    docs = await Round.find(Round.job_id == job_id).sort(Round.round_order).to_list()
    return [_serialize_round(d) for d in docs]


@router.post(
    "/assessment-questions",
    status_code=status.HTTP_201_CREATED,
    response_model=AssessmentQuestionsResponseSchema,
)
async def create_or_update_assessment_questions(payload: AssessmentQuestionsCreateSchema):
    existing = await AssessmentQuestions.find_one(
        AssessmentQuestions.job_id == payload.job_id,
        AssessmentQuestions.round_id == payload.round_id,
    )

    if existing:
        existing.questionans = [item.model_dump() for item in payload.questionans]
        existing.updated_at = existing.created_at.utcnow()
        await existing.save()
        return _serialize_assessment_questions(existing)

    doc = AssessmentQuestions(
        job_id=payload.job_id,
        round_id=payload.round_id,
        questionans=[item.model_dump() for item in payload.questionans],
    )
    await doc.insert()
    return _serialize_assessment_questions(doc)


@router.get(
    "/assessment-questions/by-job/{job_id}/round/{round_id}",
    response_model=AssessmentQuestionsResponseSchema,
)
async def get_assessment_questions(job_id: str, round_id: str):
    doc = await AssessmentQuestions.find_one(
        AssessmentQuestions.job_id == job_id,
        AssessmentQuestions.round_id == round_id,
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment questions not found for provided job_id and round_id",
        )

    return _serialize_assessment_questions(doc)


@router.post(
    "/assessment-question-responses",
    status_code=status.HTTP_201_CREATED,
    response_model=AssessmentQuestionResponseSchema,
)
async def create_or_update_assessment_question_response(
    payload: AssessmentQuestionResponseCreateSchema,
):
    existing = await AssessmentQuestionResponse.find_one(
        AssessmentQuestionResponse.job_id == payload.job_id,
        AssessmentQuestionResponse.round_id == payload.round_id,
        AssessmentQuestionResponse.candidate_id == payload.candidate_id,
    )

    if existing:
        existing.totalmarks = payload.totalmarks
        existing.questionanswer = [item.model_dump() for item in payload.questionanswer]
        existing.updated_at = existing.submitted_at.utcnow()
        await existing.save()
        return _serialize_assessment_question_response(existing)

    doc = AssessmentQuestionResponse(
        job_id=payload.job_id,
        round_id=payload.round_id,
        candidate_id=payload.candidate_id,
        totalmarks=payload.totalmarks,
        questionanswer=[item.model_dump() for item in payload.questionanswer],
    )
    await doc.insert()
    return _serialize_assessment_question_response(doc)


@router.get(
    "/assessment-question-responses/by-job/{job_id}/round/{round_id}/candidate/{candidate_id}",
    response_model=AssessmentQuestionResponseSchema,
)
async def get_assessment_question_response(job_id: str, round_id: str, candidate_id: str):
    doc = await AssessmentQuestionResponse.find_one(
        AssessmentQuestionResponse.job_id == job_id,
        AssessmentQuestionResponse.round_id == round_id,
        AssessmentQuestionResponse.candidate_id == candidate_id,
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment response not found for provided job_id, round_id and candidate_id",
        )

    return _serialize_assessment_question_response(doc)


@router.post(
    "/round-results",
    status_code=status.HTTP_201_CREATED,
    response_model=RoundResultResponseSchema,
)
async def create_round_result(payload: RoundResultCreateSchema):
    """Store candidate evaluation for a round and progress application status."""
    application = await _get_or_404(payload.application_id)
    if application.job_id != payload.job_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="application_id does not belong to provided job_id",
        )

    try:
        round_obj_id = PydanticObjectId(payload.round_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid round_id format",
        )

    round_doc = await Round.get(round_obj_id)
    if not round_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Round '{payload.round_id}' not found",
        )
    if round_doc.job_id != payload.job_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="round_id does not belong to provided job_id",
        )

    if payload.score is not None and round_doc.max_score is not None and payload.score > round_doc.max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"score cannot exceed max_score ({round_doc.max_score})",
        )

    doc = RoundResult(
        job_id=payload.job_id,
        application_id=payload.application_id,
        candidate_id=payload.candidate_id,
        round_id=payload.round_id,
        score=payload.score,
        status=payload.status,
        feedback=payload.feedback,
        evaluated_by=payload.evaluated_by,
    )
    await doc.insert()

    if payload.status in {RoundResultStatus.failed, RoundResultStatus.rejected}:
        application.status = ApplicationStatus.rejected
        application.current_round = round_doc.round_order
    elif payload.status == RoundResultStatus.passed:
        next_round = (
            await Round.find(
                Round.job_id == payload.job_id,
                Round.round_order > round_doc.round_order,
            )
            .sort(Round.round_order)
            .first_or_none()
        )
        if next_round:
            application.status = ApplicationStatus.in_round
            application.current_round = next_round.round_order
        else:
            application.status = ApplicationStatus.selected
            application.current_round = round_doc.round_order
    else:
        application.status = ApplicationStatus.in_round
        application.current_round = round_doc.round_order

    await application.save()
    return _serialize_round_result(doc)


@router.get(
    "/{application_id}/round-history",
    response_model=list[RoundResultResponseSchema],
)
async def get_round_history(application_id: str):
    """Get complete round history for an application."""
    await _get_or_404(application_id)
    docs = (
        await RoundResult.find(RoundResult.application_id == application_id)
        .sort(RoundResult.evaluated_at)
        .to_list()
    )
    return [_serialize_round_result(d) for d in docs]


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
