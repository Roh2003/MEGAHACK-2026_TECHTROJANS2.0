import os
import uuid
from datetime import datetime

from fastapi import HTTPException, UploadFile, status

from models.application import Application
from schemas.application import ApplicationCreateSchema

UPLOAD_DIR = os.path.join("uploads", "resumes")

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _serialize_application(app: Application) -> dict:
    return {
        "id": str(app.id),
        "job_id": app.job_id,
        "candidate_name": app.candidate_name,
        "email": app.email,
        "phone": app.phone,
        "experience": app.experience,
        "resume_path": app.resume_path,
        "status": app.status,
        "created_at": (
            app.created_at.isoformat()
            if isinstance(app.created_at, datetime)
            else str(app.created_at)
        ),
    }


async def apply_for_job(
    job_id: str, data: ApplicationCreateSchema, resume: UploadFile
) -> dict:
    if resume.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and Word documents (.pdf, .doc, .docx) are accepted",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_ext = os.path.splitext(resume.filename or "")[1].lower() or ".bin"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    contents = await resume.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    application = Application(
        job_id=job_id,
        candidate_name=data.candidate_name,
        email=data.email,
        phone=data.phone,
        experience=data.experience,
        resume_path=file_path,
        status="pending",
    )
    await application.insert()
    return _serialize_application(application)


async def get_applications_for_job(job_id: str) -> list:
    applications = (
        await Application.find(Application.job_id == job_id)
        .sort(-Application.created_at)
        .to_list()
    )
    return [_serialize_application(app) for app in applications]
