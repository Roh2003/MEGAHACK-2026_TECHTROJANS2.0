from beanie import PydanticObjectId
from datetime import datetime, timedelta
import os
from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query, status

from models.assessment_question_response import AssessmentQuestionResponse
from models.assessment_questions import AssessmentQuestions
from models.job_application import JobApplication
from models.round import Round
from models.schedule_assessment import ScheduleAssessment
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
from schemas.schedule_assessment import (
    AssessmentInviteRequestSchema,
    AssessmentInviteResponseSchema,
)
from schemas.round import RoundCreateSchema, RoundResponseSchema
from schemas.round_result import (
    RoundCandidateDecisionSchema,
    RoundResultCreateSchema,
    RoundResultResponseSchema,
    RoundWiseCandidateSchema,
)
from shared.email import send_assessment_invitation_email
from database import get_db
from tasks.ai_tasks import ai_screen_resume

router = APIRouter(prefix="/job-applications", tags=["Job Applications"])


# ── helpers ───────────────────────────────────────────────────────────────────

def _serialize(doc: JobApplication) -> dict:
    return {
        "id": str(doc.id),                           # j_d_id
        "job_id": doc.job_id,
        "candidate_id": doc.candidate_id,
        "email": doc.email,
        "applicant_name": doc.applicant_name,
        "address": doc.address,
        "highest_qualification": doc.highest_qualification,
        "experience": doc.experience,
        "resume_url": doc.resume_url,
        "ai_score": doc.ai_score,
        "strengths": doc.strengths,
        "weaknesses": doc.weaknesses,
        "pipeline_snapshot": [
            {
                "round_id": item.round_id,
                "name": item.name,
                "order": item.order,
            }
            for item in (doc.pipeline_snapshot or [])
        ],
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


async def _get_user_doc(candidate_id: str) -> dict | None:
    db = get_db()
    users = db["users"]
    return await users.find_one({"$expr": {"$eq": [{"$toString": "$_id"}, candidate_id]}})


async def _get_job_title(job_id: str) -> str:
    db = get_db()

    job_doc = await db["job_posts"].find_one({"jobid": job_id})
    if not job_doc:
        legacy_query = {"$expr": {"$eq": [{"$toString": "$_id"}, job_id]}}
        job_doc = await db["job_posts"].find_one(legacy_query)
    if job_doc and job_doc.get("title"):
        return str(job_doc["title"])

    fallback_job_doc = await db["jobs"].find_one({"jobid": job_id})
    if not fallback_job_doc:
        legacy_query = {"$expr": {"$eq": [{"$toString": "$_id"}, job_id]}}
        fallback_job_doc = await db["jobs"].find_one(legacy_query)
    if fallback_job_doc and fallback_job_doc.get("title"):
        return str(fallback_job_doc["title"])

    return "the applied role"


def _build_assessment_link(assessment_id: str, job_id: str, round_id: str) -> str:
    base_url = os.getenv(
        "ASSESSMENT_TEST_BASE_URL",
        "https://4j2q47l4-8080.inc1.devtunnels.ms/assessment",
    )
    return (
        f"{base_url}/{assessment_id}/test"
        f"?candidate_id={{candidate_id}}&jobId={job_id}&round_id={round_id}"
    )


def _build_candidate_assessment_link(
    assessment_id: str,
    candidate_id: str,
    job_id: str,
    round_id: str,
) -> str:
    return _build_assessment_link(assessment_id, job_id, round_id).replace(
        "{candidate_id}", candidate_id
    )


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


async def _get_round_or_404(round_id: str) -> Round:
    try:
        round_obj_id = PydanticObjectId(round_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid round_id format",
        )

    round_doc = await Round.get(round_obj_id)
    if not round_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Round '{round_id}' not found",
        )

    return round_doc


