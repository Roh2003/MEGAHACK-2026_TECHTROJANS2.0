from __future__ import annotations

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from dotenv import load_dotenv

from ai_resume_model.utils.ai_email_generator import OpenRouterEmailAgent

load_dotenv()

SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM: str = os.getenv("SMTP_FROM", SMTP_USER)


def _normalize_status(status: str) -> str:
    normalized = status.strip().lower().replace("-", "_").replace(" ", "_")

    accepted_aliases = {"accepted", "selected", "shortlisted", "approved"}
    rejected_aliases = {"rejected", "not_selected", "declined", "denied"}

    if normalized in accepted_aliases:
        return "accepted"
    if normalized in rejected_aliases:
        return "rejected"

    raise ValueError(
        "Invalid status. Use accepted/selected/shortlisted or rejected/not_selected."
    )


def _fallback_email(
    candidate_name: str,
    job_title: str,
    status: str,
    matching_skills: list[str],
    weaknesses: list[str],
) -> dict[str, str]:
    if status == "accepted":
        skills_line = ", ".join(matching_skills[:4]) if matching_skills else "your profile"
        return {
            "subject": f"Congratulations! Selected for {job_title}",
            "body": (
                f"<p>Hi {candidate_name},</p>"
                f"<p>Congratulations! You have been selected for the <b>{job_title}</b> role.</p>"
                f"<p>We were impressed by {skills_line}. Our team will contact you shortly with next steps.</p>"
                "<p>Best regards,<br/>AI Recruitment Team</p>"
            ),
        }

    weakness_line = ", ".join(weaknesses[:4]) if weaknesses else "a few role-specific areas"
    return {
        "subject": f"Update on your {job_title} application",
        "body": (
            f"<p>Hi {candidate_name},</p>"
            f"<p>Thank you for applying for the <b>{job_title}</b> role.</p>"
            f"<p>After review, we are moving forward with other candidates at this time. "
            f"You may improve in areas such as {weakness_line}.</p>"
            "<p>We appreciate your interest and encourage you to apply again in the future.</p>"
            "<p>Best regards,<br/>AI Recruitment Team</p>"
        ),
    }


def _fallback_assessment_email(
    candidate_name: str,
    job_title: str,
    assessment_link: str,
    assessment_description: str | None,
) -> dict[str, str]:
    description = assessment_description.strip() if assessment_description else "assessment round"
    return {
        "subject": f"You have been selected for the next round: {job_title}",
        "body": (
            f"<p>Hi {candidate_name},</p>"
            f"<p>Congratulations! You have moved to the next round for the <b>{job_title}</b> role.</p>"
            f"<p>This is an <b>{description}</b>. Please complete it using the link below:</p>"
            f"<p><a href=\"{assessment_link}\">Start Assessment</a></p>"
            "<p>If the link does not work, copy and paste it into your browser.</p>"
            "<p>Best regards,<br/>AI Recruitment Team</p>"
        ),
    }


async def send_email(
    to: str | list[str],
    subject: str,
    body: str,
    html: bool = False,
) -> None:
    recipients = [to] if isinstance(to, str) else to

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = ", ".join(recipients)

    mime_type = "html" if html else "plain"
    message.attach(MIMEText(body, mime_type, "utf-8"))

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True,
    )


async def send_ai_application_result(
    to: str,
    candidate_name: str,
    job_title: str,
    status: str,
    matching_skills: list[str] | None = None,
    weaknesses: list[str] | None = None,
):
    """Draft and send a selection/rejection email using OpenRouter with safe fallback."""

    normalized_status = _normalize_status(status)
    matching_skills = matching_skills or []
    weaknesses = weaknesses or []

    try:
        agent = OpenRouterEmailAgent()
        result = agent.generate_email(
            candidate_name=candidate_name,
            job_title=job_title,
            status=normalized_status,
            matching_skills=matching_skills,
            weaknesses=weaknesses,
        )

        subject = str((result or {}).get("subject", "")).strip()
        body = str((result or {}).get("body", "")).strip()

        if not subject or not body:
            raise ValueError("OpenRouter returned invalid output")

    except Exception:
        fallback = _fallback_email(
            candidate_name=candidate_name,
            job_title=job_title,
            status=normalized_status,
            matching_skills=matching_skills,
            weaknesses=weaknesses,
        )
        subject = fallback["subject"]
        body = fallback["body"]

    await send_email(
        to=to,
        subject=subject,
        body=body,
        html=True,
    )


async def send_assessment_invitation_email(
    to: str,
    candidate_name: str,
    job_title: str,
    assessment_link: str,
    assessment_description: str | None = None,
) -> None:
    """Draft and send an assessment invitation email using OpenRouter with safe fallback."""

    try:
        agent = OpenRouterEmailAgent()
        result = agent.generate_assessment_email(
            candidate_name=candidate_name,
            job_title=job_title,
            assessment_link=assessment_link,
            assessment_description=assessment_description,
        )

        subject = str((result or {}).get("subject", "")).strip()
        body = str((result or {}).get("body", "")).strip()

        if not subject or not body:
            raise ValueError("OpenRouter returned invalid output")

    except Exception:
        fallback = _fallback_assessment_email(
            candidate_name=candidate_name,
            job_title=job_title,
            assessment_link=assessment_link,
            assessment_description=assessment_description,
        )
        subject = fallback["subject"]
        body = fallback["body"]

    await send_email(
        to=to,
        subject=subject,
        body=body,
        html=True,
    )