async def _upsert_round_result_and_progress(
    *,
    job_id: str,
    application_id: str,
    candidate_id: str,
    round_id: str,
    status_value: RoundResultStatus,
    score: float | None = None,
    feedback: str | None = None,
    evaluated_by: str | None = None,
) -> RoundResult:
    application = await _get_or_404(application_id)
    if application.job_id != job_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="application_id does not belong to provided job_id",
        )
    if application.candidate_id != candidate_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="candidate_id does not belong to provided application_id",
        )

    round_doc = await _get_round_or_404(round_id)
    if round_doc.job_id != job_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="round_id does not belong to provided job_id",
        )

    if score is not None and round_doc.max_score is not None and score > round_doc.max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"score cannot exceed max_score ({round_doc.max_score})",
        )

    existing = await RoundResult.find_one(
        RoundResult.application_id == application_id,
        RoundResult.round_id == round_id,
    )

    if existing:
        existing.job_id = job_id
        existing.candidate_id = candidate_id
        existing.score = score
        existing.status = status_value
        existing.feedback = feedback
        existing.evaluated_by = evaluated_by
        existing.evaluated_at = datetime.utcnow()
        await existing.save()
        result_doc = existing
    else:
        result_doc = RoundResult(
            job_id=job_id,
            application_id=application_id,
            candidate_id=candidate_id,
            round_id=round_id,
            score=score,
            status=status_value,
            feedback=feedback,
            evaluated_by=evaluated_by,
        )
        await result_doc.insert()

    if not application.pipeline_snapshot:
        application.pipeline_snapshot = await _build_pipeline_snapshot(job_id)

    if status_value in {RoundResultStatus.failed, RoundResultStatus.rejected}:
        application.status = ApplicationStatus.rejected
        application.current_round = round_doc.round_order
    elif status_value == RoundResultStatus.passed:
        next_round = (
            await Round.find(
                Round.job_id == job_id,
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
    return result_doc


async def _build_pipeline_snapshot(job_id: str) -> list[dict]:
    rounds = await Round.find(Round.job_id == job_id).sort(Round.round_order).to_list()
    return [
        {
            "round_id": str(doc.id),
            "name": doc.round_name,
            "order": doc.round_order,
        }
        for doc in rounds
    ]


async def _round_wise_candidates(
    job_id: str,
    round_id: str,
    statuses: set[RoundResultStatus],
) -> list[dict]:
    if not statuses:
        return []

    status_filters = [RoundResult.status == s for s in statuses]
    status_clause = status_filters[0]
    for expression in status_filters[1:]:
        status_clause = status_clause | expression

    docs = (
        await RoundResult.find(
            RoundResult.job_id == job_id,
            RoundResult.round_id == round_id,
            status_clause,
        )
        .sort(RoundResult.evaluated_at)
        .to_list()
    )

    output: list[dict] = []
    for doc in docs:
        app = await _get_or_404(doc.application_id)
        output.append(
            {
                "round_result_id": str(doc.id),
                "job_id": doc.job_id,
                "round_id": doc.round_id,
                "application_id": doc.application_id,
                "candidate_id": doc.candidate_id,
                "candidate_name": app.applicant_name,
                "score": doc.score,
                "status": doc.status,
                "feedback": doc.feedback,
                "evaluated_by": doc.evaluated_by,
                "evaluated_at": doc.evaluated_at.isoformat(),
            }
        )
    return output


# ── CREATE ────────────────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, response_model=JobApplicationResponseSchema)
async def create_job_application(payload: JobApplicationCreateSchema):
    """Submit a new job application and store it in MongoDB."""
    pipeline_snapshot = await _build_pipeline_snapshot(payload.job_id)

    doc = JobApplication(
        job_id=payload.job_id,
        candidate_id=payload.candidate_id,
        email=payload.email,
        applicant_name=payload.applicant_name,
        address=payload.address,
        highest_qualification=payload.highest_qualification,
        experience=payload.experience,
        resume_url=payload.resume_url,
        ai_score=payload.ai_score,
        strengths=payload.strengths or [],
        weaknesses=payload.weaknesses or [],
        pipeline_snapshot=pipeline_snapshot,
        current_round=None,
        status=payload.status,
    )
    await doc.insert()
    ai_screen_resume.delay(str(doc.id))
    return _serialize(doc)


# ── READ ALL ──────────────────────────────────────────────────────────────────

@router.get("", response_model=list[JobApplicationResponseSchema])
async def get_all_job_applications():
    """Retrieve all job applications, sorted newest first."""
    docs = await JobApplication.find_all().sort(-JobApplication.submit_at).to_list()
    return [_serialize(d) for d in docs]


# ── READ BY ID ────────────────────────────────────────────────────────────────

@router.get("/{application_id}", response_model=JobApplicationResponseSchema)
async def get_job_application(
    application_id: str = Path(..., pattern=r"^[a-fA-F0-9]{24}$")
):
    """Retrieve a single job application by its MongoDB _id (j_d_id)."""
    doc = await _get_or_404(application_id)
    return _serialize(doc)


# ── READ BY JOB ID ────────────────────────────────────────────────────────────

@router.get("/by-job/{jobid}", response_model=list[JobApplicationResponseSchema])
async def get_applications_by_job(jobid: str):
    """Retrieve all applications for a job, sorted by AI score descending."""
    docs = (
        await JobApplication.find(JobApplication.job_id == jobid)
        .sort(-JobApplication.ai_score, -JobApplication.submit_at)
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


@router.get("/rounds/by-job/{jobid}", response_model=list[RoundResponseSchema])
async def get_rounds_by_job(jobid: str):
    """List configured rounds for a job in pipeline order."""
    docs = await Round.find(Round.job_id == jobid).sort(Round.round_order).to_list()
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
        existing.updated_at = datetime.utcnow()
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
    "/assessment-questions/by-job/{jobid}/round/{round_id}",
    response_model=AssessmentQuestionsResponseSchema,
)
async def get_assessment_questions(jobid: str, round_id: str):
    doc = await AssessmentQuestions.find_one(
        AssessmentQuestions.job_id == jobid,
        AssessmentQuestions.round_id == round_id,
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment questions not found for provided jobid and round_id",
        )

    return _serialize_assessment_questions(doc)


@router.post(
    "/assessment/attach",
    status_code=status.HTTP_201_CREATED,
    response_model=AssessmentInviteResponseSchema,
)
async def attach_assessment_to_candidates(payload: AssessmentInviteRequestSchema):
    round_doc = await _get_round_or_404(payload.round_id)
    if round_doc.job_id != payload.job_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="round_id does not belong to provided job_id",
        )

    assessment_doc = await AssessmentQuestions.find_one(
        AssessmentQuestions.job_id == payload.job_id,
        AssessmentQuestions.round_id == payload.round_id,
    )
    if not assessment_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment questions not found for provided jobid and round_id",
        )

    job_title = await _get_job_title(payload.job_id)
    assessment_description = f"Assessment round for {job_title}"

    eligible_applications = await JobApplication.find(
        JobApplication.job_id == payload.job_id,
        JobApplication.current_round == round_doc.round_order,
    ).to_list()

    if not eligible_applications:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No candidates found for the requested assessment round",
        )

    candidate_ids: list[str] = []
    seen_candidate_ids: set[str] = set()
    candidate_targets: list[dict[str, str]] = []
    for application in eligible_applications:
        if not application.candidate_id:
            continue

        if application.candidate_id in seen_candidate_ids:
            continue

        email = application.email
        user_doc = None
        if not email:
            user_doc = await _get_user_doc(application.candidate_id)
            email = (user_doc or {}).get("email")
        if not email:
            continue

        seen_candidate_ids.add(application.candidate_id)
        candidate_ids.append(application.candidate_id)
        candidate_targets.append(
            {
                "candidate_id": application.candidate_id,
                "candidate_name": (user_doc or {}).get("name") or application.applicant_name,
                "email": str(email),
            }
        )

    if not candidate_targets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No candidate emails found for the requested assessment round",
        )

    start_time = round_doc.start_time or datetime.utcnow()
    end_time = round_doc.end_time or (start_time + timedelta(hours=1))

    assessment_link_template = _build_assessment_link(
        assessment_id=str(assessment_doc.id),
        job_id=payload.job_id,
        round_id=payload.round_id,
    )

    schedule_doc = await ScheduleAssessment.find_one(
        ScheduleAssessment.job_id == payload.job_id,
        ScheduleAssessment.round_id == payload.round_id,
    )

    if schedule_doc:
        schedule_doc.assessment_id = str(assessment_doc.id)
        schedule_doc.assign_candidate_ids = candidate_ids
        schedule_doc.assessment_description = assessment_description
        schedule_doc.assessment_link = assessment_link_template
        schedule_doc.start_time = start_time
        schedule_doc.end_time = end_time
        await schedule_doc.save()
    else:
        schedule_doc = ScheduleAssessment(
            assessment_id=str(assessment_doc.id),
            job_id=payload.job_id,
            round_id=payload.round_id,
            assign_candidate_ids=candidate_ids,
            assessment_description=assessment_description,
            assessment_link=assessment_link_template,
            start_time=start_time,
            end_time=end_time,
        )
        await schedule_doc.insert()

    emailed_count = 0
    skipped_count = 0
    for candidate in candidate_targets:
        candidate_link = _build_candidate_assessment_link(
            assessment_id=str(assessment_doc.id),
            candidate_id=candidate["candidate_id"],
            job_id=payload.job_id,
            round_id=payload.round_id,
        )
        try:
            await send_assessment_invitation_email(
                to=candidate["email"],
                candidate_name=candidate["candidate_name"],
                job_title=job_title,
                assessment_link=candidate_link,
                assessment_description=assessment_description,
            )
            emailed_count += 1
        except Exception:
            skipped_count += 1

    return {
        "assessment_id": str(assessment_doc.id),
        "job_id": payload.job_id,
        "round_id": payload.round_id,
        "round_name": round_doc.round_name,
        "assessment_link": assessment_link_template,
        "assignment_count": len(candidate_ids),
        "emailed_count": emailed_count,
        "skipped_count": skipped_count,
        "candidate_ids": candidate_ids,
    }


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
        existing.updated_at = datetime.utcnow()
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
    "/assessment-question-responses/by-job/{jobid}/round/{round_id}/candidate/{candidate_id}",
    response_model=AssessmentQuestionResponseSchema,
)
async def get_assessment_question_response(jobid: str, round_id: str, candidate_id: str):
    doc = await AssessmentQuestionResponse.find_one(
        AssessmentQuestionResponse.job_id == jobid,
        AssessmentQuestionResponse.round_id == round_id,
        AssessmentQuestionResponse.candidate_id == candidate_id,
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment response not found for provided jobid, round_id and candidate_id",
        )

    return _serialize_assessment_question_response(doc)


@router.post(
    "/round-results",
    status_code=status.HTTP_201_CREATED,
    response_model=RoundResultResponseSchema,
)
async def create_round_result(payload: RoundResultCreateSchema):
    """Store candidate evaluation for a round and progress application status."""
    doc = await _upsert_round_result_and_progress(
        job_id=payload.job_id,
        application_id=payload.application_id,
        candidate_id=payload.candidate_id,
        round_id=payload.round_id,
        status_value=payload.status,
        score=payload.score,
        feedback=payload.feedback,
        evaluated_by=payload.evaluated_by,
    )
    return _serialize_round_result(doc)


@router.post(
    "/round-results/decision",
    status_code=status.HTTP_200_OK,
    response_model=RoundResultResponseSchema,
)
async def decide_candidate_for_round(
    payload: RoundCandidateDecisionSchema,
    action: Literal["select", "reject"] = Query(..., description="Select or reject the candidate"),
):
    status_value = (
        RoundResultStatus.passed if action == "select" else RoundResultStatus.rejected
    )
    doc = await _upsert_round_result_and_progress(
        job_id=payload.job_id,
        application_id=payload.application_id,
        candidate_id=payload.candidate_id,
        round_id=payload.round_id,
        status_value=status_value,
        score=payload.score,
        feedback=payload.feedback,
        evaluated_by=payload.evaluated_by,
    )
    return _serialize_round_result(doc)


@router.get(
    "/round-results/candidates/by-job/{jobid}/round/{round_id}",
    response_model=list[RoundWiseCandidateSchema],
)
async def round_wise_candidates_by_status(
    jobid: str,
    round_id: str,
    status_filter: Literal["selected", "rejected"] = Query(
        ...,
        alias="status",
        description="Filter candidates by selected or rejected status",
    ),
):
    if status_filter == "selected":
        return await _round_wise_candidates(
            job_id=jobid,
            round_id=round_id,
            statuses={RoundResultStatus.passed},
        )

    return await _round_wise_candidates(
        job_id=jobid,
        round_id=round_id,
        statuses={RoundResultStatus.rejected, RoundResultStatus.failed},
    )


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
async def update_job_application(
    application_id: str = Path(..., pattern=r"^[a-fA-F0-9]{24}$"),
    payload: JobApplicationUpdateSchema = ...,
):
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
async def delete_job_application(
    application_id: str = Path(..., pattern=r"^[a-fA-F0-9]{24}$")
):
    """Permanently delete a job application from MongoDB."""
    doc = await _get_or_404(application_id)
    await doc.delete()
    return {"message": "Job application deleted successfully", "id": application_id}
